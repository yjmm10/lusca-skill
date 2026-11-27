#!/usr/bin/env python3
"""Create an Astro + TypeScript + Tailwind static product-site skeleton.

Usage:
  python init_project.py TARGET_DIR --name "Aether" --domain "example.com" \
    --description "一句话定位" --deploy github
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import struct
import sys
import zlib
from pathlib import Path
from textwrap import dedent
from typing import Any


HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent


def render(text: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        text = text.replace(f"__{key}__", value)
    return text


def write_file(root: Path, relative: str, content: str, overwrite: bool = False) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing file: {target}")
    target.write_text(content, encoding="utf-8")


def copy_asset(root: Path, asset_name: str, relative: str) -> None:
    source = SKILL_ROOT / "assets" / asset_name
    write_file(root, relative, source.read_text(encoding="utf-8"))


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _star_points(cx: float, cy: float, scale: float, samples: int = 24) -> list[tuple[float, float]]:
    """Sample the four-point concave sparkle (same curves as the SVG logo)."""
    segs = [
        ((0.0, -108.0), (15.0, -36.0), (36.0, -15.0), (108.0, 0.0)),
        ((108.0, 0.0), (36.0, 15.0), (15.0, 36.0), (0.0, 108.0)),
        ((0.0, 108.0), (-15.0, 36.0), (-36.0, 15.0), (-108.0, 0.0)),
        ((-108.0, 0.0), (-36.0, -15.0), (-15.0, -36.0), (0.0, -108.0)),
    ]
    pts: list[tuple[float, float]] = []
    for p0, c1, c2, p1 in segs:
        for i in range(samples):
            t = i / samples
            mt = 1 - t
            x = mt**3 * p0[0] + 3 * mt**2 * t * c1[0] + 3 * mt * t**2 * c2[0] + t**3 * p1[0]
            y = mt**3 * p0[1] + 3 * mt**2 * t * c1[1] + 3 * mt * t**2 * c2[1] + t**3 * p1[1]
            pts.append((cx + x * scale, cy + y * scale))
    return pts


def _point_in_polygon(x: float, y: float, poly: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(poly) - 1
    for i, (xi, yi) in enumerate(poly):
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def _lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))  # type: ignore[return-value]


def _badge_gradient(t: float) -> tuple[int, int, int]:
    sky_light, sky, indigo = (56, 189, 248), (14, 165, 233), (99, 102, 241)
    if t < 0.55:
        return _lerp(sky_light, sky, t / 0.55)
    return _lerp(sky, indigo, (t - 0.55) / 0.45)


def _blend(dst: bytearray, index: int, color: tuple[int, int, int], alpha: float) -> None:
    if alpha <= 0:
        return
    for i in range(3):
        dst[index + i] = int(dst[index + i] * (1 - alpha) + color[i] * alpha)


def _inside_rounded(x: float, y: float, x0: float, y0: float, x1: float, y1: float, r: float) -> bool:
    if x < x0 or x > x1 or y < y0 or y > y1:
        return False
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    dx, dy = x - cx, y - cy
    return dx * dx + dy * dy <= r * r


def make_png(path: Path, size: int = 512) -> None:
    """Write the brand logo PNG using only the standard library.

    Composition mirrors logo.svg: gradient badge, orbit ring, concave sparkle,
    orbit nodes, and a core dot. The SVG stays the editable master.
    """
    try:
        import cairosvg  # type: ignore

        svg = (path.with_suffix(".svg")).read_text(encoding="utf-8")
        cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=str(path), output_width=size, output_height=size)
        return
    except Exception:
        pass

    width = height = size
    s = size / 512.0
    center = (256 * s, 262 * s)
    a, b = 152 * s, 56 * s
    import math

    theta = math.radians(-18)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    star = _star_points(center[0], center[1], s)
    star_box = (
        min(p[0] for p in star) - 2,
        min(p[1] for p in star) - 2,
        max(p[0] for p in star) + 2,
        max(p[1] for p in star) + 2,
    )
    star_ys = (star_box[1], star_box[3])
    nodes = [
        (center[0] + a * cos_t, center[1] + a * sin_t, 17 * s, 1.0),
        (center[0] - a * cos_t, center[1] - a * sin_t, 11 * s, 0.85),
    ]

    rows: list[bytearray] = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            index = 1 + 4 * x
            px, py = x + 0.5, y + 0.5
            if not _inside_rounded(px, py, 40 * s, 40 * s, 472 * s, 472 * s, 104 * s):
                row.extend((0, 0, 0, 0))
                continue
            t = ((px - 40 * s) + (py - 40 * s)) / (864 * s)
            color = _badge_gradient(t)
            row.extend(color)
            row.append(255)
            glow = max(0.0, 1.0 - math.dist((px, py), (170 * s, 150 * s)) / (560 * s))
            _blend(row, index, (255, 255, 255), 0.22 * glow)
            if _inside_rounded(px, py, 54 * s, 54 * s, 458 * s, 458 * s, 92 * s) and not _inside_rounded(
                px, py, 63 * s, 63 * s, 449 * s, 449 * s, 83 * s
            ):
                _blend(row, index, (255, 255, 255), 0.22)
            ex, ey = px - center[0], py - center[1]
            ux = ex * cos_t - ey * sin_t
            uy = ex * sin_t + ey * cos_t
            v = math.hypot(ux / a, uy / b)
            r_mean = (a + b) / 2
            if abs(v - 1) * r_mean <= 13 * s:
                _blend(row, index, (255, 255, 255), 0.55)
            if abs(v - 1) * r_mean <= 6 * s:
                _blend(row, index, (255, 255, 255), 0.9)
            if star_box[0] <= px <= star_box[2] and star_box[1] <= py <= star_box[3] and _point_in_polygon(px, py, star):
                grad_t = (py - star_ys[0]) / max(1e-6, star_ys[1] - star_ys[0])
                _blend(row, index, _lerp((255, 255, 255), (219, 234, 254), grad_t), 1.0)
            for nx, ny, nr, na in nodes:
                if math.hypot(px - nx, py - ny) <= nr:
                    _blend(row, index, (255, 255, 255), na)
            dist_core = math.hypot(px - center[0], py - center[1])
            if dist_core <= 24 * s:
                _blend(row, index, (14, 165, 233), 1.0)
            if abs(dist_core - 27.5 * s) <= 3.5 * s:
                _blend(row, index, (255, 255, 255), 1.0)
        rows.append(row)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    raw = b"".join(bytes(row) for row in rows)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def make_og_png(path: Path, width: int = 1200, height: int = 630) -> None:
    """Write a 1200x630 social-share image: gradient backdrop, brand badge,
    and a soft product-card silhouette. Standard library only."""
    import math

    rows: list[bytearray] = []
    badge_c = (330.0, 315.0)
    badge_r = 150.0
    a, b = 112.0, 42.0
    theta = math.radians(-18)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    star = _star_points(badge_c[0], badge_c[1], 0.62)
    star_box = (
        min(p[0] for p in star) - 2,
        min(p[1] for p in star) - 2,
        max(p[0] for p in star) + 2,
        max(p[1] for p in star) + 2,
    )
    card = (560.0, 110.0, 1140.0, 520.0, 36.0)
    bars = [
        (600.0, 160.0, 200.0, 34.0, (14, 165, 233), 1.0),
        (600.0, 226.0, 420.0, 26.0, (203, 213, 225), 1.0),
        (600.0, 280.0, 340.0, 26.0, (226, 232, 240), 1.0),
        (600.0, 334.0, 460.0, 26.0, (226, 232, 240), 1.0),
        (600.0, 388.0, 260.0, 26.0, (203, 213, 225), 1.0),
    ]
    r_mean = (a + b) / 2

    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            index = 1 + 3 * x
            px, py = x + 0.5, y + 0.5
            t = (px / width + py / height) / 2
            row.extend(_badge_gradient(t))
            dist = math.hypot(px - badge_c[0], py - badge_c[1])
            if dist <= badge_r:
                bt = 0.9 * (0.5 + ((px - badge_c[0]) + (py - badge_c[1])) / (4 * badge_r))
                bt = max(0.0, min(1.0, bt))
                _blend(row, index, _badge_gradient(bt), 1.0)
                ex, ey = px - badge_c[0], py - badge_c[1]
                ux = ex * cos_t - ey * sin_t
                uy = ex * sin_t + ey * cos_t
                v = math.hypot(ux / a, uy / b)
                if abs(v - 1) * r_mean <= 5.0:
                    _blend(row, index, (255, 255, 255), 0.85)
                if star_box[0] <= px <= star_box[2] and star_box[1] <= py <= star_box[3] and _point_in_polygon(px, py, star):
                    _blend(row, index, (255, 255, 255), 1.0)
                dist_core = math.hypot(px - badge_c[0], py - badge_c[1])
                if dist_core <= 13.0:
                    _blend(row, index, (14, 165, 233), 1.0)
                if abs(dist_core - 16.0) <= 2.4:
                    _blend(row, index, (255, 255, 255), 1.0)
            if dist <= badge_r + 10 and dist > badge_r:
                _blend(row, index, (255, 255, 255), 0.12)
            x0, y0, x1, y1, rad = card
            if _inside_rounded(px, py, x0, y0, x1, y1, rad):
                _blend(row, index, (255, 255, 255), 0.93)
                for bx0, by0, bw, bh, bcolor, balpha in bars:
                    if _inside_rounded(px, py, bx0, by0, bx0 + bw, by0 + bh, bh / 2):
                        _blend(row, index, bcolor, balpha)
        rows.append(row)

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    raw = b"".join(bytes(row) for row in rows)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def load_derive(product_path: Path, highlights_path: Path) -> None:
    spec = importlib.util.spec_from_file_location("lucas_normalize_data", HERE / "normalize_data.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load normalize_data.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = module.load_json(product_path)
    module.validate(data)
    result = module.derive(data, 3, 6)
    highlights_path.parent.mkdir(parents=True, exist_ok=True)
    highlights_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


PACKAGE_JSON = """{
  "name": "__SLUG__",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "check": "astro check"
  },
  "dependencies": {
    "astro": "^5.0.0",
    "tailwindcss": "^4.0.0",
    "@tailwindcss/vite": "^4.0.0"
  },
  "devDependencies": {
    "@playwright/test": "^1.48.0",
    "typescript": "^5.6.0"
  }
}
"""

ASTRO_CONFIG = """import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  site: '__SITE__',
  base: '__BASE__',
  output: 'static',
  vite: { plugins: [tailwindcss()] },
  i18n: {
    defaultLocale: 'zh',
    locales: ['zh', 'en'],
    routing: { prefixDefaultLocale: false },
  },
  build: { inlineStylesheets: 'auto' },
});
"""

TAILWIND_CONFIG = """/* Tailwind v4 is configured CSS-first in src/styles/global.css
   (@import 'tailwindcss', @custom-variant dark, @theme).
   This file only documents the mapping for future editors. */
