#!/usr/bin/env python3
"""Copy selected figures from note imgs/ into outdir/imgs/."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def resolve_fig(note_dir: Path, rel: str | None) -> Path | None:
    if not rel:
        return None
    p = (note_dir / rel).resolve()
    if p.is_file():
        return p
    alt = note_dir / "imgs" / Path(rel).name
    return alt if alt.is_file() else None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--copy", type=Path, required=True)
    ap.add_argument("--note-dir", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()
    data = json.loads(args.copy.read_text(encoding="utf-8"))
    figs = data.get("figures") or {}
    dest_dir = args.outdir / "imgs"
    dest_dir.mkdir(parents=True, exist_ok=True)
    mapping = {}
    for slot in ("method", "result"):
        src = resolve_fig(args.note_dir, figs.get(slot))
        if src is None:
            mapping[slot] = None
            continue
        dest = dest_dir / src.name
        shutil.copy2(src, dest)
        mapping[slot] = f"imgs/{src.name}"
        figs[slot] = mapping[slot]
    data["figures"] = figs
    args.copy.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    print(json.dumps(mapping, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
