#!/usr/bin/env python3
"""Generate QR PNGs from poster_copy.json qr URLs into outdir/assets/qr/."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import qrcode
except ImportError:
    print("ERROR: pip install qrcode[pil]", file=sys.stderr)
    sys.exit(2)


def make_one(url: str, dest: Path) -> None:
    img = qrcode.make(url)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--copy", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    args = ap.parse_args()
    data = json.loads(args.copy.read_text(encoding="utf-8"))
    qr = data.get("qr") or {}
    out_qr = args.outdir / "assets" / "qr"
    written = []
    paper = qr.get("paper_url")
    code = qr.get("code_url")
    if paper:
        p = out_qr / "paper.png"
        make_one(paper, p)
        written.append({"kind": "paper", "url": paper, "path": "assets/qr/paper.png",
                        "label": "Paper"})
    if code and code != paper:
        p = out_qr / "code.png"
        make_one(code, p)
        written.append({"kind": "code", "url": code, "path": "assets/qr/code.png",
                        "label": "Code"})
    manifest = {"qr": written}
    (args.outdir / "assets").mkdir(parents=True, exist_ok=True)
    (args.outdir / "assets" / "qr_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    sys.exit(0 if written else 1)


if __name__ == "__main__":
    main()
