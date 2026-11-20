#!/usr/bin/env python3
"""lusca-tech-writing: batch-download blog images with format sniffing, size checks, and hash dedup.

Reads a manifest JSON (array of {url, name, source?, note?}), downloads each image,
validates it is a real image (magic bytes), enforces size bounds, dedupes by content
hash, and writes files into the output dir.

Usage:
    python3 fetch_images.py --manifest imgs-manifest.json \
        --output-dir outputs/lusca-tech-writing/<slug>/imgs [--timeout 30] \
        [--min-bytes 1024] [--max-bytes 20971520]

Output (stdout):
    ===RESULT===   JSON array, one entry per manifest item:
                   {"name", "url", "source", "file", "bytes", "sha256", "ok",
                    "error", "duplicate_of"}
    ===SUMMARY===  成功 X / 失败 Y / 去重 Z

Exit code: 0 if the manifest was processed (individual failures reported in JSON),
2 on manifest read/parse error.

Notes:
- SVGs are downloaded but cannot be visually vetted downstream (see
  references/image-workflow.md); they are reported with ext "svg" so the caller
  can decide.
- Standard library only; Windows-safe (utf-8, pathlib).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) lusca-tech-writing/1.0"
)

MAGIC = [
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"BM", "bmp"),
]

CONTENT_TYPE_EXT = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/bmp": "bmp",
    "image/svg+xml": "svg",
    "image/x-icon": "ico",
    "image/avif": "avif",
}

URL_EXT_RE = re.compile(r"\.(png|jpe?g|gif|webp|bmp|svg|ico|avif)\s*$", re.I)


def sniff_ext(data: bytes, content_type: str, url: str) -> str | None:
    """Detect image extension from magic bytes, then content-type, then URL."""
    for magic, ext in MAGIC:
        if data.startswith(magic):
            return ext
    if len(data) > 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    head = data[:512].lstrip()
    if head[:4] == b"<svg" or head.startswith(b"<?xml"):
        return "svg"
    ct = content_type.split(";")[0].strip().lower()
    if ct in CONTENT_TYPE_EXT:
        return CONTENT_TYPE_EXT[ct]
    m = URL_EXT_RE.search(url.split("?")[0])
    if m:
        ext = m.group(1).lower()
        return "jpg" if ext in ("jpeg", "jpg") else ext
    return None


def sanitize_name(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name.strip()).strip("-.")
    return name or "img"


def unique_path(directory: Path, stem: str, ext: str) -> Path:
    """First free path: stem.ext, stem-2.ext, stem-3.ext, ..."""
    candidate = directory / f"{stem}.{ext}"
    n = 2
    while candidate.exists():
        candidate = directory / f"{stem}-{n}.{ext}"
        n += 1
    return candidate


def download(url: str, timeout: int, max_bytes: int) -> tuple[bytes, str]:
    """Return (data, content_type); raise on HTTP/network errors or oversize."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        ct = resp.headers.get("Content-Type", "")
        data = resp.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"exceeds max size ({max_bytes} bytes)")
    return data, ct


def main() -> int:
    # Windows 控制台默认 GBK，强制 UTF-8 保证中文摘要不乱码
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser(description="Batch-download blog images with validation & dedup")
    ap.add_argument("--manifest", required=True, help="JSON array of {url, name, source?, note?}")
    ap.add_argument("--output-dir", required=True, help="directory to save images into")
    ap.add_argument("--timeout", type=int, default=30, help="per-image download timeout (s)")
    ap.add_argument("--min-bytes", type=int, default=1024, help="reject images smaller than this")
    ap.add_argument("--max-bytes", type=int, default=20 * 1024 * 1024, help="reject images larger than this")
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    try:
        items = json.loads(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            raise ValueError("manifest must be a JSON array")
    except Exception as exc:  # noqa: BLE001 - report to caller
        print(f"manifest error: {exc}", file=sys.stderr)
        return 2

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    seen_hashes: dict[str, str] = {}  # sha256 -> first saved name
    results: list[dict] = []
    ok_count = dup_count = fail_count = 0

    for item in items:
        url = str(item.get("url", "")).strip()
        name = sanitize_name(str(item.get("name", "")) or "img")
        source = str(item.get("source", "")).strip()
        entry: dict = {"name": name, "url": url, "source": source,
                       "file": None, "bytes": 0, "sha256": None,
                       "ok": False, "error": None, "duplicate_of": None}
        results.append(entry)

        if not url.startswith(("http://", "https://")):
            entry["error"] = f"invalid url: {url!r}"
            fail_count += 1
            continue

        try:
            data, ct = download(url, args.timeout, args.max_bytes)
        except Exception as exc:  # noqa: BLE001
            entry["error"] = f"download failed: {exc}"
            fail_count += 1
            continue

        if len(data) < args.min_bytes:
            entry["error"] = f"too small ({len(data)} bytes, min {args.min_bytes})"
            fail_count += 1
            continue

        ext = sniff_ext(data, ct, url)
        if ext is None:
            entry["error"] = f"not a recognizable image (content-type {ct or 'unknown'})"
            fail_count += 1
            continue

        sha = hashlib.sha256(data).hexdigest()
        entry["bytes"] = len(data)
        entry["sha256"] = sha

        if sha in seen_hashes:
            entry["duplicate_of"] = seen_hashes[sha]
            entry["error"] = f"duplicate content of {seen_hashes[sha]}"
            dup_count += 1
            continue

        path = unique_path(out_dir, name, ext)
        path.write_bytes(data)
        entry["file"] = str(path)
        entry["ok"] = True
        seen_hashes[sha] = path.stem
        ok_count += 1

    print("===RESULT===")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print("===SUMMARY===")
    print(f"成功 {ok_count} / 失败 {fail_count} / 去重 {dup_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
