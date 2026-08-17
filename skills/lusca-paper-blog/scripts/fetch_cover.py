#!/usr/bin/env python3
"""lusca-paper-blog 封面图获取脚本（不重复版）

保证**跨文章长期不重复**：合并 Bing 每日一图候选池（~15 张）与 picsum.photos
全量池（~300 张）为候选，用持久化登记文件记录已用过的图，每次只从**没用过的**
里选；两池全用完才清空登记重新循环。登记文件在用户级缓存（跨项目、跨会话生效）。
禁止手选——手选会反复取同一张。

Usage:
    python3 skills/lusca-paper-blog/scripts/fetch_cover.py <slug> <timestamp> <outdir>

    slug      — 博客 slug (kebab-case)
    timestamp — 运行时间戳 (YYYYMMDDHHmmss)，即文件名里的时间戳
    outdir    — 博客输出目录 (如 outputs/lusca-paper-blog/my-slug/)

Output (JSON to stdout):
    {"url": "https://...", "backup": "imgs/cover.jpg", "source": "Bing 每日一图 · ..."}
"""
import sys
import json
import random
import hashlib
import os
import urllib.request
from datetime import datetime

REGISTRY_PATH = os.path.expanduser("~/.cache/lusca-skill/lusca-paper-blog/used_covers.json")
PICSUM_PAGES = 3          # v2/list 每页 100 张，共 300 张
PICSUM_W, PICSUM_H = 1200, 600


def md5int(s: str) -> int:
    """Deterministic integer hash (Python's hash() is salted per process)."""
    return int(hashlib.md5(s.encode()).hexdigest(), 16)


def http_get_json(url: str, timeout: int = 15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_bing_pool() -> list:
    """Bing daily wallpapers (idx=0 + idx=7, deduped by urlbase). ~15 张."""
    images = []
    for idx in [0, 7]:
        try:
            data = http_get_json(
                f"https://cn.bing.com/HPImageArchive.aspx?format=js&idx={idx}&n=8&mkt=zh-CN")
            images.extend(data.get("images", []))
        except Exception:
            continue
    seen, unique = set(), []
    for img in images:
        key = img.get("urlbase", "")
        if key and key not in seen:
            seen.add(key)
            unique.append(("bing:" + key,
                           "https://cn.bing.com" + img["url"],
                           f"Bing 每日一图 · {img.get('copyright', 'Bing Daily Wallpaper')}"))
    return unique


def fetch_picsum_pool() -> list:
    """Picsum.photos full pool via v2/list. ~300 张."""
    out = []
    for page in range(1, PICSUM_PAGES + 1):
        try:
            data = http_get_json(f"https://picsum.photos/v2/list?page={page}&limit=100")
        except Exception:
            continue
        for item in data:
            out.append((f"picsum:{item['id']}",
                        f"https://picsum.photos/id/{item['id']}/{PICSUM_W}/{PICSUM_H}",
                        f"picsum · id={item['id']} · {item.get('author', '')}".rstrip(" ·")))
    return out


def load_registry() -> dict:
    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_registry(registry: dict):
    try:
        os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
        with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(registry, f, ensure_ascii=False, indent=1)
    except Exception:
        pass  # 登记写不进（只读环境）不影响出图，只是跨次去重失效


def pick(pool: list, seed: str):
    """Pick one candidate by seed hash (same inputs → same pick). Returns tuple."""
    h = md5int(seed)
    return pool[h % len(pool)]


def download(url: str, path: str) -> bool:
    """Download URL to local path. Returns True on success."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return True
    except Exception:
        return False


def main():
    if len(sys.argv) != 4:
        print("Usage: fetch_cover.py <slug> <timestamp> <outdir>", file=sys.stderr)
        sys.exit(1)

    slug, timestamp, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    seed = f"{slug}-{timestamp}"
    backup_path = os.path.join(outdir, "imgs", "cover.jpg")

    # 合并两池，去掉已用过的；全用完则清空登记重新循环
    pool = fetch_bing_pool() + fetch_picsum_pool()
    registry = load_registry()
    unused = [c for c in pool if c[0] not in registry]
    if pool and not unused:
        registry = {}
        unused = pool

    if unused:
        key, url, source = pick(unused, seed)
        registry[key] = {"slug": slug, "used_at": datetime.now().strftime("%Y-%m-%d")}
        save_registry(registry)
    else:
        # 两池都取不到（离线）：退化为带唯一 seed 的 picsum 直链
        safe = seed.replace("/", "-").replace(" ", "-")
        url = f"https://picsum.photos/seed/{safe}/{PICSUM_W}/{PICSUM_H}"
        source = f"picsum · seed={safe}"

    download(url, backup_path)

    print(json.dumps({
        "url": url,
        "backup": "imgs/cover.jpg",
        "source": source,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
