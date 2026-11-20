#!/usr/bin/env python3
"""Fill landscape HTML template from poster_copy.json → outdir/poster.html."""
from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "assets" / "templates" / "poster_landscape_60x36.html"


def lis(items: list[str]) -> str:
    if not items:
        return "<li>—</li>"
    return "\n".join(f"<li>{html.escape(t)}</li>" for t in items)


def authors_str(authors) -> str:
    if isinstance(authors, list):
        return ", ".join(str(a) for a in authors)
    return str(authors or "")


def fig_html(rel: str | None) -> str:
    if not rel:
        return "<p style='color:#888;font-size:14pt'>(no figure)</p>"
    return f'<img src="{html.escape(rel)}" alt="figure" />'


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--copy", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--template", type=Path, default=TEMPLATE)
    args = ap.parse_args()
    data = json.loads(args.copy.read_text(encoding="utf-8"))
    meta = data["meta"]
    qr_manifest_path = args.outdir / "assets" / "qr_manifest.json"
    qr_tiles = []
    if qr_manifest_path.is_file():
        qr_tiles = (json.loads(qr_manifest_path.read_text(encoding="utf-8"))
                    .get("qr") or [])

    paper = next((t for t in qr_tiles if t.get("kind") == "paper"), None)
    code = next((t for t in qr_tiles if t.get("kind") == "code"), None)

    repl = {
        "{{TITLE}}": html.escape(str(meta.get("title", ""))[:200]),
        "{{AUTHORS}}": html.escape(authors_str(meta.get("authors"))),
        "{{VENUE}}": html.escape(str(meta.get("venue", ""))),
        "{{PROBLEM_LIS}}": lis(data.get("problem") or []),
        "{{CONTRIBUTION_LIS}}": lis(data.get("contribution") or []),
        "{{METHOD_LIS}}": lis(data.get("method") or []),
        "{{RESULTS_LIS}}": lis(data.get("results") or []),
        "{{TAKEAWAY}}": html.escape(str(data.get("takeaway", ""))),
        "{{CAVEAT}}": html.escape(str(data.get("caveat", ""))),
        "{{METHOD_FIGURE}}": fig_html((data.get("figures") or {}).get("method")),
        "{{RESULT_FIGURE}}": fig_html((data.get("figures") or {}).get("result")),
        "{{QR_PAPER_SRC}}": paper["path"] if paper else "",
        "{{QR_PAPER_LABEL}}": paper.get("label", "Paper") if paper else "",
        "{{QR_PAPER_HIDDEN}}": "" if paper else "hidden",
        "{{QR_CODE_SRC}}": code["path"] if code else "",
        "{{QR_CODE_LABEL}}": code.get("label", "Code") if code else "",
        "{{QR_CODE_HIDDEN}}": "" if code else "hidden",
    }

    text = args.template.read_text(encoding="utf-8")
    for k, v in repl.items():
        text = text.replace(k, v)

    args.outdir.mkdir(parents=True, exist_ok=True)
    out = args.outdir / "poster.html"
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
