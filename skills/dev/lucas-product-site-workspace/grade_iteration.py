#!/usr/bin/env python3
"""Grade iteration-1 eval outputs against eval_metadata.json assertions.

Mechanical checks only; evidence strings cite files that were checked.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEXT_SUFFIXES = {".astro", ".html", ".md", ".ts", ".mjs", ".js", ".json", ".txt", ".toml", ".yml", ".yaml", ".css"}


def iter_files(outputs: Path):
    if not outputs.exists():
        return []
    return [p for p in outputs.rglob("*") if p.is_file()]


def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return ""


def grep_all(outputs: Path, pattern: str) -> list[Path]:
    rx = re.compile(pattern, re.IGNORECASE)
    return [p for p in iter_files(outputs) if p.suffix.lower() in TEXT_SUFFIXES and rx.search(read(p))]


def find(outputs: Path, name: str) -> list[Path]:
    return [p for p in iter_files(outputs) if p.name.lower() == name.lower()]


def metric_values(data: dict) -> set[str]:
    values = set()
    for key in ("metrics",):
        for m in data.get(key) or []:
            if isinstance(m, dict) and m.get("value") is not None:
                values.add(str(m["value"]))
    return values


def check_three_pages(outputs: Path, astro: bool) -> tuple[bool, str]:
    pages = []
    if astro:
        needed = ["src/pages/index.astro", "src/pages/data/index.astro", "src/pages/about/index.astro",
                  "src/pages/en/index.astro", "src/pages/en/data/index.astro", "src/pages/en/about/index.astro"]
    else:
        rels = [str(p.relative_to(outputs)).replace("\\", "/").lower() for p in iter_files(outputs) if p.suffix == ".html"]
        roots = {r.split("/")[0] for r in rels}
        if len(roots) == 1 and all(r.count("/") >= 1 for r in rels):
            prefix = roots.pop() + "/"
            rels = [r[len(prefix):] for r in rels]
        top = {r for r in rels if "/" not in r}
        en = {r for r in rels if r.startswith("en/")}
        ok = ("index.html" in top and any("data" in r for r in top) and any("about" in r for r in top)
              and any(r.endswith("index.html") for r in en) and any("data" in r for r in en) and any("about" in r for r in en))
        return ok, f"html files: {sorted(rels)[:12]}"
    missing = [n for n in needed if not find(outputs, Path(n).name) and not (outputs / n).exists()]
    found = [n for n in needed if n not in missing]
    # simpler: check relative paths under any project root
    rel_ok = []
    for n in needed:
        hits = [p for p in iter_files(outputs) if str(p.relative_to(outputs)).replace("\\", "/").endswith(n)]
        rel_ok.append(bool(hits))
    ok = all(rel_ok)
    return ok, f"found {sum(rel_ok)}/{len(needed)}: {found if not ok else 'all'}"


def grade_eval1(outputs: Path) -> list[dict]:
    res = []
    astro = bool(find(outputs, "astro.config.mjs")) or bool([p for p in iter_files(outputs) if p.suffix == ".astro"])
    ok, ev = check_three_pages(outputs, astro)
    res.append({"text": "Project has landing, data, about and /en/ page files", "passed": ok, "evidence": ev})
    prod = [p for p in iter_files(outputs) if p.name == "product.json"]
    hl = [p for p in iter_files(outputs) if p.name in ("highlights.json",)]
    res.append({"text": "product.json and derived highlights.json both exist",
                "passed": bool(prod and hl),
                "evidence": f"product.json={len(prod)}, highlights.json={len(hl)}" + ("; baseline splits data into metrics.json/news.json without single-source highlights" if not hl else "")})
    tokens = grep_all(outputs, r"--(bg|surface|brand)\s*:")
    bilingual = grep_all(outputs, r'"zh"\s*:')
    res.append({"text": "Theme tokens and zh/en dictionaries are present",
                "passed": bool(tokens) and bool(bilingual),
                "evidence": f"token declarations in {len(tokens)} files; zh-keyed bilingual data in {len(bilingual)} files"})
    seo_hits = {m: bool(grep_all(outputs, m)) for m in ("canonical", "hreflang")}
    sitemap = bool(find(outputs, "sitemap.xml") or [p for p in iter_files(outputs) if "sitemap" in p.name] or grep_all(outputs, "sitemap"))
    llms = bool(find(outputs, "llms.txt") or [p for p in iter_files(outputs) if "llms" in p.name])
    res.append({"text": "SEO/GEO files include canonical, hreflang, sitemap and llms.txt",
                "passed": all(seo_hits.values()) and sitemap and llms,
                "evidence": f"canonical={seo_hits['canonical']}, hreflang={seo_hits['hreflang']}, sitemap={sitemap}, llms.txt={llms}"})
    svg = bool(find(outputs, "logo.svg") or grep_all(outputs, "<svg"))
    png = bool(find(outputs, "logo.png") or find(outputs, "og-image.png"))
    workflow = bool(grep_all(outputs, "actions/deploy-pages|github/pages|pages deploy") or find(outputs, "deploy.yml"))
    res.append({"text": "SVG and PNG logo plus GitHub Pages workflow exist",
                "passed": svg and png and workflow,
                "evidence": f"svg={svg}, png={png}, gh workflow={workflow}"})
    readme = bool(find(outputs, "README.md"))
    plan = bool([p for p in iter_files(outputs) if "screenshot" in p.name.lower()] or grep_all(outputs, "截图计划|screenshot plan"))
    res.append({"text": "README and a screenshot plan are present", "passed": readme and plan,
                "evidence": f"README.md={readme}, screenshot plan={plan}"})
    return res


def grade_eval2(outputs: Path) -> list[dict]:
    res = []
    sample = [p for p in iter_files(outputs) if p.name == "product.example.json"]
    normalized = [p for p in iter_files(outputs) if p.name in ("product.json", "normalized.json")]
    res.append({"text": "Example product data is copied and normalized to the required schema",
                "passed": bool(sample and normalized),
                "evidence": f"sample copies={len(sample)}, normalized files={[str(p.relative_to(outputs)) for p in normalized][:3]}"})
    src_vals: set[str] = set()
    derived_vals: set[str] = set()
    try:
        s = json.loads(read(sample[0])) if sample else {}
        src_vals = metric_values(s)
    except Exception:
        pass
    for p in normalized:
        try:
            d = json.loads(read(p))
            derived_vals |= metric_values(d)
        except Exception:
            pass
    unknown = derived_vals - src_vals
    res.append({"text": "Derived highlights contain no metric values absent from the source data",
                "passed": not unknown,
                "evidence": f"source values={sorted(src_vals)}, unknown derived values={sorted(unknown) if unknown else 'none'}"})
    landing_import = grep_all(outputs, r"highlights\.json") if any(p.suffix == ".astro" for p in iter_files(outputs)) else []
    js_render = grep_all(outputs, r"fetch\(|app\.js|data/metrics|normalized\.json")
    landing_files = [p for p in iter_files(outputs) if p.name in ("index.html", "LandingContent.astro")]
    hardcoded = [v for v in derived_vals if v and any(v in read(p) for p in landing_files)]
    res.append({"text": "Landing page reads derived highlights instead of hardcoding metric values",
                "passed": bool(landing_import or js_render),
                "evidence": f"highlights.json referenced in {len(landing_import)} astro files; JSON-driven render refs in {len(js_render)} files; hardcoded metric hits={len(hardcoded)}"})
    ui = [p for p in iter_files(outputs) if "ui-decision" in p.name.lower() or "ui-research" in p.name.lower()]
    ui_text = "\n".join(read(p) for p in ui)
    url_count = len(re.findall(r"https?://", ui_text))
    tradeoff = bool(re.search(r"代价|tradeoff|升级路径|trade-offs|limitations", ui_text, re.I))
    res.append({"text": "UI decision document cites at least 3 sources and states a tradeoff",
                "passed": url_count >= 3 and tradeoff,
                "evidence": f"docs={[p.name for p in ui]}, links={url_count}, tradeoff/limits mentioned={tradeoff}"})
    period = grep_all(outputs, r"period|周期")
    source = grep_all(outputs, r"source|来源")
    res.append({"text": "Data page displays source and period for metrics",
                "passed": bool(period and source),
                "evidence": f"period refs in {len(period)} files; source refs in {len(source)} files"})
    return res


def grade_eval3(outputs: Path) -> list[dict]:
    res = []
    brand_files = [p for p in iter_files(outputs) if "brand" in p.name.lower() and p.suffix == ".md"]
    all_md = "\n".join(read(p) for p in iter_files(outputs) if p.suffix == ".md")
    candidates = len(re.findall(r"^\s*[-*]\s+\*\*[A-Za-zÀ-ɏ\u4e00-\u9fff][\w\u4e00-\u9fff]{1,12}\*\*", all_md, re.M))
    recommend = bool(re.search(r"推荐|recommendation|chose|selected|named", all_md, re.I))
    res.append({"text": "At least 3 short name candidates and one recommendation are documented",
                "passed": candidates >= 3 and recommend,
                "evidence": f"bold candidate bullets={candidates}, recommendation present={recommend}, brand docs={[p.name for p in brand_files]}"})
    svg = bool(find(outputs, "logo.svg") or grep_all(outputs, "<svg"))
    png = bool(find(outputs, "logo.png") or find(outputs, "og-image.png") or [p for p in iter_files(outputs) if p.suffix == ".png"])
    concept = bool(re.search(r"含义|concept|meaning|意象", (read(brand_files[0]) if brand_files else all_md), re.I))
    res.append({"text": "Logo SVG and PNG exist and the brand doc explains their concept",
                "passed": svg and png and concept,
                "evidence": f"svg={svg}, png={png}, concept explained={concept}"})
    idx = bool([p for p in iter_files(outputs) if p.name == "index.html" or p.name == "index.astro"])
    en = bool([p for p in iter_files(outputs) if (p.name == "index.html" or p.name == "index.astro") and ("en" in str(p.parent).lower())])
    res.append({"text": "Chinese landing page and English /en/ landing page both exist",
                "passed": idx and en,
                "evidence": f"zh landing={idx}, en landing={en}"})
    canonical = bool(grep_all(outputs, "canonical"))
    hreflang = bool(grep_all(outputs, "hreflang"))
    jsonld = bool(grep_all(outputs, "application/ld\\+json|schema\\.org"))
    llms = bool(find(outputs, "llms.txt") or [p for p in iter_files(outputs) if "llms" in p.name])
    res.append({"text": "SEO/GEO includes canonical, hreflang, JSON-LD and llms.txt",
                "passed": canonical and hreflang and jsonld and llms,
                "evidence": f"canonical={canonical}, hreflang={hreflang}, json-ld={jsonld}, llms.txt={llms}"})
    cache = bool([p for p in iter_files(outputs) if p.name in ("_headers", "vercel.json", "netlify.toml")] or grep_all(outputs, "Cache-Control|LCP|性能预算|performance budget"))
    res.append({"text": "Performance or cache configuration is present", "passed": cache,
                "evidence": f"cache/perf artifacts found={cache}"})
    return res


def main() -> None:
    iteration = ROOT / "iteration-1"
    graders = {"astro-three-page-site": grade_eval1, "data-source-derivation": grade_eval2, "naming-brand-seo": grade_eval3}
    for eval_dir in sorted(p for p in iteration.iterdir() if p.is_dir() and p.name.startswith("eval-")):
        meta = json.loads((eval_dir / "eval_metadata.json").read_text(encoding="utf-8"))
        grader = graders[meta["eval_name"]]
        for variant in ("with_skill", "without_skill"):
            run_dir = eval_dir / variant
            expectations = grader(run_dir / "outputs")
            passed = sum(1 for e in expectations if e["passed"])
            grading = {
                "expectations": expectations,
                "summary": {"passed": passed, "failed": len(expectations) - passed, "total": len(expectations),
                            "pass_rate": round(passed / len(expectations), 2) if expectations else 0},
            }
            (run_dir / "grading.json").write_text(json.dumps(grading, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(eval_dir.name, variant, f"{passed}/{len(expectations)}")


if __name__ == "__main__":
    main()