export const theme = {
  darkVariant: '[data-theme="dark"]',
  brandColor: 'rgb(var(--brand) / <alpha-value>)',
};
"""

GLOBAL_CSS = """@import './tokens.css';
@import 'tailwindcss';

@custom-variant dark ([data-theme="dark"] &);

@theme {
  --color-bg: rgb(var(--bg));
  --color-surface: rgb(var(--surface));
  --color-mutedsurface: rgb(var(--surface-muted));
  --color-fg: rgb(var(--fg));
  --color-muted: rgb(var(--muted));
  --color-brand: rgb(var(--brand));
  --color-brand-strong: rgb(var(--brand-strong));
  --font-sans: Inter, 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  --breakpoint-sm: 40rem;
  --breakpoint-md: 48rem;
  --breakpoint-lg: 64rem;
  --breakpoint-xl: 80rem;
}

:root { font-family: var(--font-sans); background: rgb(var(--bg)); color: rgb(var(--fg)); }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
body { margin: 0; min-height: 100vh; background: rgb(var(--bg)); color: rgb(var(--fg)); line-height: 1.65; -webkit-font-smoothing: antialiased; }
a { color: inherit; text-decoration: none; }
img { max-width: 100%; height: auto; display: block; }
::selection { background: rgb(var(--brand) / 0.25); }
.site-shell { width: min(calc(100% - 3rem), var(--max-width)); margin: 0 auto; }

.site-header { position: sticky; top: 0; z-index: 30; border-bottom: 1px solid rgb(var(--border)); background: rgb(var(--bg) / 0.85); backdrop-filter: blur(14px); }
.header-inner { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; min-height: 4.25rem; }
.brand { display: inline-flex; align-items: center; gap: 0.6rem; font-weight: 750; letter-spacing: -0.02em; }
.brand img { width: 2.1rem; height: 2.1rem; border-radius: 0.6rem; }
.nav { display: flex; align-items: center; gap: 1.35rem; font-size: 0.9rem; color: rgb(var(--muted)); }
.nav a { transition: color 150ms ease; }
.nav a:hover { color: rgb(var(--fg)); }
.nav-actions { display: flex; align-items: center; gap: 0.55rem; }
.pill { display: inline-flex; align-items: center; justify-content: center; min-height: 2.25rem; padding: 0 0.85rem; border: 1px solid rgb(var(--border)); border-radius: 999px; background: rgb(var(--surface)); font-size: 0.85rem; cursor: pointer; transition: border-color 150ms ease; }
.pill:hover { border-color: rgb(var(--brand)); }
main { display: block; }

