#!/usr/bin/env python3
"""Parse PDF / images / DOCX into structured Markdown via the MinerU API.

Accepts local file paths or remote URLs (http(s)://...). Single file or batch.
For each input, downloads the result zip and extracts Markdown + images +
layout/content JSON (+ HTML/DOCX/TeX when present in the zip). The token is read
from the MINERU_TOKEN env var (loaded from .env via _env.py when run through bash
without a shell-sourced env).

Usage:
    python parse_pdf.py INPUT [INPUT ...] [--model-version vlm] [--output-dir DIR]

INPUTs that start with http(s):// are treated as URLs; the rest as local paths.
Local files are uploaded as one MinerU batch (<= 50). URLs are submitted one by one.

Stdout prints an ===RESULT=== JSON array (one entry per input) for the AI to
locate the parsed Markdown, then an ===SUMMARY=== line. Diagnostics go to stderr.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests

# Load .env (MINERU_TOKEN) before anything runs, so this works under bash
# without a shell-sourced env. No-op if no .env is found.
try:
    from _env import load_env_once
    load_env_once()
except Exception:
    pass

DEFAULT_BASE_URL = "https://mineru.net"
MODEL_VERSIONS = ("vlm", "auto")  # vlm: 视觉语言模型（默认，复杂版面更优）; auto: 传统流水线
DEFAULT_OUTPUT_DIR = "./outputs/lusca-pdf-parse"
MAX_BATCH = 50  # MinerU 单批上限


class MinerUError(RuntimeError):
    """Raised when the MinerU API returns a non-zero code or an unexpected shape."""


def _slugify(name: str) -> str:
    """文件名 / URL 末段 → kebab-case slug，用作输出子目录名。"""
    stem = Path(name).stem or "doc"
    slug = re.sub(r"[^\w\s-]", "", stem).strip().lower()
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug or "doc"


def _is_url(s: str) -> bool:
    return urlparse(s).scheme in ("http", "https")


def _check_code(result: dict, action: str) -> dict:
    """MinerU 约定 code==0 为成功；非 0 抛错并带上 msg。"""
    if result.get("code") != 0:
        raise MinerUError(f"{action} 失败: code={result.get('code')} msg={result.get('msg')}")
    return result


class MinerUClient:
    """MinerU 精准解析 API 客户端：本地批量上传 / URL 提交 → 轮询 → 下载解压。"""

    def __init__(self, token: str, base_url: str = DEFAULT_BASE_URL,
                 poll_interval: int = 5, timeout: int = 600, max_workers: int = 5):
        if not token:
            sys.exit(
                "❌ 未找到 MINERU_TOKEN。请在仓库根 .env 设置 MINERU_TOKEN=<token>"
                "（申请方式见 references/mineru_api.md）。"
            )
        self.base_url = base_url.rstrip("/")
        self.poll_interval = poll_interval
        self.timeout = timeout
        self.max_workers = max_workers
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    # ---------------- 提交 ----------------

    def submit_url(self, url: str, model_version: str) -> str:
        """提交一个 URL 解析任务，返回 task_id。"""
        resp = requests.post(
            f"{self.base_url}/api/v4/extract/task",
            headers=self.headers,
            json={"url": url, "model_version": model_version},
            timeout=60,
        )
        resp.raise_for_status()
        data = _check_code(resp.json(), "提交 URL 任务")["data"]
        task_id = data.get("task_id")
        if not task_id:
            raise MinerUError(f"URL 任务未返回 task_id: {json.dumps(data, ensure_ascii=False)[:300]}")
        return task_id

    def upload_batch(self, paths: list[str], model_version: str) -> tuple[str, list[dict]]:
        """申请批量上传链接并并行 PUT 上传本地文件。返回 (batch_id, file_list)。"""
        files_payload = [
            {"name": Path(p).name, "data_id": f"{idx}_{Path(p).name}"}
            for idx, p in enumerate(paths)
        ]
        resp = requests.post(
            f"{self.base_url}/api/v4/file-urls/batch",
            headers=self.headers,
            json={"files": files_payload, "model_version": model_version},
            timeout=60,
        )
        resp.raise_for_status()
        data = _check_code(resp.json(), "申请上传链接")["data"]
        batch_id = data.get("batch_id")
        file_urls = data.get("file_urls") or []
        if not batch_id or len(file_urls) != len(paths):
            raise MinerUError(
                f"批量上传链接异常: batch_id={batch_id}, "
                f"got {len(file_urls)} urls for {len(paths)} files"
            )
        file_list = [
            {"path": p, "name": Path(p).name, "file_url": file_urls[i]}
            for i, p in enumerate(paths)
        ]
        # 并行上传（预签名 URL 用 PUT，不带 Content-Type）
        with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futs = {ex.submit(self._put_file, fi): fi for fi in file_list}
            for fut in as_completed(futs):
                fut.result()  # 失败直接抛，由调用方捕获并整体记错
        return batch_id, file_list

    @staticmethod
    def _put_file(fi: dict) -> None:
        with open(fi["path"], "rb") as fp:
            resp = requests.put(fi["file_url"], data=fp, timeout=300)
        if resp.status_code != 200:
            raise MinerUError(f"上传失败 {fi['name']}: HTTP {resp.status_code} {resp.text[:200]}")

    # ---------------- 轮询 ----------------

    def get_batch_task_ids(self, batch_id: str) -> list[str]:
        """从 batch_id 取各子任务 task_id（上传后任务注册有延迟，短轮询等待）。"""
        url = f"{self.base_url}/api/v4/extract/batch/{batch_id}"
        deadline = time.time() + min(self.timeout, 120)
        while time.time() < deadline:
            resp = requests.get(url, headers=self.headers, timeout=30)
            resp.raise_for_status()
            data = _check_code(resp.json(), "查询批量任务详情")["data"]
            # 字段命名容错：不同版本可能用不同 key
            for key in ("task_ids", "task_id_list"):
                ids = data.get(key)
                if ids:
                    return ids
            tasks = data.get("task_list") or data.get("tasks") or []
            ids = [t.get("task_id") for t in tasks if t.get("task_id")]
            if ids:
                return ids
            time.sleep(self.poll_interval)
        raise MinerUError(f"无法从批量任务 {batch_id} 解析出 task_id（字段路径可能已变，详见 references/mineru_api.md）")

    def wait_task(self, task_id: str) -> dict:
        """轮询单个 task_id 直到 done/failed/超时，返回结果 data（含 full_zip_url）。"""
        url = f"{self.base_url}/api/v4/extract/task/{task_id}"
        deadline = time.time() + self.timeout
        last = ""
        while time.time() < deadline:
            resp = requests.get(url, headers=self.headers, timeout=30)
            resp.raise_for_status()
            data = _check_code(resp.json(), "查询任务状态")["data"]
            state = data.get("state")
            if state == "done":
                return data
            if state == "failed":
                raise MinerUError(f"任务失败: {data.get('err_msg')}")
            prog = data.get("extract_progress") or {}
            msg = f"state={state} pages={prog.get('extracted_pages', 0)}/{prog.get('total_pages', 0)}"
            if msg != last:
                print(f"  ⏳ {task_id[:8]} {msg}", file=sys.stderr)
                last = msg
            time.sleep(self.poll_interval)
        raise TimeoutError(f"任务 {task_id} 轮询超时（{self.timeout}s）")

    # ---------------- 下载 / 解压 / 定位 ----------------

    def finalize(self, slug: str, task_id: str, data: dict, output_root: Path) -> dict:
        """下载结果 zip 并解压到 {output_root}/{slug}/parsed/，定位关键文件。"""
        zip_url = data.get("full_zip_url") or data.get("zip_url")
        if not zip_url:
            raise MinerUError(f"任务 {task_id} 无 full_zip_url: {json.dumps(data, ensure_ascii=False)[:300]}")
        slug_dir = output_root / slug
        out_dir = slug_dir / "parsed"
        out_dir.mkdir(parents=True, exist_ok=True)
        zip_path = slug_dir / f"{slug}.zip"
        self._download(zip_url, zip_path)
        self._extract(zip_path, out_dir)
        files = self._find_files(out_dir)
        return {
            "slug": slug,
            "task_id": task_id,
            "state": "done",
            "output_dir": str(out_dir),
            "zip": str(zip_path),
            "files": files,
        }

    @staticmethod
    def _download(zip_url: str, dest: Path) -> None:
        with requests.get(zip_url, stream=True, timeout=300) as r:
            r.raise_for_status()
            with open(dest, "wb") as fp:
                for chunk in r.iter_content(8192):
                    fp.write(chunk)

    @staticmethod
    def _extract(zip_path: Path, out_dir: Path) -> None:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(out_dir)

    @staticmethod
    def _find_files(out_dir: Path) -> dict:
        """定位解析产物：markdown / images_dir / layout_json / content_json / html / docx / tex。"""
        found: dict[str, str] = {}
        for f in out_dir.rglob("*"):
            if f.is_dir():
                if f.name.lower() in ("images", "image") and "images_dir" not in found:
                    found["images_dir"] = str(f)
                continue
            suf = f.suffix.lower()
            name = f.name.lower()
            if suf == ".md" and "markdown" not in found:
                found["markdown"] = str(f)
            elif suf == ".json" and "layout" in name:
                found["layout_json"] = str(f)
            elif suf == ".json" and "content" in name:
                found["content_json"] = str(f)
            elif suf in (".html", ".docx", ".tex"):
                found.setdefault(suf[1:], str(f))
        return found


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Parse PDF/images/DOCX → structured Markdown via MinerU API."
    )
    ap.add_argument("inputs", nargs="+", help="本地文件路径或 URL（http(s):// 开头）")
    ap.add_argument("--model-version", choices=MODEL_VERSIONS, default="vlm",
                    help="vlm（默认，复杂版面更优）/ auto（传统流水线，更快）")
    ap.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="输出根目录")
    ap.add_argument("--poll-interval", type=int, default=5, help="轮询间隔（秒）")
    ap.add_argument("--timeout", type=int, default=600, help="单任务轮询超时（秒）")
    ap.add_argument("--max-workers", type=int, default=5, help="本地文件上传并发数")
    args = ap.parse_args()

    client = MinerUClient(
        os.environ.get("MINERU_TOKEN", ""),
        poll_interval=args.poll_interval,
        timeout=args.timeout,
        max_workers=args.max_workers,
    )

    urls = [i for i in args.inputs if _is_url(i)]
    locals_ = [i for i in args.inputs if not _is_url(i)]
    for p in locals_:
        if not Path(p).is_file():
            sys.exit(f"❌ 文件不存在: {p}")
    if len(locals_) > MAX_BATCH:
        sys.exit(f"❌ 单批本地文件不能超过 {MAX_BATCH} 个（收到 {len(locals_)}）")

    output_root = Path(args.output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []

    # URL：逐个提交
    for url in urls:
        slug = _slugify(urlparse(url).path.rsplit("/", 1)[-1] or url)
        print(f"🌐 提交 URL: {url}", file=sys.stderr)
        try:
            task_id = client.submit_url(url, args.model_version)
            data = client.wait_task(task_id)
            res = client.finalize(slug, task_id, data, output_root)
            res["input"] = url
            results.append(res)
            print(f"  ✅ {slug}", file=sys.stderr)
        except Exception as e:
            results.append({"input": url, "slug": slug, "state": "failed", "error": str(e)})
            print(f"  ❌ {slug}: {e}", file=sys.stderr)

    # 本地：批量上传后逐个轮询
    if locals_:
        print(f"📦 上传 {len(locals_)} 个本地文件...", file=sys.stderr)
        try:
            batch_id, file_list = client.upload_batch(locals_, args.model_version)
            task_ids = client.get_batch_task_ids(batch_id)
            for fi, task_id in zip(file_list, task_ids):
                slug = _slugify(fi["name"])
                try:
                    data = client.wait_task(task_id)
                    res = client.finalize(slug, task_id, data, output_root)
                    res["input"] = fi["name"]
                    results.append(res)
                    print(f"  ✅ {slug}", file=sys.stderr)
                except Exception as e:
                    results.append({"input": fi["name"], "slug": slug, "state": "failed", "error": str(e)})
                    print(f"  ❌ {slug}: {e}", file=sys.stderr)
        except Exception as e:
            # 上传 / 批次失败：每个本地文件记一笔
            for p in locals_:
                results.append({"input": p, "slug": _slugify(Path(p).name), "state": "failed", "error": str(e)})
            print(f"  ❌ 批量上传失败: {e}", file=sys.stderr)

    print("===RESULT===")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    ok = sum(1 for r in results if r.get("state") == "done")
    fail = len(results) - ok
    print(f"===SUMMARY=== 成功 {ok} / 失败 {fail}")
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
