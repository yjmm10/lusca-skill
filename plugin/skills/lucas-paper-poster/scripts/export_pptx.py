#!/usr/bin/env python3
"""Export poster.html → editable poster.pptx via paper2poster html2pptx."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

CANDIDATES = [
    Path(__file__).resolve().parents[3] / ".claude" / "skills" / "paper2poster" / "html2pptx",
    Path(__file__).resolve().parents[3] / "3rdparty" / "ResearchStudio" / "ResearchStudio-Reel" / "skills" / "paper2poster" / "html2pptx",
]


def find_html2pptx() -> Path:
    for p in CANDIDATES:
        if (p / "scripts" / "html_to_pptx.py").is_file():
            return p
    raise SystemExit("ERROR: paper2poster html2pptx not found")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--html", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--width-inch", type=float, default=60.0)
    ap.add_argument("--height-inch", type=float, default=36.0)
    args = ap.parse_args()
    root = find_html2pptx()
    # Prefer one-shot html_to_pptx (no vision audit loop).
    cmd = [
        sys.executable, "-m", "scripts.html_to_pptx",
        "--html", str(args.html.resolve()),
        "--out", str(args.out.resolve()),
        "--width-inch", str(args.width_inch),
        "--height-inch", str(args.height_inch),
    ]
    print("RUN:", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=str(root))
    if r.returncode != 0:
        sys.exit(r.returncode)
    print(f"wrote {args.out}")
    sys.exit(0)


if __name__ == "__main__":
    main()