.hero { position: relative; padding: clamp(4.5rem, 9vw, 7.5rem) 0 4rem; overflow: hidden; }
.hero::before { content: ""; position: absolute; inset: 0; background: radial-gradient(640px 340px at 10% -6%, rgb(var(--brand) / 0.16), transparent 62%), radial-gradient(760px 400px at 96% 6%, rgb(var(--brand-2) / 0.14), transparent 58%); pointer-events: none; }
.hero::after { content: ""; position: absolute; inset: 0; background-image: linear-gradient(rgb(var(--fg) / 0.05) 1px, transparent 1px), linear-gradient(90deg, rgb(var(--fg) / 0.05) 1px, transparent 1px); background-size: 42px 42px; -webkit-mask-image: radial-gradient(760px 440px at 28% -2%, #000 25%, transparent 72%); mask-image: radial-gradient(760px 440px at 28% -2%, #000 25%, transparent 72%); pointer-events: none; }
.hero-grid { position: relative; display: grid; grid-template-columns: minmax(0, 1.02fr) minmax(0, 0.98fr); gap: clamp(2.5rem, 5vw, 4.5rem); align-items: center; }
.hero-grid > * { position: relative; z-index: 1; }
.eyebrow { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.4rem 0.95rem; border: 1px solid rgb(var(--brand) / 0.35); border-radius: 999px; background: rgb(var(--brand) / 0.08); color: rgb(var(--brand-strong)); font-size: 0.8rem; font-weight: 650; letter-spacing: 0.08em; text-transform: uppercase; }
.eyebrow::before { content: ""; width: 0.5rem; height: 0.5rem; border-radius: 999px; background: rgb(var(--brand)); box-shadow: 0 0 0 4px rgb(var(--brand) / 0.18); }
h1 { font-size: clamp(2.7rem, 6vw, 4.3rem); line-height: 1.06; letter-spacing: -0.045em; margin: 1.4rem 0 1.1rem; max-width: 18ch; }
.grad-text { background: linear-gradient(92deg, rgb(var(--fg)) 0%, rgb(var(--fg)) 35%, rgb(var(--brand)) 68%, rgb(var(--brand-2)) 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
h2 { font-size: clamp(1.9rem, 3vw, 2.6rem); line-height: 1.16; letter-spacing: -0.032em; margin: 0 0 0.7rem; }
h3 { font-size: 1.08rem; line-height: 1.35; margin: 0 0 0.5rem; }
.lede { font-size: clamp(1.05rem, 1.7vw, 1.22rem); color: rgb(var(--muted)); max-width: 54ch; }
.cta-row { display: flex; flex-wrap: wrap; gap: 0.8rem; margin-top: 2.1rem; }
.cta-row.center { justify-content: center; }
.button { display: inline-flex; align-items: center; justify-content: center; min-height: 3rem; padding: 0 1.4rem; border-radius: var(--radius-sm); font-weight: 650; font-size: 0.95rem; transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease; }
.button:hover { transform: translateY(-1px); }
.button-primary { background: linear-gradient(135deg, rgb(var(--brand)), rgb(var(--brand-2))); color: #fff; box-shadow: 0 10px 24px rgb(var(--brand) / 0.32); }
.button-primary:hover { box-shadow: 0 14px 30px rgb(var(--brand) / 0.4); }
.button-secondary { border: 1px solid rgb(var(--border)); background: rgb(var(--surface)); }
.button-secondary:hover { border-color: rgb(var(--brand)); }
.button-invert { background: #fff; color: rgb(var(--brand-strong)); box-shadow: 0 12px 28px rgb(0 0 0 / 0.22); }
.hero-meta { display: flex; flex-wrap: wrap; gap: 0.55rem; margin-top: 1.9rem; }
.meta-chip { display: inline-flex; align-items: center; gap: 0.45rem; padding: 0.42rem 0.85rem; border: 1px solid rgb(var(--border)); border-radius: 999px; background: rgb(var(--surface) / 0.7); color: rgb(var(--muted)); font-size: 0.8rem; }
.meta-chip::before { content: ""; width: 0.42rem; height: 0.42rem; border-radius: 999px; background: rgb(var(--success)); }

.window { border: 1px solid rgb(var(--border)); border-radius: var(--radius-lg); background: rgb(var(--surface)); box-shadow: var(--shadow-md), 0 40px 80px rgb(var(--brand) / 0.10); overflow: hidden; }
.window-bar { display: flex; align-items: center; gap: 0.9rem; padding: 0.7rem 1rem; border-bottom: 1px solid rgb(var(--border)); background: rgb(var(--surface-muted)); }
.window-dots { display: inline-flex; gap: 0.42rem; }
.window-dots i { width: 0.68rem; height: 0.68rem; border-radius: 999px; background: rgb(var(--border)); }
.window-dots i:nth-child(1) { background: #f87171; }
.window-dots i:nth-child(2) { background: #fbbf24; }
.window-dots i:nth-child(3) { background: #34d399; }
.window-url { flex: 1; max-width: 26rem; margin-inline: auto; padding: 0.32rem 0.9rem; border: 1px solid rgb(var(--border)); border-radius: 999px; background: rgb(var(--bg)); color: rgb(var(--muted)); font-size: 0.76rem; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.window-tabs { display: inline-flex; gap: 0.3rem; }
.window-tab { border: 1px solid rgb(var(--border)); border-radius: 999px; min-width: 2rem; min-height: 1.6rem; padding: 0 0.5rem; background: transparent; color: rgb(var(--muted)); font: inherit; font-size: 0.7rem; cursor: pointer; }
.window-tab[aria-selected="true"] { background: rgb(var(--brand) / 0.12); border-color: rgb(var(--brand) / 0.5); color: rgb(var(--brand-strong)); }
.window-stage { position: relative; aspect-ratio: 16 / 10; background: rgb(var(--surface-muted)); }
.preview-image { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity 200ms ease; }
.preview-image.active { opacity: 1; }

.section { padding: clamp(3.8rem, 7vw, 6.2rem) 0; }
.section-muted { position: relative; background: rgb(var(--surface-muted)); border-block: 1px solid rgb(var(--border)); }
.section-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 1.5rem; margin-bottom: 2.4rem; }
.section-note { color: rgb(var(--muted)); font-size: 0.92rem; max-width: 52ch; }
.kicker { display: inline-flex; align-items: center; gap: 0.5rem; color: rgb(var(--brand-strong)); font-size: 0.78rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 0.7rem; }
.kicker::before { content: ""; width: 1.1rem; height: 2px; border-radius: 2px; background: linear-gradient(90deg, rgb(var(--brand)), rgb(var(--brand-2))); }
.link-arrow { color: rgb(var(--brand-strong)); font-size: 0.88rem; font-weight: 600; white-space: nowrap; }
.link-arrow:hover { text-decoration: underline; text-underline-offset: 4px; }
.grid { display: grid; gap: 1.1rem; }
.grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }

.card { position: relative; border: 1px solid rgb(var(--border)); border-radius: var(--radius-md); background: rgb(var(--surface)); padding: 1.6rem; box-shadow: var(--shadow-sm); transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease; }
.card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: rgb(var(--brand) / 0.4); }
.metric-card::before { content: ""; position: absolute; inset: 0 0 auto 0; height: 3px; border-radius: 999px; background: linear-gradient(90deg, rgb(var(--brand)), rgb(var(--brand-2))); opacity: 0; transition: opacity 180ms ease; }
.metric-card:hover::before { opacity: 1; }
.metric-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.metric-icon { display: inline-flex; align-items: center; justify-content: center; width: 2.3rem; height: 2.3rem; border-radius: 0.7rem; background: rgb(var(--brand) / 0.1); color: rgb(var(--brand-strong)); }
.metric-period { color: rgb(var(--muted)); font-size: 0.78rem; font-variant-numeric: tabular-nums; }
.metric-label { color: rgb(var(--muted)); font-weight: 600; font-size: 0.92rem; }
.metric-value { font-size: 2.4rem; font-weight: 770; letter-spacing: -0.045em; line-height: 1.1; margin: 0.2rem 0 1rem; font-variant-numeric: tabular-nums; }
.metric-unit { font-size: 1rem; font-weight: 600; color: rgb(var(--muted)); margin-left: 0.3rem; letter-spacing: 0; }
.metric-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem 0.9rem; color: rgb(var(--muted)); font-size: 0.8rem; }
.delta-pill { display: inline-flex; align-items: center; padding: 0.22rem 0.6rem; border-radius: 999px; background: rgb(var(--success) / 0.12); color: rgb(var(--success)); font-weight: 600; }
.source-link { color: rgb(var(--brand-strong)); text-decoration: underline; text-decoration-thickness: 1px; text-underline-offset: 3px; }

.news-list { display: grid; gap: 0.9rem; }
.news-card { display: grid; grid-template-columns: 8.2rem minmax(0, 1fr); gap: 1.2rem; align-items: start; padding: 1.3rem 1.4rem; border: 1px solid rgb(var(--border)); border-radius: var(--radius-md); background: rgb(var(--surface)); box-shadow: var(--shadow-sm); transition: border-color 160ms ease, transform 160ms ease; }
.news-card:hover { border-color: rgb(var(--brand) / 0.45); transform: translateY(-2px); }
.date-pill { display: inline-flex; justify-content: center; padding: 0.4rem 0.7rem; border: 1px solid rgb(var(--border)); border-radius: var(--radius-sm); background: rgb(var(--surface-muted)); color: rgb(var(--muted)); font-size: 0.78rem; font-variant-numeric: tabular-nums; white-space: nowrap; }
.news-title { font-weight: 680; font-size: 1.02rem; }
.news-link:hover { color: rgb(var(--brand-strong)); }
.news-summary { color: rgb(var(--muted)); font-size: 0.92rem; margin-top: 0.35rem; }
.news-tags { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.7rem; }
.tag-chip { padding: 0.18rem 0.6rem; border-radius: 999px; background: rgb(var(--brand) / 0.08); border: 1px solid rgb(var(--brand) / 0.25); color: rgb(var(--brand-strong)); font-size: 0.72rem; font-weight: 600; }

.feature-icon { display: inline-flex; align-items: center; justify-content: center; width: 2.6rem; height: 2.6rem; margin-bottom: 1.1rem; border-radius: 0.8rem; background: linear-gradient(135deg, rgb(var(--brand) / 0.14), rgb(var(--brand-2) / 0.14)); color: rgb(var(--brand-strong)); }

.faq { max-width: 52rem; }
.faq details { border-bottom: 1px solid rgb(var(--border)); padding: 1.05rem 0; }
.faq summary { cursor: pointer; font-weight: 650; list-style: none; display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.faq summary::after { content: "+"; color: rgb(var(--brand-strong)); font-size: 1.2rem; }
.faq details[open] summary::after { content: "–"; }
.faq p { color: rgb(var(--muted)); margin-top: 0.6rem; }

.cta-band { position: relative; overflow: hidden; border-radius: var(--radius-lg); padding: clamp(2.8rem, 5vw, 4.2rem) clamp(1.6rem, 4vw, 3.5rem); text-align: center; color: #fff; background: linear-gradient(120deg, rgb(var(--brand)) 0%, rgb(var(--brand-2)) 100%); box-shadow: var(--shadow-md); }
.cta-band::before { content: ""; position: absolute; inset: 0; background-image: radial-gradient(420px 200px at 18% 0%, rgb(255 255 255 / 0.16), transparent 60%), radial-gradient(520px 260px at 92% 100%, rgb(0 0 0 / 0.14), transparent 65%); pointer-events: none; }
.cta-band h2 { position: relative; color: #fff; }
.cta-band .cta-note { position: relative; color: rgb(255 255 255 / 0.82); margin: 0.5rem auto 0; }
.cta-band .cta-row { position: relative; margin-top: 1.8rem; }

.site-footer { border-top: 1px solid rgb(var(--border)); padding: 3rem 0 2.4rem; color: rgb(var(--muted)); font-size: 0.85rem; }
.footer-grid { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) minmax(0, 1fr); gap: 2rem; }
.footer-brand p { margin: 0.8rem 0 0; max-width: 34ch; }
.footer-head { font-weight: 700; color: rgb(var(--fg)); font-size: 0.82rem; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.8rem; }
.footer-col a { display: block; padding: 0.22rem 0; }
.footer-col a:hover { color: rgb(var(--fg)); }
.footer-meta { text-align: right; }

.table-tools { display: flex; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1rem; }
.table-tools input { min-width: min(100%, 22rem); padding: 0.7rem 0.9rem; border: 1px solid rgb(var(--border)); border-radius: var(--radius-sm); background: rgb(var(--surface)); color: rgb(var(--fg)); font: inherit; }
.table-wrap { overflow-x: auto; border: 1px solid rgb(var(--border)); border-radius: var(--radius-md); background: rgb(var(--surface)); }
table { width: 100%; border-collapse: collapse; min-width: 46rem; }
th, td { text-align: left; padding: 0.9rem 1rem; border-bottom: 1px solid rgb(var(--border)); font-size: 0.9rem; vertical-align: top; }
th { background: rgb(var(--surface-muted)); font-size: 0.78rem; letter-spacing: 0.04em; text-transform: uppercase; color: rgb(var(--muted)); }
tbody tr:last-child td { border-bottom: 0; }

[data-reveal] { opacity: 0; transform: translateY(12px); transition: opacity 500ms ease, transform 500ms ease; transition-delay: var(--delay, 0ms); }
[data-reveal].is-visible { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { [data-reveal] { opacity: 1; transform: none; transition: none; } .card:hover, .news-card:hover, .button:hover { transform: none; } }
@media (max-width: 900px) {
  .hero-grid, .grid-3, .grid-2, .footer-grid { grid-template-columns: 1fr; }
  .section-head { align-items: flex-start; flex-direction: column; }
  .nav { display: none; }
  .footer-meta { text-align: left; }
}
@media (max-width: 600px) {
  .site-shell { width: min(calc(100% - 2rem), var(--max-width)); }
  .news-card { grid-template-columns: 1fr; gap: 0.5rem; }
  .window-url { display: none; }
}
"""

UI_TS = """export type Locale = 'zh' | 'en';

export const ui = {
  zh: {
    nav: { home: '首页', data: '数据', about: '关于', theme: '切换主题', language: 'EN' },
    heroEyebrow: '产品事实，一处讲清',
    heroAction: '查看完整数据',
    heroSecondary: '了解产品',
    metricsTitle: '核心指标',
    metricsNote: '数据来自产品数据文件，点击来源可核验。',
    kickerMetrics: '指标',
    kickerLatest: '动态',
    kickerFeatures: '能力',
    viewAll: '查看全部数据',
    metaMetrics: '项核心指标',
    metaUpdated: '最近更新',
    metaVerified: '来源可核验',
    ctaTitle: '让每个数字都可追溯',
    ctaNote: '完整数据、统计口径与来源链接都在数据页公开。',
    latestTitle: '最新动态',
    latestNote: '自动取最近更新的三条记录。',
    featuresTitle: '为什么选择它',
    previewTitle: '产品预览',
    faqTitle: '常见问题',
    dataTitle: '产品数据',
    dataNote: '完整指标、统计周期与来源链接。',
    searchPlaceholder: '搜索指标或来源',
    aboutTitle: '关于我们',
    productStory: '关于产品',
    author: '关于作者',
    disclaimer: '免责声明',
    updated: '更新日期',
    source: '来源',
    period: '周期',
    empty: '没有匹配的数据，请调整搜索词。',
  },
  en: {
    nav: { home: 'Home', data: 'Data', about: 'About', theme: 'Toggle theme', language: '中文' },
    heroEyebrow: 'Product facts, clearly in one place',
    heroAction: 'View full data',
    heroSecondary: 'About the product',
    metricsTitle: 'Key metrics',
    metricsNote: 'Metrics come from the product data file; follow each source to verify.',
    kickerMetrics: 'Metrics',
    kickerLatest: 'Updates',
    kickerFeatures: 'Capabilities',
    viewAll: 'View all data',
    metaMetrics: 'key metrics',
    metaUpdated: 'Last update',
    metaVerified: 'Verifiable sources',
    ctaTitle: 'Make every number traceable',
    ctaNote: 'Full data, methodology, and source links are public on the data page.',
    latestTitle: 'Latest updates',
    latestNote: 'The three most recent records are derived automatically.',
    featuresTitle: 'Why it works',
    previewTitle: 'Product preview',
    faqTitle: 'Frequently asked questions',
    dataTitle: 'Product data',
    dataNote: 'Full metrics, periods, and source links.',
    searchPlaceholder: 'Search metrics or sources',
    aboutTitle: 'About us',
    productStory: 'About the product',
    author: 'About the author',
    disclaimer: 'Disclaimer',
    updated: 'Updated',
    source: 'Source',
    period: 'Period',
    empty: 'No matching data. Try another search.',
  },
} as const;
"""

BASE_LAYOUT = """---
import '../styles/global.css';
import { ui, type Locale } from '../i18n/ui';
import product from '../data/product.json';
import highlights from '../data/highlights.json';

interface Props {
  locale?: Locale;
  title?: string;
  description?: string;
  path?: string;
}

const { locale = 'zh', title, description, path = Astro.url.pathname } = Astro.props;
const t = ui[locale];
const site = (Astro.site?.toString() ?? Astro.url.origin).replace(/\\/$/, '');
const cleanPath = path.startsWith('/') ? path : `/${path}`;
const canonicalPath = cleanPath === '/' ? '/' : `${cleanPath.replace(/\\/$/, '')}/`;
const canonicalUrl = `${site}${canonicalPath}`;
const basePath = locale === 'en' ? (cleanPath.replace(/^\\/en/, '') || '/') : cleanPath;
const zhUrl = `${site}${basePath === '/' ? '/' : basePath.replace(/\\/$/, '') + '/'}`;
const enSuffix = basePath === '/' ? '' : basePath.replace(/\\/$/, '');
const enUrl = `${site}/en${enSuffix}/`;
const pageTitle = title ?? `${product.product.name} — ${product.product.tagline[locale]}`;
const pageDescription = description ?? product.product.summary[locale];
const lastUpdated = highlights.latest?.[0]?.date;
const navHref = (suffix: string) => (locale === 'en' ? `/en${suffix}` : suffix);
const structuredData = [
  {
    '@context': 'https://schema.org',
    '@type': 'SoftwareApplication',
    name: product.product.name,
    description: product.product.summary[locale],
    url: canonicalUrl,
    applicationCategory: product.product.category || 'DeveloperApplication',
    author: { '@type': 'Organization', name: product.author.name },
  },
  ...(product.faq.length
    ? [{ '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: product.faq.map((item: any) => ({
        '@type': 'Question', name: item.question[locale], acceptedAnswer: { '@type': 'Answer', text: item.answer[locale] },
      })) }]
    : []),
];
---

<!doctype html>
<html lang={locale === 'zh' ? 'zh-CN' : 'en'}>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{pageTitle}</title>
    <meta name="description" content={pageDescription} />
    <link rel="canonical" href={canonicalUrl} />
    <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
    <link rel="alternate" hreflang="zh-CN" href={zhUrl} />
    <link rel="alternate" hreflang="en" href={enUrl} />
    <link rel="alternate" hreflang="x-default" href={zhUrl} />
    <meta property="og:type" content="website" />
    <meta property="og:title" content={pageTitle} />
    <meta property="og:description" content={pageDescription} />
    <meta property="og:url" content={canonicalUrl} />
    <meta property="og:image" content={`${site}/og-image.png`} />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content={pageTitle} />
    <meta name="twitter:description" content={pageDescription} />
    <script is:inline>
      (function () {
        try {
          var forced = new URLSearchParams(location.search).get('theme');
          var stored = localStorage.getItem('theme');
          var theme = (forced === 'light' || forced === 'dark') ? forced
            : (stored === 'light' || stored === 'dark') ? stored
            : (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
          document.documentElement.setAttribute('data-theme', theme);
        } catch (error) {
          document.documentElement.setAttribute('data-theme', 'light');
        }
      })();
    </script>
    <script type="application/ld+json" set:html={JSON.stringify(structuredData)} />
  </head>
  <body>
    <header class="site-header">
      <div class="site-shell header-inner">
        <a class="brand" href={navHref('/')} aria-label={product.product.name}>
          <img src="/logo.svg" alt="" width="32" height="32" />
          <span>{product.product.name}</span>
        </a>
        <nav class="nav" aria-label={locale === 'zh' ? '主导航' : 'Main navigation'}>
          <a href={navHref('/')}>{t.nav.home}</a>
          <a href={navHref('/data/')}>{t.nav.data}</a>
          <a href={navHref('/about/')}>{t.nav.about}</a>
        </nav>
        <div class="nav-actions">
          <button id="theme-toggle" class="pill" type="button" aria-label={t.nav.theme}>◐</button>
          <a class="pill" href={locale === 'zh' ? enUrl : zhUrl} hreflang={locale === 'zh' ? 'en' : 'zh-CN'}>{t.nav.language}</a>
        </div>
      </div>
    </header>
    <main><slot /></main>
    <footer class="site-footer">
      <div class="site-shell footer-grid">
        <div class="footer-brand">
          <a class="brand" href={navHref('/')}>
            <img src="/logo.svg" alt="" width="30" height="30" />
            <span>{product.product.name}</span>
          </a>
          <p>{product.product.tagline[locale]}</p>
        </div>
        <div class="footer-col">
          <p class="footer-head">{locale === 'zh' ? '页面' : 'Pages'}</p>
          <a href={navHref('/')}>{t.nav.home}</a>
          <a href={navHref('/data/')}>{t.nav.data}</a>
          <a href={navHref('/about/')}>{t.nav.about}</a>
        </div>
        <div class="footer-col footer-meta">
          <p class="footer-head">{t.updated}</p>
          <p>{lastUpdated ?? '—'}</p>
          <p><a href="/llms.txt">llms.txt</a> · <a href="/sitemap.xml">sitemap.xml</a></p>
        </div>
      </div>
    </footer>
    <script>
      const toggle = document.getElementById('theme-toggle');
      toggle?.addEventListener('click', () => {
        const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        try { localStorage.setItem('theme', next); } catch (error) {}
      });
      const revealItems = document.querySelectorAll('[data-reveal]');
      if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        const observer = new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); }
          });
        }, { threshold: 0.12 });
        revealItems.forEach((item) => observer.observe(item));
      } else {
        revealItems.forEach((item) => item.classList.add('is-visible'));
      }
    </script>
  </body>
