#!/usr/bin/env python3
"""Validate poster_copy.json against schema + copy budgets + figure paths."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "assets" / "poster_copy.schema.json"

MAX_ITEMS = {
    "problem": 3,
    "contribution": 3,
    "method": 5,
    "results": 4,
}
# Chinese char budget OR English word budget per bullet
BULLET_ZH = 28
BULLET_EN = 18
TAKEAWAY_ZH, TAKEAWAY_EN = 80, 50
CAVEAT_ZH, CAVEAT_EN = 40, 25


def _is_cjk_heavy(s: str) -> bool:
    cjk = len(re.findall(r"[\u4e00-\u9fff]", s))
    return cjk >= max(1, len(s.strip()) // 4)


def _words(s: str) -> int:
    return len(s.split())


def _chars_zh(s: str) -> int:
    return len(re.sub(r"\s+", "", s))


def check_bullet(label: str, text: str, errs: list[str]) -> None:
    if _is_cjk_heavy(text):
        n = _chars_zh(text)
        if n > BULLET_ZH:
            errs.append(f"{label}: {n} chars > {BULLET_ZH}")
    else:
        n = _words(text)
        if n > BULLET_EN:
            errs.append(f"{label}: {n} words > {BULLET_EN}")


def check_span(label: str, text: str, zh: int, en: int, errs: list[str]) -> None:
    if _is_cjk_heavy(text):
        n = _chars_zh(text)
        if n > zh:
            errs.append(f"{label}: {n} chars > {zh}")
    else:
        n = _words(text)
        if n > en:
            errs.append(f"{label}: {n} words > {en}")


def has_number(items: list[str]) -> bool:
    return any(re.search(r"\d", x) for x in items)


def validate(data: dict, note_dir: Path | None) -> list[str]:
    errs: list[str] = []
    for key in ("meta", "problem", "contribution", "method", "results",
                "takeaway", "caveat", "figures", "qr"):
        if key not in data:
            errs.append(f"missing key: {key}")
    if errs:
        return errs

    meta = data["meta"]
    for k in ("title", "authors", "venue", "slug"):
        if k not in meta or meta[k] in (None, ""):
            errs.append(f"meta.{k} required")

    for field, cap in MAX_ITEMS.items():
        items = data[field]
        if not isinstance(items, list):
            errs.append(f"{field} must be array")
            continue
        if len(items) > cap:
            errs.append(f"{field}: {len(items)} items > {cap}")
        for i, t in enumerate(items):
            if not isinstance(t, str) or not t.strip():
                errs.append(f"{field}[{i}] empty")
            else:
                check_bullet(f"{field}[{i}]", t, errs)

    if isinstance(data["results"], list) and data["results"]:
        if not has_number(data["results"]):
            errs.append("results: need ≥1 bullet with a digit (or explicit n/a)")

    if not isinstance(data["takeaway"], str) or not data["takeaway"].strip():
        errs.append("takeaway required")
    else:
        check_span("takeaway", data["takeaway"], TAKEAWAY_ZH, TAKEAWAY_EN, errs)

    if not isinstance(data["caveat"], str) or not data["caveat"].strip():
        errs.append("caveat required")
    else:
        check_span("caveat", data["caveat"], CAVEAT_ZH, CAVEAT_EN, errs)

    figs = data.get("figures") or {}
    if note_dir is not None:
        for slot in ("method", "result"):
            rel = figs.get(slot)
            if rel in (None, "", "null"):
                continue
            path = (note_dir / rel).resolve()
            # also allow already-copied under outdir imgs
            if not path.is_file():
                alt = note_dir / "imgs" / Path(rel).name
                if not alt.is_file():
                    errs.append(f"figures.{slot} missing: {rel}")

    return errs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("copy_json", type=Path)
    ap.add_argument("--note-dir", type=Path, default=None,
                    help="note directory for resolving imgs/ paths")
    args = ap.parse_args()
    data = json.loads(args.copy_json.read_text(encoding="utf-8"))
    errs = validate(data, args.note_dir)
    if errs:
        print("INVALID poster_copy.json:", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("OK poster_copy.json")
    sys.exit(0)


if __name__ == "__main__":
    main()
