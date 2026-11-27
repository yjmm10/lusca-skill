#!/usr/bin/env python3
"""Capture real page screenshots with Playwright and write an index.

Usage:
  python capture_screenshots.py TARGET_DIR --url http://localhost:4321
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


PAGE_PATHS = {
    "landing": "",
    "data": "data/",
    "about": "about/",
}

PAGE_LABELS = {
    "zh": {
        "landing": "落地页",
        "data": "数据页",
        "about": "关于页",
    },
    "en": {
        "landing": "Landing page",
        "data": "Data page",
        "about": "About page",
    },
}


def build_url(base: str, locale: str, page: str, theme: str) -> str:
    prefix = "" if locale == "zh" else "en/"
    path = f"{prefix}{PAGE_PATHS[page]}"
    separator = "&" if "?" in base else "?"
    return f"{base.rstrip('/')}/{path}{separator}theme={theme}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--url", default="http://localhost:4321")
    parser.add_argument("--out", default="docs/images")
    parser.add_argument("--locales", default="zh", help="Comma-separated: zh,en")
    parser.add_argument("--themes", default="light,dark", help="Comma-separated: light,dark")
    parser.add_argument("--pages", default="landing,data,about")
    parser.add_argument("--viewport", default="1440,900")
    parser.add_argument("--mobile", action="store_true", help="Use 390,844 viewport and suffix names with -mobile")
    args = parser.parse_args()

    if shutil.which("npx") is None:
        print("error: npx is not available; install Playwright and capture screenshots manually", file=sys.stderr)
        return 2

    root = args.target.expanduser().resolve()
    out_dir = root / args.out
    out_dir.mkdir(parents=True, exist_ok=True)

    locales = [item.strip() for item in args.locales.split(",") if item.strip()]
    themes = [item.strip() for item in args.themes.split(",") if item.strip()]
    pages = [item.strip() for item in args.pages.split(",") if item.strip()]
    viewport = "390,844" if args.mobile else args.viewport

    captured: list[tuple[str, str, str, Path]] = []
    for locale in locales:
        for theme in themes:
            for page in pages:
                suffix = "-mobile" if args.mobile else ""
                filename = f"{page}-{locale}-{theme}{suffix}.png"
                destination = out_dir / filename
                url = build_url(args.url, locale, page, theme)
                command = [
                    "npx",
                    "playwright",
                    "screenshot",
                    f"--viewport-size={viewport}",
                    "--full-page",
                    "--wait-for-timeout=800",
                    url,
                    str(destination),
                ]
                print(f"capturing {filename} <- {url}")
                result = subprocess.run(command, check=False)
                if result.returncode != 0:
                    print(f"error: screenshot failed for {url}", file=sys.stderr)
                    return result.returncode
                captured.append((page, locale, theme, filename))

    lines = ["# 页面预览", ""]
    for page, locale, theme, filename in captured:
        label = PAGE_LABELS.get(locale, {}).get(page, page)
        lines.extend([f"## {label}（{locale} / {theme}）", "", f"![{label}](./images/{filename})", "", "要点：页面真实渲染结果，主题由 URL 参数固定。", ""])
    (root / "docs" / "screenshots.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {root / 'docs' / 'screenshots.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