</html>
"""

THEME_TOGGLE = """---
interface Props { label?: string }
const { label = 'Toggle theme' } = Astro.props;
---
<button class="pill" type="button" data-theme-toggle aria-label={label}>◐</button>
<script>
  document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
    button.addEventListener('click', () => {
      const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (error) {}
    });
  });
</script>
"""

METRIC_CARD = """---
import type { Locale } from '../i18n/ui';
interface Props { metric: any; locale: Locale; index?: number }
const { metric, locale, index = 0 } = Astro.props;
const sourceLabel = locale === 'zh' ? '来源' : 'Source';
---
<article class="card metric-card" data-reveal style={`--delay:${index * 70}ms`}>
  <div class="metric-top">
    <span class="metric-icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l2.4 7.6L22 12l-7.6 2.4L12 22l-2.4-7.6L2 12l7.6-2.4z" /></svg>
    </span>
    <span class="metric-period">{metric.period}</span>
  </div>
  <h3 class="metric-label">{metric.label[locale]}</h3>
  <p class="metric-value">{metric.value}<span class="metric-unit">{metric.unit ?? ''}</span></p>
  <div class="metric-meta">
    {metric.delta && <span class="delta-pill">{metric.delta}</span>}
    {metric.source && <a class="source-link" href={metric.source} rel="noopener noreferrer" target="_blank">{sourceLabel}</a>}
  </div>
