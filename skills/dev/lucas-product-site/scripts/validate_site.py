#!/usr/bin/env python3
"""Validate a generated static product site.

Usage:
  python validate_site.py TARGET_DIR [--strict]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_normalize_module():
    spec = importlib.util.spec_from_file_location("lucas_normalize_data", HERE / "normalize_data.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load normalize_data.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--strict", action="store_true", help="Exit 1 when any check fails")
    args = parser.parse_args()

    root = args.target.expanduser().resolve()
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, bool(ok), detail))

    required = [
        "package.json",
        "astro.config.mjs",
        "tailwind.config.mjs",
        "README.md",
        "src/data/product.json",
        "src/data/highlights.json",
        "src/i18n/ui.ts",
        "src/styles/tokens.css",
        "src/layouts/BaseLayout.astro",
        "src/components/ProductPreview.astro",
        "src/components/MetricCard.astro",
        "src/components/LatestStrip.astro",
        "src/components/DataTable.astro",
        "src/pages/index.astro",
        "src/pages/data/index.astro",
        "src/pages/about/index.astro",
        "src/pages/en/index.astro",
        "src/pages/en/data/index.astro",
        "src/pages/en/about/index.astro",
        "src/pages/robots.txt.ts",
        "src/pages/sitemap.xml.ts",
        "src/pages/llms.txt.ts",
        "public/logo.svg",
        "public/logo.png",
        "public/og-image.png",
        "public/favicon.svg",
        "public/images/product-preview.svg",
        "docs/product-overview.md",
        "docs/data-sources.md",
        "docs/ui-decisions.md",
        "docs/seo-geo.md",
        "docs/screenshots.md",
        "docs/brand.md",
    ]
    missing = [item for item in required if not (root / item).is_file()]
    check("required files exist", not missing, ", ".join(missing))

    package = {}
    try:
        package = json.loads(read(root / "package.json"))
    except json.JSONDecodeError as exc:
        check("package.json parses", False, str(exc))
    all_scripts = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    scripts = package.get("scripts", {})
    check("Astro + Tailwind + TS installed", all(k in all_scripts for k in ("astro", "tailwindcss", "typescript")))
    check("npm scripts present", all(k in scripts for k in ("dev", "build", "preview")))

    normalize = load_normalize_module()
    try:
        data = normalize.load_json(root / "src/data/product.json")
        normalize.validate(data)
        check("product.json validates", True)
    except normalize.ValidationError as exc:
        check("product.json validates", False, str(exc))
        data = {}

    try:
        highlights = json.loads(read(root / "src/data/highlights.json"))
        check("highlights.json derived shape", all(k in highlights for k in ("product", "latest", "metrics", "features")))
    except json.JSONDecodeError as exc:
        check("highlights.json derived shape", False, str(exc))

    ui = read(root / "src/i18n/ui.ts")
    check("i18n zh/en dictionaries", "zh:" in ui and "en:" in ui and "Locale" in ui)

    tokens = read(root / "src/styles/tokens.css")
    check("theme tokens include light/dark/system", ":root" in tokens and 'data-theme="dark"' in tokens and "prefers-color-scheme" in tokens)

    layout = read(root / "src/layouts/BaseLayout.astro")
    seo_markers = ["rel=\"canonical\"", "hreflang", "og:title", "application/ld+json", "data-theme"]
    missing_seo = [marker for marker in seo_markers if marker not in layout]
    check("SEO/theme markers in layout", not missing_seo, ", ".join(missing_seo))

    logo_svg = read(root / "public/logo.svg")
    rich_icon = ("linearGradient" in logo_svg or "radialGradient" in logo_svg) or logo_svg.count("<path") + logo_svg.count("<ellipse") + logo_svg.count("<circle") >= 3
    check("logo has layered icon elements", rich_icon, "needs gradient or >=3 shape elements")

    astro_config = read(root / "astro.config.mjs")
    check("static output and i18n routing", "output: 'static'" in astro_config and "locales: ['zh', 'en']" in astro_config)

    previews = read(root / "src/components/ProductPreview.astro")
    check("lazy product previews", 'loading={index === 0 ? \'eager\' : \'lazy\'}' in previews or "loading=\"lazy\"" in previews)

    about = read(root / "src/components/AboutContent.astro")
    check("about page has product/author/disclaimer", all(k in about for k in ("productStory", "author", "disclaimer")))

    cache_files = [item for item in ("public/_headers", "vercel.json", "netlify.toml") if (root / item).exists()]
    check("deployment cache config present", bool(cache_files), ", ".join(cache_files))

    docs = read(root / "docs/ui-decisions.md")
    check("UI decisions recorded", "候选" in docs or "候选来源" in docs)

    screenshot_doc = read(root / "docs/screenshots.md")
    images = re.findall(r"\]\(\./images/([^)]+\.png)\)", screenshot_doc)
    existing_images = [name for name in images if (root / "docs" / "images" / name).is_file()]
    check("at least 3 real screenshots indexed", len(existing_images) >= 3, f"found {len(existing_images)}")

    forbidden = re.findall(r"(?:本文由\s*AI\s*生成|仅供参考|欢迎指正|数据与结论均来自论文原文)", read(root / "README.md") + screenshot_doc)
    check("no AI disclaimer tail", not forbidden, ", ".join(set(forbidden)))

    width = max(len(name) for name, _, _ in checks)
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        suffix = f" — {detail}" if detail and not ok else ""
        print(f"[{status}] {name.ljust(width)}{suffix}")

    passed = sum(1 for _, ok, _ in checks if ok)
    print(f"\n{passed}/{len(checks)} checks passed")
    if args.strict and passed != len(checks):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
