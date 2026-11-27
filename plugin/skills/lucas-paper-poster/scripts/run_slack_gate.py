#!/usr/bin/env python3
"""Run paper2poster check_poster slack --strict (FULL 90% gate).

Exit 0 = all sections FULL (and polish clean if --with-polish).
Exit 1 = gate failed (agent may edit poster.html / poster_copy and retry).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Prefer project symlink, then 3rdparty checkout.
CANDIDATES = [
    Path(__file__).resolve().parents[3] / ".claude" / "skills" / "paper2poster" / "scripts" / "check_poster.py",
    Path(__file__).resolve().parents[3] / "3rdparty" / "ResearchStudio" / "ResearchStudio-Reel" / "skills" / "paper2poster" / "scripts" / "check_poster.py",
    Path(__file__).resolve().parents[2] / "paper2poster" / "scripts" / "check_poster.py",
]


def find_check() -> Path:
    for p in CANDIDATES:
        if p.is_file():
            return p
    raise SystemExit(
        "ERROR: paper2poster check_poster.py not found. "
        "Ensure paper2poster is linked under .claude/skills/."
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("poster_html", type=Path)
    ap.add_argument("--with-polish", action="store_true", default=True)
    ap.add_argument("--no-polish", action="store_true")
    args = ap.parse_args()
    check = find_check()
    cmd = [
        sys.executable, str(check), "slack",
        str(args.poster_html.resolve()),
        "--strict",
        "--canvas", "60x36in",
    ]
    if not args.no_polish:
        cmd.append("--with-polish")
    print("RUN:", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, cwd=str(check.parent))
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
