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
    parser.add_argument("--skip-screenshots", action="store_true", help="Skip the screenshot check (user opted out; skipped items do not fail --strict)")
    args = parser.parse_args()

    root = args.target.expanduser().resolve()
    checks: list[tuple[str, bool | None, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, bool(ok), detail))

    def skip(name: str, detail: str = "") -> None:
        checks.append((name, None, detail))

    # 结构契约：只锁不变量（数据单一源、三页双语路由、SEO/GEO、品牌、文档），不锁实现细节。
    # 页面/组件/tokens 的具体文件名与写法允许差异化。
    contract_files = [
        "package.json",
        "README.md",
        "src/data/product.json",
        "src/data/highlights.json",
        "public/logo.svg",
        "public/logo.png",
        "public/favicon.svg",
        "public/og-image.png",
        "docs/product-overview.md",
        "docs/data-sources.md",
        "docs/ui-decisions.md",
        "docs/seo-geo.md",
        "docs/screenshots.md",
        "docs/brand.md",
    ]
    missing = [item for item in contract_files if not (root / item).is_file()]

    # 三页双语路由（结构契约：zh 默认 + /en/）
    routes = {
        "zh landing (src/pages/index.astro)": root / "src/pages/index.astro",
        "zh data (/data/)": root / "src/pages/data/index.astro",
        "zh about (/about/)": root / "src/pages/about/index.astro",
        "en landing (/en/)": root / "src/pages/en/index.astro",
        "en data (/en/data/)": root / "src/pages/en/data/index.astro",
        "en about (/en/about/)": root / "src/pages/en/about/index.astro",
    }
    missing += [name for name, path in routes.items() if not path.is_file()]

    # robots / sitemap / llms.txt：端点或静态文件均可
    def has_any(*candidates: str) -> bool:
        return any((root / c).exists() for c in candidates)

    if not has_any("src/pages/robots.txt.ts", "public/robots.txt", "src/pages/robots.txt"):
        missing.append("robots (route or public/robots.txt)")
    if not has_any("src/pages/sitemap.xml.ts", "public/sitemap.xml", "src/pages/sitemap.xml"):
        missing.append("sitemap (route or public/sitemap.xml)")
    if not has_any("src/pages/llms.txt.ts", "public/llms.txt", "src/pages/llms.txt"):
        missing.append("llms.txt (route or public/llms.txt)")

    check("contract files, three bilingual routes and index endpoints exist", not missing, ", ".join(missing))

    package = {}
    try:
        package = json.loads(read(root / "package.json"))
    except json.JSONDecodeError as exc:
        check("package.json parses", False, str(exc))
    all_scripts = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
    scripts = package.get("scripts", {})
    check("Astro + Tailwind installed", all(k in all_scripts for k in ("astro", "tailwindcss")))
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

    # i18n 字典：src/i18n/ 下任意文件含 zh/en 字典（不限定文件名）
    i18n_files = list((root / "src/i18n").rglob("*.ts")) + list((root / "src/i18n").rglob("*.mjs")) if (root / "src/i18n").is_dir() else []
    i18n_content = "\n".join(read(f) for f in i18n_files)
    check("i18n zh/en dictionaries", bool(i18n_files) and "zh" in i18n_content and "en" in i18n_content, "src/i18n/ 下未找到 zh/en 字典")

    # tokens：src 下任意 css 含 :root + 暗色主题 + 跟随系统（不限定文件名）
    css_files = list((root / "src").rglob("*.css"))
    tokens = "\n".join(read(f) for f in css_files)
    check("theme tokens include light/dark/system", ":root" in tokens and 'data-theme="dark"' in tokens and "prefers-color-scheme" in tokens)

    # SEO/主题标记：任意 layout（src/layouts/**）内查，不限定 BaseLayout 文件名
    layout_files = list((root / "src/layouts").rglob("*.astro"))
    layout = "\n".join(read(f) for f in layout_files)
    seo_markers = ["rel=\"canonical\"", "hreflang", "og:title", "application/ld+json", "data-theme"]
    missing_seo = [marker for marker in seo_markers if marker not in layout]
    check("SEO/theme markers in layout", not missing_seo, ", ".join(missing_seo))

    logo_svg = read(root / "public/logo.svg")
    rich_icon = ("linearGradient" in logo_svg or "radialGradient" in logo_svg) or logo_svg.count("<path") + logo_svg.count("<ellipse") + logo_svg.count("<circle") >= 3
    check("logo has layered icon elements", rich_icon, "needs gradient or >=3 shape elements")

    astro_config = read(root / "astro.config.mjs") if (root / "astro.config.mjs").exists() else read(root / "astro.config.ts")
    check("static output and i18n routing", re.search(r"output\s*:\s*['\"]static['\"]", astro_config) is not None and "zh" in astro_config and "en" in astro_config)

    # 落地页从派生数据读：源码中引用 highlights（数据单一源红线的落地证据）
    src_texts = "\n".join(read(f) for f in list((root / "src").rglob("*.astro")) + list((root / "src").rglob("*.ts")))
    check("landing derives from highlights.json", "highlights" in src_texts)

    # 关于页：含产品故事 / 作者 / 免责声明内容标记（不限文件名）
    about_texts = "\n".join(read(f) for f in list((root / "src/pages/about").rglob("*.astro")) + list((root / "src").rglob("*About*.astro")))
    has_boundaries = any(k in about_texts for k in ("disclaimer", "免责"))
    has_author = any(k in about_texts for k in ("author", "作者", "团队"))
    check("about page has product story/author/disclaimer", has_boundaries and has_author, "关于页缺免责声明或作者信息")

    cache_files = [item for item in ("public/_headers", "vercel.json", "netlify.toml") if (root / item).exists()]
    check("deployment cache config present", bool(cache_files), ", ".join(cache_files))

    docs = read(root / "docs/ui-decisions.md")
    cited = len(re.findall(r"https?://", docs))
    ui_ok = bool(docs) and "待补充" not in docs and cited >= 3
    check("UI decisions recorded (no placeholder, >=3 cited sources)", ui_ok, "仍含待补充占位或可核验来源不足 3 个——交付前必须完成组件调研" if not ui_ok else "")

    screenshot_doc = read(root / "docs/screenshots.md")
    if args.skip_screenshots:
        skip("at least 3 real screenshots indexed", "用户选择跳过截图——交付说明需标注该选择与原因")
    else:
        images = re.findall(r"\]\(\./images/([^)]+\.png)\)", screenshot_doc)
        existing_images = [name for name in images if (root / "docs" / "images" / name).is_file()]
        check("at least 3 real screenshots indexed", len(existing_images) >= 3, f"found {len(existing_images)}；环境无 Playwright 时可询问用户后用 --skip-screenshots 跳过")

    forbidden = re.findall(r"(?:本文由\s*AI\s*生成|仅供参考|欢迎指正|数据与结论均来自论文原文)", read(root / "README.md") + screenshot_doc)
    check("no AI disclaimer tail", not forbidden, ", ".join(set(forbidden)))

    width = max(len(name) for name, _, _ in checks)
    failed = 0
    skipped = 0
    for name, ok, detail in checks:
        if ok is None:
            skipped += 1
            suffix = f" — {detail}" if detail else ""
            print(f"[SKIP] {name.ljust(width)}{suffix}")
        elif ok:
            print(f"[PASS] {name.ljust(width)}")
        else:
            failed += 1
            suffix = f" — {detail}" if detail else ""
            print(f"[FAIL] {name.ljust(width)}{suffix}")

    passed = sum(1 for _, ok, _ in checks if ok is True)
    print(f"\n{passed}/{len(checks)} checks passed, {skipped} skipped")
    if args.strict and failed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
