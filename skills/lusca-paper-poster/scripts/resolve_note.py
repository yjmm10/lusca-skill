#!/usr/bin/env python3
"""Resolve lusca-paper-read note path + imgs root from CLI arg."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def latest_note(slug_dir: Path) -> Path | None:
    cands = sorted(slug_dir.glob(f"*_{slug_dir.name}.md")) + sorted(
        slug_dir.glob("*.md")
    )
    # prefer timestamped notes
    stamped = [p for p in cands if p.name[0:8].isdigit()]
    pool = stamped or cands
    if not pool:
        return None
    return max(pool, key=lambda p: p.stat().st_mtime)


def resolve(arg: str) -> dict:
    p = Path(arg).expanduser().resolve()
    if p.is_file() and p.suffix.lower() == ".md":
        note = p
        note_dir = p.parent
    elif p.is_dir():
        note = latest_note(p)
        if note is None:
            raise SystemExit(f"ERROR: no .md note in {p}")
        note_dir = p
    else:
        raise SystemExit(f"ERROR: not a note file or slug dir: {arg}")

    imgs = note_dir / "imgs"
    slug = note_dir.name
    return {
        "note": str(note),
        "note_dir": str(note_dir),
        "imgs": str(imgs),
        "imgs_exists": imgs.is_dir(),
        "slug": slug,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help="note .md or lusca-paper-read/{slug}/ dir")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args()
    info = resolve(args.path)
    if args.json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        for k, v in info.items():
            print(f"{k}={v}")


if __name__ == "__main__":
    main()