</article>
"""

LATEST_STRIP = """---
import type { Locale } from '../i18n/ui';
import { ui } from '../i18n/ui';
interface Props { updates: any[]; locale: Locale }
const { updates, locale } = Astro.props;
const t = ui[locale];
const formatDate = (value: string) => locale === 'zh'
  ? value.replace(/^(\\d{4})-(\\d{2})-(\\d{2})$/, '$1年$2月$3日')
  : new Date(`${value}T00:00:00Z`).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' });
---
<div class="news-list">
  {updates.length === 0 && <p class="section-note">{t.empty}</p>}
  {updates.map((item) => (
    <article class="news-card" data-reveal>
      <time class="date-pill" datetime={item.date}>{formatDate(item.date)}</time>
      <div>
        <p class="news-title">{item.url ? <a class="news-link" href={item.url}>{item.title[locale]} <span aria-hidden="true">→</span></a> : item.title[locale]}</p>
        <p class="news-summary">{item.summary[locale]}</p>
        {item.tags?.length > 0 && <div class="news-tags">{item.tags.map((tag: string) => <span class="tag-chip">{tag}</span>)}</div>}
      </div>
    </article>
  ))}
</div>
"""

PRODUCT_PREVIEW = """---
import type { Locale } from '../i18n/ui';
import { ui } from '../i18n/ui';
interface Props { gallery: any[]; locale: Locale }
const { gallery, locale } = Astro.props;
const t = ui[locale];
const items = gallery.length ? gallery : [{ src: '/images/product-preview.svg', alt: { zh: '产品界面预览示意图', en: 'Illustrative product interface preview' }, caption: { zh: '示例界面：请替换为真实产品截图。', en: 'Illustrative UI: replace with a real product screenshot.' } }];
const urlLabel = locale === 'en' ? 'product · preview' : '产品 · 预览';
---
<div class="window" data-preview data-reveal>
  <div class="window-bar">
    <span class="window-dots" aria-hidden="true"><i></i><i></i><i></i></span>
    <span class="window-url">{urlLabel}</span>
    <div class="window-tabs" role="tablist" aria-label={t.previewTitle}>
      {items.map((item, index) => (
        <button class="window-tab" type="button" role="tab" aria-selected={index === 0} aria-label={`${index + 1}`} data-preview-tab={index}>
          {String(index + 1).padStart(2, '0')}
        </button>
      ))}
    </div>
  </div>
  <div class="window-stage">
    {items.map((item, index) => (
      <img
        class:list={['preview-image', { active: index === 0 }]}
        src={item.src}
        alt={item.alt?.[locale] ?? ''}
        loading={index === 0 ? 'eager' : 'lazy'}
        decoding="async"
        width="1200"
        height="750"
        data-preview-image={index}
      />
    ))}
  </div>
</div>
<script>
  const root = document.querySelector('[data-preview]');
  if (root) {
    const tabs = root.querySelectorAll<HTMLButtonElement>('[data-preview-tab]');
    const images = root.querySelectorAll<HTMLImageElement>('[data-preview-image]');
    const activate = (index: number) => {
      tabs.forEach((tab, i) => tab.setAttribute('aria-selected', String(i === index)));
      images.forEach((image, i) => image.classList.toggle('active', i === index));
    };
    tabs.forEach((tab, index) => tab.addEventListener('click', () => activate(index)));
  }
</script>
"""

DATA_TABLE = """---
import type { Locale } from '../i18n/ui';
import { ui } from '../i18n/ui';
interface Props { metrics: any[]; locale: Locale }
const { metrics, locale } = Astro.props;
const t = ui[locale];
---
<div>
  <div class="table-tools">
    <input type="search" data-table-search placeholder={t.searchPlaceholder} aria-label={t.searchPlaceholder} />
  </div>
  <div class="table-wrap">
    <table data-metric-table>
      <thead>
        <tr>
          <th>{locale === 'zh' ? '指标' : 'Metric'}</th>
          <th>{locale === 'zh' ? '数值' : 'Value'}</th>
          <th>{t.period}</th>
          <th>{t.updated}</th>
          <th>{t.source}</th>
        </tr>
      </thead>
      <tbody>
        {metrics.map((metric) => (
          <tr>
            <td>{metric.label[locale]}</td>
            <td><strong>{metric.value}{metric.unit ?? ''}</strong></td>
            <td>{metric.period}</td>
            <td>{metric.date ?? metric.period}</td>
            <td>{metric.source ? <a class="source-link" href={metric.source} target="_blank" rel="noopener noreferrer">{t.source}</a> : '—'}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
  <p class="section-note" data-table-empty hidden>{t.empty}</p>
</div>
<script>
  const input = document.querySelector<HTMLInputElement>('[data-table-search]');
  const table = document.querySelector<HTMLTableElement>('[data-metric-table]');
  const empty = document.querySelector<HTMLElement>('[data-table-empty]');
  input?.addEventListener('input', () => {
    const query = input.value.trim().toLowerCase();
    let visible = 0;
    table?.querySelectorAll<HTMLTableRowElement>('tbody tr').forEach((row) => {
      const match = row.textContent?.toLowerCase().includes(query) ?? false;
      row.hidden = !match;
      if (match) visible += 1;
    });
    if (empty) empty.hidden = visible > 0;
  });
</script>
"""

LANDING_CONTENT = """---
import { ui, type Locale } from '../i18n/ui';
import product from '../data/product.json';
import highlights from '../data/highlights.json';
import BaseLayout from '../layouts/BaseLayout.astro';
import MetricCard from '../components/MetricCard.astro';
import LatestStrip from '../components/LatestStrip.astro';
import ProductPreview from '../components/ProductPreview.astro';

interface Props { locale: Locale }
const { locale } = Astro.props;
const t = ui[locale];
const path = locale === 'en' ? '/en/' : '/';
const dataHref = locale === 'en' ? '/en/data/' : '/data/';
const aboutHref = locale === 'en' ? '/en/about/' : '/about/';
const lastUpdate = highlights.latest[0]?.date;
const icons = [
  'M12 3l7 3v5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3zM9 12l2 2 4-4',
  'M13 2 4 14h6l-1 8 9-12h-6l1-8z',
  'M5 20v-8M11 20V6M17 20v-9M3 20h18',
  'M12 3l9 5-9 5-9-5 9-5zM3 14l9 5 9-5',
];
---
<BaseLayout locale={locale} path={path}>
  <section class="hero">
    <div class="site-shell hero-grid">
      <div>
        <span class="eyebrow">{t.heroEyebrow}</span>
        <h1><span class="grad-text">{product.product.tagline[locale]}</span></h1>
        <p class="lede">{product.product.summary[locale]}</p>
        <div class="cta-row">
          <a class="button button-primary" href={dataHref}>{t.heroAction}</a>
          <a class="button button-secondary" href={aboutHref}>{t.heroSecondary}</a>
        </div>
        <div class="hero-meta">
          <span class="meta-chip">{highlights.metrics.length} {t.metaMetrics}</span>
          {lastUpdate && <span class="meta-chip">{t.metaUpdated} · {lastUpdate}</span>}
          <span class="meta-chip">{t.metaVerified}</span>
        </div>
      </div>
      <ProductPreview gallery={highlights.gallery} locale={locale} />
    </div>
  </section>

  <section class="section section-muted" id="metrics">
    <div class="site-shell">
      <div class="section-head">
        <div>
          <span class="kicker">{t.kickerMetrics}</span>
          <h2>{t.metricsTitle}</h2>
          <p class="section-note">{t.metricsNote}</p>
        </div>
        <a class="link-arrow" href={dataHref}>{t.viewAll} →</a>
      </div>
      <div class="grid grid-3">
        {highlights.metrics.map((metric, index) => <MetricCard metric={metric} locale={locale} index={index} />)}
      </div>
    </div>
  </section>

  <section class="section" id="latest">
    <div class="site-shell">
      <div class="section-head">
        <div>
          <span class="kicker">{t.kickerLatest}</span>
          <h2>{t.latestTitle}</h2>
          <p class="section-note">{t.latestNote}</p>
        </div>
        <a class="link-arrow" href={dataHref}>{t.viewAll} →</a>
      </div>
      <LatestStrip updates={highlights.latest} locale={locale} />
    </div>
  </section>

  <section class="section section-muted" id="features">
    <div class="site-shell">
      <div class="section-head">
        <div>
          <span class="kicker">{t.kickerFeatures}</span>
          <h2>{t.featuresTitle}</h2>
        </div>
      </div>
      <div class="grid grid-3">
        {highlights.features.map((feature, index) => (
          <article class="card" data-reveal style={`--delay:${index * 70}ms`}>
            <span class="feature-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d={icons[index % icons.length]} /></svg>
            </span>
            <h3>{feature.title[locale]}</h3>
            <p class="section-note">{feature.description[locale]}</p>
          </article>
        ))}
      </div>
    </div>
  </section>

  {highlights.faq.length > 0 && (
    <section class="section" id="faq">
      <div class="site-shell faq">
        <span class="kicker">FAQ</span>
        <h2>{t.faqTitle}</h2>
        {highlights.faq.map((item) => (
          <details>
            <summary>{item.question[locale]}</summary>
            <p>{item.answer[locale]}</p>
          </details>
        ))}
      </div>
    </section>
  )}

  <section class="section" id="cta">
    <div class="site-shell">
      <div class="cta-band" data-reveal>
        <h2>{t.ctaTitle}</h2>
        <p class="section-note cta-note">{t.ctaNote}</p>
        <div class="cta-row center">
          <a class="button button-invert" href={dataHref}>{t.heroAction}</a>
        </div>
      </div>
    </div>
  </section>
</BaseLayout>
"""

DATA_CONTENT = """---
import { ui, type Locale } from '../i18n/ui';
import product from '../data/product.json';
import { ui as strings } from '../i18n/ui';
import BaseLayout from '../layouts/BaseLayout.astro';
import DataTable from '../components/DataTable.astro';

interface Props { locale: Locale }
const { locale } = Astro.props;
const t = strings[locale];
const path = locale === 'en' ? '/en/data/' : '/data/';
const updated = [...product.updates].sort((a, b) => b.date.localeCompare(a.date))[0]?.date ?? '';
---
<BaseLayout locale={locale} path={path} title={`${t.dataTitle} — ${product.product.name}`} description={t.dataNote}>
  <section class="section">
    <div class="site-shell">
      <span class="eyebrow">{product.product.name}</span>
      <h1>{t.dataTitle}</h1>
      <p class="lede">{t.dataNote}</p>
      <p class="section-note">{t.updated}: <time datetime={updated}>{updated}</time></p>
      <div style="margin-top:2rem">
        <DataTable metrics={product.metrics} locale={locale} />
      </div>
    </div>
  </section>
  <section class="section section-muted">
    <div class="site-shell">
      <h2>{locale === 'zh' ? '数据与口径' : 'Data and methodology'}</h2>
      <div class="grid grid-2" style="margin-top:1.5rem">
        <div class="card">
          <h3>{locale === 'zh' ? '更新机制' : 'Update mechanism'}</h3>
          <p class="section-note">{locale === 'zh' ? '数据页从产品数据文件构建，落地页只读取派生摘要。' : 'The data page is built from the product data file; the landing page reads derived highlights only.'}</p>
        </div>
        <div class="card">
          <h3>{locale === 'zh' ? '来源' : 'Sources'}</h3>
          <p class="section-note">{locale === 'zh' ? '每项指标都保留来源链接，详见上方表格。' : 'Every metric keeps its source link; see the table above.'}</p>
        </div>
      </div>
    </div>
  </section>
</BaseLayout>
"""

ABOUT_CONTENT = """---
import { ui, type Locale } from '../i18n/ui';
import product from '../data/product.json';
import BaseLayout from '../layouts/BaseLayout.astro';

interface Props { locale: Locale }
const { locale } = Astro.props;
const t = ui[locale];
const path = locale === 'en' ? '/en/about/' : '/about/';
---
<BaseLayout locale={locale} path={path} title={`${t.aboutTitle} — ${product.product.name}`} description={product.product.summary[locale]}>
  <section class="section">
    <div class="site-shell">
      <span class="eyebrow">{product.product.name}</span>
      <h1>{t.aboutTitle}</h1>
      <p class="lede">{product.product.summary[locale]}</p>
      <div class="grid grid-2" style="margin-top:2.5rem">
        <article class="card">
          <h2>{t.productStory}</h2>
          <p class="section-note">{product.product.summary[locale]}</p>
        </article>
        <article class="card">
          <h2>{t.author}</h2>
          <p><strong>{product.author.name}</strong> · {product.author.role[locale]}</p>
          <p class="section-note">{product.author.bio[locale]}</p>
          <p>{product.author.links.map((link) => <a class="source-link" href={link.url} target="_blank" rel="noopener noreferrer" style="margin-right:1rem">{link.label}</a>)}</p>
        </article>
      </div>
    </div>
  </section>
  <section class="section section-muted">
    <div class="site-shell">
      <h2>{t.disclaimer}</h2>
      <p class="section-note">{product.disclaimer[locale]}</p>
    </div>
  </section>
</BaseLayout>
"""

PAGE_INDEX = """---
import LandingContent from '../components/LandingContent.astro';
---
<LandingContent locale="__LOCALE__" />
"""

PAGE_SUB = """---
import __COMPONENT__ from '../../components/__COMPONENT__.astro';
---
<__COMPONENT__ locale="__LOCALE__" />
"""

ROBOTS_TS = """export function GET({ site }: { site: URL | undefined }) {
  const base = site?.toString().replace(/\\/$/, '') ?? 'https://example.com';
  const body = `User-agent: *\\nAllow: /\\nSitemap: ${base}/sitemap.xml\\n`;
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}
"""

SITEMAP_TS = """import product from '../data/product.json';

export function GET({ site }: { site: URL | undefined }) {
  const base = (site?.toString() ?? 'https://example.com').replace(/\\/$/, '');
  const paths = ['/', '/data/', '/about/', '/en/', '/en/data/', '/en/about/'];
  const lastmod = [...product.updates].sort((a, b) => b.date.localeCompare(a.date))[0]?.date ?? new Date().toISOString().slice(0, 10);
  const urls = paths.map((path) => `  <url><loc>${base}${path}</loc><lastmod>${lastmod}</lastmod></url>`).join('\\n');
  const body = `<?xml version="1.0" encoding="UTF-8"?>\\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n${urls}\\n</urlset>\\n`;
  return new Response(body, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
"""

LLMS_TS = """import product from '../data/product.json';

export function GET({ site }: { site: URL | undefined }) {
  const base = (site?.toString() ?? 'https://example.com').replace(/\\/$/, '');
  const updated = [...product.updates].sort((a, b) => b.date.localeCompare(a.date))[0]?.date ?? 'unknown';
  const body = [
    `# ${product.product.name}`,
    '',
    `> ${product.product.summary.en}`,
    '',
    `- Audience: ${product.product.category || 'product users'}`,
    `- Latest update: ${updated}`,
    `- Canonical source: ${base}/data/`,
    '',
    '## Pages',
    `- Landing: ${base}/`,
    `- Data: ${base}/data/`,
    `- About: ${base}/about/`,
    `- English: ${base}/en/`,
    '',
    '## Facts',
    ...product.metrics.map((metric) => `- ${metric.label.en}: ${metric.value}${metric.unit ?? ''} (${metric.period})${metric.source ? ` — ${metric.source}` : ''}`),
    '',
  ].join('\\n');
  return new Response(body, { headers: { 'Content-Type': 'text/plain; charset=utf-8' } });
}
"""

NOT_FOUND = """---
import BaseLayout from '../layouts/BaseLayout.astro';
---
<BaseLayout title="404 — Page not found" description="The requested page does not exist.">
  <section class="section">
    <div class="site-shell">
      <h1>404</h1>
      <p class="lede">This page does not exist. <a class="source-link" href="/">Return home</a>.</p>
    </div>
  </section>
</BaseLayout>
"""

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="__NAME__ logo">
  <defs>
    <linearGradient id="badge" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#38bdf8"/>
      <stop offset="0.55" stop-color="#0ea5e9"/>
      <stop offset="1" stop-color="#6366f1"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.32" cy="0.26" r="0.95">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.30"/>
      <stop offset="0.55" stop-color="#ffffff" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="spark" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#dbeafe"/>
    </linearGradient>
  </defs>
  <rect x="40" y="40" width="432" height="432" rx="104" fill="url(#badge)"/>
  <rect x="40" y="40" width="432" height="432" rx="104" fill="url(#glow)"/>
  <rect x="54" y="54" width="404" height="404" rx="92" fill="none" stroke="#ffffff" stroke-opacity="0.22" stroke-width="3"/>
  <g transform="translate(256 262)">
    <g transform="rotate(-18)">
      <ellipse rx="152" ry="56" fill="none" stroke="#ffffff" stroke-opacity="0.55" stroke-width="26"/>
      <ellipse rx="152" ry="56" fill="none" stroke="#ffffff" stroke-opacity="0.9" stroke-width="12"/>
      <circle cx="152" cy="0" r="17" fill="#ffffff"/>
      <circle cx="-152" cy="0" r="11" fill="#ffffff" fill-opacity="0.85"/>
    </g>
    <path d="M0 -108 C 15 -36 36 -15 108 0 C 36 15 15 36 0 108 C -15 36 -36 15 -108 0 C -36 -15 -15 -36 0 -108 Z" fill="url(#spark)"/>
    <circle r="24" fill="#0ea5e9" stroke="#ffffff" stroke-width="7"/>
  </g>
</svg>
"""

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs>
    <linearGradient id="b" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#38bdf8"/>
      <stop offset="1" stop-color="#6366f1"/>
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="15" fill="url(#b)"/>
  <ellipse cx="32" cy="33" rx="20" ry="7.6" fill="none" stroke="#ffffff" stroke-opacity="0.85" stroke-width="2.6" transform="rotate(-18 32 33)"/>
  <path d="M32 12 C 33.7 25.5 35.5 27.3 49 29 C 35.5 30.7 33.7 32.5 32 46 C 30.3 32.5 28.5 30.7 15 29 C 28.5 27.3 30.3 25.5 32 12 Z" fill="#ffffff"/>
  <circle cx="32" cy="29" r="3.4" fill="#0ea5e9" stroke="#ffffff" stroke-width="1.2"/>
</svg>
"""

PREVIEW_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 750">
  <defs>
    <linearGradient id="pbrand" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#38bdf8"/><stop offset="1" stop-color="#6366f1"/>
    </linearGradient>
    <linearGradient id="parea" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#0ea5e9" stop-opacity="0.4"/><stop offset="1" stop-color="#0ea5e9" stop-opacity="0.02"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="750" fill="#f8fafc"/>
  <rect width="250" height="750" fill="#0f172a"/>
  <circle cx="52" cy="60" r="16" fill="url(#pbrand)"/>
  <rect x="80" y="52" width="96" height="16" rx="8" fill="#334155"/>
  <rect x="36" y="130" width="178" height="40" rx="10" fill="#0ea5e9"/>
  <rect x="52" y="144" width="86" height="12" rx="6" fill="#ffffff" opacity="0.92"/>
  <rect x="36" y="186" width="178" height="40" rx="10" fill="#1e293b"/>
  <rect x="52" y="200" width="104" height="12" rx="6" fill="#64748b"/>
  <rect x="36" y="242" width="178" height="40" rx="10" fill="#1e293b"/>
  <rect x="52" y="256" width="76" height="12" rx="6" fill="#64748b"/>
  <rect x="36" y="298" width="178" height="40" rx="10" fill="#1e293b"/>
  <rect x="52" y="312" width="112" height="12" rx="6" fill="#64748b"/>
  <rect x="290" y="50" width="300" height="26" rx="13" fill="#0f172a"/>
  <rect x="760" y="46" width="240" height="34" rx="17" fill="#ffffff" stroke="#e2e8f0" stroke-width="2"/>
  <rect x="782" y="58" width="120" height="10" rx="5" fill="#cbd5e1"/>
  <circle cx="1128" cy="63" r="17" fill="url(#pbrand)"/>
  <rect x="290" y="120" width="280" height="140" rx="16" fill="#ffffff" stroke="#e2e8f0" stroke-width="2"/>
  <rect x="314" y="144" width="90" height="12" rx="6" fill="#94a3b8"/>
  <rect x="314" y="166" width="120" height="26" rx="8" fill="#0f172a"/>
  <rect x="470" y="166" width="58" height="20" rx="10" fill="#dcfce7"/>
  <rect x="314" y="214" width="34" height="22" rx="6" fill="#bae6fd"/>
  <rect x="360" y="204" width="34" height="32" rx="6" fill="#7dd3fc"/>
  <rect x="406" y="212" width="34" height="24" rx="6" fill="#bae6fd"/>
  <rect x="452" y="198" width="34" height="38" rx="6" fill="#0ea5e9"/>
  <rect x="590" y="120" width="280" height="140" rx="16" fill="#ffffff" stroke="#e2e8f0" stroke-width="2"/>
  <rect x="614" y="144" width="110" height="12" rx="6" fill="#94a3b8"/>
  <rect x="614" y="166" width="96" height="26" rx="8" fill="#0f172a"/>
  <rect x="770" y="166" width="58" height="20" rx="10" fill="#dcfce7"/>
  <rect x="614" y="214" width="34" height="26" rx="6" fill="#bae6fd"/>
  <rect x="660" y="206" width="34" height="34" rx="6" fill="#0ea5e9"/>
  <rect x="706" y="216" width="34" height="24" rx="6" fill="#bae6fd"/>
  <rect x="752" y="200" width="34" height="40" rx="6" fill="#7dd3fc"/>
  <rect x="890" y="120" width="280" height="140" rx="16" fill="#ffffff" stroke="#e2e8f0" stroke-width="2"/>
  <rect x="914" y="144" width="100" height="12" rx="6" fill="#94a3b8"/>
  <rect x="914" y="166" width="132" height="26" rx="8" fill="#0f172a"/>
  <rect x="914" y="214" width="34" height="20" rx="6" fill="#bae6fd"/>
  <rect x="960" y="208" width="34" height="26" rx="6" fill="#7dd3fc"/>
  <rect x="1006" y="204" width="34" height="30" rx="6" fill="#0ea5e9"/>
  <rect x="1052" y="212" width="34" height="22" rx="6" fill="#bae6fd"/>
  <rect x="290" y="290" width="560" height="240" rx="16" fill="#ffffff" stroke="#e2e8f0" stroke-width="2"/>
  <rect x="314" y="314" width="140" height="14" rx="7" fill="#94a3b8"/>
  <path d="M314 470 L314 428 C360 418 384 382 434 374 C484 366 506 400 556 390 C606 380 634 344 684 340 C734 336 764 360 826 352 L826 470 Z" fill="url(#parea)"/>
  <path d="M314 428 C360 418 384 382 434 374 C484 366 506 400 556 390 C606 380 634 344 684 340 C734 336 764 360 826 352" fill="none" stroke="#0ea5e9" stroke-width="3" stroke-linecap="round"/>
  <circle cx="434" cy="374" r="5" fill="#ffffff" stroke="#0ea5e9" stroke-width="3"/>
  <circle cx="684" cy="340" r="5" fill="#ffffff" stroke="#0ea5e9" stroke-width="3"/>
  <rect x="870" y="290" width="300" height="240" rx="16" fill="#ffffff" stroke="#e2e8f0" stroke-width="2"/>
  <rect x="894" y="314" width="120" height="14" rx="7" fill="#94a3b8"/>
  <circle cx="908" cy="366" r="12" fill="url(#pbrand)"/>
  <rect x="932" y="356" width="150" height="10" rx="5" fill="#cbd5e1"/>
  <rect x="932" y="372" width="96" height="8" rx="4" fill="#e2e8f0"/>
  <circle cx="908" cy="416" r="12" fill="url(#pbrand)"/>
  <rect x="932" y="406" width="180" height="10" rx="5" fill="#cbd5e1"/>
  <rect x="932" y="422" width="120" height="8" rx="4" fill="#e2e8f0"/>
  <circle cx="908" cy="466" r="12" fill="url(#pbrand)"/>
  <rect x="932" y="456" width="140" height="10" rx="5" fill="#cbd5e1"/>
  <rect x="932" y="472" width="110" height="8" rx="4" fill="#e2e8f0"/>
  <rect x="290" y="550" width="880" height="150" rx="16" fill="#ffffff" stroke="#e2e8f0" stroke-width="2"/>
  <rect x="314" y="574" width="180" height="14" rx="7" fill="#0f172a"/>
  <rect x="314" y="606" width="220" height="10" rx="5" fill="#cbd5e1"/>
  <rect x="314" y="636" width="180" height="10" rx="5" fill="#e2e8f0"/>
  <rect x="314" y="666" width="200" height="10" rx="5" fill="#e2e8f0"/>
  <rect x="600" y="604" width="90" height="20" rx="10" fill="#dcfce7"/>
  <rect x="600" y="640" width="90" height="20" rx="10" fill="#fef9c3"/>
  <rect x="760" y="604" width="70" height="14" rx="7" fill="#0f172a"/>
  <rect x="760" y="640" width="56" height="14" rx="7" fill="#334155"/>
  <rect x="980" y="604" width="160" height="14" rx="7" fill="#e2e8f0"/>
  <rect x="980" y="640" width="130" height="14" rx="7" fill="#e2e8f0"/>
  <text x="1164" y="726" text-anchor="end" font-family="system-ui, sans-serif" font-size="15" fill="#94a3b8">Illustrative preview — replace with a real screenshot</text>
</svg>
"""

HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
/
  Cache-Control: public, max-age=0, must-revalidate
/_astro/*
  Cache-Control: public, max-age=31536000, immutable
/assets/*
  Cache-Control: public, max-age=31536000, immutable
/*.png
  Cache-Control: public, max-age=31536000, immutable
/sitemap.xml
  Cache-Control: public, max-age=3600
/llms.txt
  Cache-Control: public, max-age=3600
"""

GITHUB_WORKFLOW = """name: Deploy static site

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm install
      - run: npm run build
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
"""

VERCEL_JSON = """{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "headers": [
    { "source": "/_astro/(.*)", "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }] },
    { "source": "/(.*)", "headers": [{ "key": "X-Content-Type-Options", "value": "nosniff" }] }
  ]
}
"""

NETLIFY_TOML = """[build]
  command = "npm run build"
  publish = "dist"

[[headers]]
  for = "/_astro/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
"""


def build_files(values: dict[str, str], deploy: str) -> dict[str, str]:
    files: dict[str, str] = {
        "package.json": render(PACKAGE_JSON, values),
        "astro.config.mjs": render(ASTRO_CONFIG, values),
        "tsconfig.json": '{"extends": "astro/tsconfigs/strict", "include": [".astro/types.d.ts", "**/*"], "exclude": ["dist"]}\n',
        "tailwind.config.mjs": TAILWIND_CONFIG,
        ".gitignore": "node_modules/\ndist/\n.astro/\n.DS_Store\n.env\n",
        "src/env.d.ts": '/// <reference types="astro/client" />\n',
        "src/styles/global.css": GLOBAL_CSS,
        "src/i18n/ui.ts": UI_TS,
        "src/layouts/BaseLayout.astro": BASE_LAYOUT,
        "src/components/ThemeToggle.astro": THEME_TOGGLE,
        "src/components/MetricCard.astro": METRIC_CARD,
        "src/components/LatestStrip.astro": LATEST_STRIP,
        "src/components/ProductPreview.astro": PRODUCT_PREVIEW,
        "src/components/DataTable.astro": DATA_TABLE,
        "src/components/LandingContent.astro": LANDING_CONTENT,
        "src/components/DataContent.astro": DATA_CONTENT,
        "src/components/AboutContent.astro": ABOUT_CONTENT,
        "src/pages/index.astro": render(PAGE_INDEX, {"LOCALE": "zh"}),
        "src/pages/en/index.astro": render(PAGE_INDEX, {"LOCALE": "en"}),
        "src/pages/data/index.astro": render(PAGE_SUB, {"COMPONENT": "DataContent", "LOCALE": "zh"}),
        "src/pages/en/data/index.astro": render(PAGE_SUB, {"COMPONENT": "DataContent", "LOCALE": "en"}),
        "src/pages/about/index.astro": render(PAGE_SUB, {"COMPONENT": "AboutContent", "LOCALE": "zh"}),
        "src/pages/en/about/index.astro": render(PAGE_SUB, {"COMPONENT": "AboutContent", "LOCALE": "en"}),
        "src/pages/404.astro": NOT_FOUND,
        "src/pages/robots.txt.ts": ROBOTS_TS,
        "src/pages/sitemap.xml.ts": SITEMAP_TS,
        "src/pages/llms.txt.ts": LLMS_TS,
        "public/logo.svg": render(LOGO_SVG, values),
        "public/favicon.svg": FAVICON_SVG,
        "public/images/product-preview.svg": PREVIEW_SVG,
        "public/_headers": HEADERS,
        "docs/product-overview.md": f"# {values['NAME']} 产品概览\n\n定位：{values['DESCRIPTION']}\n\n受众：待补充。\n\n数据来源：`src/data/product.json`。\n\n部署平台：{deploy}。\n\n未确认事项：待补充。\n",
        "docs/data-sources.md": "# 数据来源\n\n原始来源：待补充。\n\n字段映射：产品事实映射到 `src/data/product.json`，落地页读取 `src/data/highlights.json`。\n\n缺失字段：待补充。\n\n失败回退：构建时使用上次校验通过的快照。\n",
        "docs/ui-decisions.md": "# UI 组件决策\n\n候选来源：待补充，至少 3 个可核验链接。\n\n结论：默认使用 Astro + Tailwind 原生组件，复杂交互按需引入。\n\n代价：复杂图表需要后续单独调研。\n",
        "docs/seo-geo.md": "# SEO 与 GEO\n\n已生成 canonical、hreflang、OG、sitemap、robots、JSON-LD 与 `llms.txt`。\n\n实测性能数据：待补充。\n\nGEO 说明：产品定义、指标、时间与来源均使用可抓取文本。\n",
        "docs/screenshots.md": "# 页面预览\n\n截图待生成。启动 `npm run dev` 后运行截图脚本，再按 `assets/screenshot-plan.md` 填充索引。\n",
        "docs/brand.md": f"# 品牌说明\n\n名称：{values['NAME']}\n\n含义：待补充。\n\nLogo：当前为几何占位方案，请按名字含义确认或替换。\n",
    }
    if deploy == "github":
        files[".github/workflows/deploy.yml"] = GITHUB_WORKFLOW
    elif deploy == "vercel":
        files["vercel.json"] = VERCEL_JSON
    elif deploy == "netlify":
        files["netlify.toml"] = NETLIFY_TOML
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--name", required=True, help="Product name, preferably one short word")
    parser.add_argument("--slug", help="URL/npm slug; defaults to lowercased name")
    parser.add_argument("--domain", default="example.com", help="Domain without protocol")
    parser.add_argument("--description", default="一句话产品定位", help="One-sentence product summary")
    parser.add_argument("--base-path", default="/", help="Astro base path, e.g. /my-repo/ for GitHub Pages")
    parser.add_argument("--deploy", choices=["github", "vercel", "netlify", "generic"], default="generic")
    args = parser.parse_args()

    target = args.target.expanduser().resolve()
    if target.exists() and any(target.iterdir()):
        print(f"error: target directory is not empty: {target}", file=sys.stderr)
        return 1
    target.mkdir(parents=True, exist_ok=True)

    slug = args.slug or args.name.lower().replace(" ", "-")
    domain = args.domain.replace("https://", "").replace("http://", "").strip("/")
    values = {
        "NAME": args.name,
        "SLUG": slug,
        "SITE": f"https://{domain}",
        "BASE": args.base_path if args.base_path.endswith("/") else args.base_path + "/",
        "DESCRIPTION": args.description,
    }

    files = build_files(values, args.deploy)
    readme_values = {
        "PRODUCT_NAME": args.name,
        "PRODUCT_TAGLINE_ZH": args.description,
        "PRODUCT_SUMMARY_ZH": args.description,
    }
    readme = render((SKILL_ROOT / "assets" / "README-template.md").read_text(encoding="utf-8"), readme_values)
    files["README.md"] = readme

    for relative, content in files.items():
        if "{{" in content.replace("${{", ""):
            print(f"warning: unresolved placeholder in {relative}", file=sys.stderr)
        write_file(target, relative, content)

    copy_asset(target, "tokens.css", "src/styles/tokens.css")
    copy_asset(target, "product.example.json", "src/data/product.json")
    product_path = target / "src/data/product.json"
    data = json.loads(product_path.read_text(encoding="utf-8"))
    data["product"]["name"] = args.name
    data["product"]["slug"] = slug
    data["product"]["website"] = f"https://{domain}"
    data["product"]["tagline"]["zh"] = args.description
    data["product"]["summary"]["zh"] = args.description
    product_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    load_derive(product_path, target / "src/data/highlights.json")
    make_png(target / "public" / "logo.png")
    make_og_png(target / "public" / "og-image.png")

    print(f"created {target}")
    print("next: replace example data, confirm name/logo, run npm install && npm run dev")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main())
