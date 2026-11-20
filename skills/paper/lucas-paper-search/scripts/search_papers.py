#!/usr/bin/env python3
"""Unified interface to search for academic papers across multiple sources.

Supported sources: arXiv, DBLP, OpenAlex, OpenReview, Semantic Scholar, Crossref,
DeepXiv, Sciverse.
"""

import argparse
import concurrent.futures
import importlib
import json
import re
from datetime import date, datetime
from typing import Optional

# Load .env (credentials for openreview etc.) before any source runs, so the aggregator works
# when invoked via bash without a shell-sourced .env. No-op if no .env is found.
try:
    from _env import load_env_once
    load_env_once()
except Exception:
    pass

# Map source name -> module that defines `search_papers_by_<source>`. Modules are imported
# LAZILY (only when a source is actually queried, see _load_source_func) so that a missing
# optional dependency for ONE source — e.g. `scholarly` for google_scholar — no longer crashes
# the whole aggregator at import time. By convention the function name equals the module name.
_SOURCE_MODULE = {
    "arxiv": "search_papers_by_arxiv",
    "dblp": "search_papers_by_dblp",
    # "google_scholar": "search_papers_by_google_scholar",  # needs `scholarly`; disabled by default
    "open_alex": "search_papers_by_open_alex",
    "openreview": "search_papers_by_openreview",
    "semantic_scholar": "search_papers_by_semantic_scholar",
    "crossref": "search_papers_by_crossref",
    "deepxiv": "search_papers_by_deepxiv",
    "sciverse": "search_papers_by_sciverse",
}
ALL_SOURCES = list(_SOURCE_MODULE.keys())


def _load_source_func(source: str):
    """Lazily import and return the search function for one source.

    Raises ImportError (with the underlying missing-module message) if the source's
    optional dependency is not installed — callers catch this and skip just that source."""
    module_name = _SOURCE_MODULE[source]
    module = importlib.import_module(module_name)
    return getattr(module, module_name)

def _parse_date(value, field_name: str) -> Optional[date]:
    """Parse a YYYY-MM-DD string (or pass through date/None) for the post-filter."""
    if value is None or isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as e:
        raise ValueError(f"{field_name} must be YYYY-MM-DD, got {value!r}") from e


def _filter_by_date_range(
    papers: list[dict],
    start_date: Optional[date],
    end_date: Optional[date],
) -> list[dict]:
    """Drop papers whose publication_date falls outside [start_date, end_date].

    Papers without a parseable publication_date are KEPT (we can't prove they're
    out of range, and dropping them would silently lose otherwise relevant results)."""
    if not start_date and not end_date:
        return papers
    kept: list[dict] = []
    for p in papers:
        pub_str = p.get("publication_date")
        if not pub_str:
            kept.append(p)
            continue
        try:
            pub = datetime.strptime(pub_str[:10], "%Y-%m-%d").date()
        except (TypeError, ValueError):
            kept.append(p)
            continue
        if start_date and pub < start_date:
            continue
        if end_date and pub > end_date:
            continue
        kept.append(p)
    return kept


# --- 跨源去重与代码/项目链接提取 -------------------------------------------

_CODE_LINK_RE = re.compile(
    r"https?://(?:www\.)?(?:github\.com/[\w.\-/]+|huggingface\.co/[\w.\-/]+"
    r"|hf\.co/[\w.\-/]+|gitlab\.com/[\w.\-/]+|bitbucket\.org/[\w.\-/]+)",
    re.IGNORECASE,
)


def _normalize_title(title: str) -> str:
    """归一化标题用于跨源去重：小写、标点转空格、压缩空白。"""
    t = (title or "").lower()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _paper_completeness(p: dict) -> int:
    """信息完整度：字段越全分越高，用于标题冲突时保留更全的那条。

    摘要最稀缺（权重 3），URL 次之（2），其余元数据各 1。citation_count=0
    是有效值（新论文），按"字段存在"计 1 分，不按大小。"""
    score = 0
    if p.get("abstract"):
        score += 3
    if p.get("url"):
        score += 2
    if p.get("venue"):
        score += 1
    if p.get("publication_date"):
        score += 1
    if p.get("authors"):
        score += 1
    if p.get("citation_count") is not None:
        score += 1
    if p.get("year"):
        score += 1
    return score


def _extract_code_links(paper: dict) -> list[str]:
    """从摘要抽取 GitHub / HuggingFace / GitLab 等代码或项目链接，去重保序。"""
    text = paper.get("abstract") or ""
    links: list[str] = []
    seen: set[str] = set()
    for match in _CODE_LINK_RE.findall(text):
        url = match.rstrip(".,;)]")
        if url and url not in seen:
            seen.add(url)
            links.append(url)
    return links


def _dedup_cross_source(results: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """跨源标题去重：归一化标题相同者合并为一条，保留最优版本。

    - 选保留版本时 **DBLP 优先级最低**：DBLP 无原生摘要、信息不足，重复组里只要有
      非 dblp 源就丢弃 dblp 版本；非 dblp 之间再按信息完整度取最全。
    - 合并后的记录在其主来源（保留版本的原 source）下展示，并新增 `sources`
      字段记录所有命中来源，让用户知道哪些源都收录了该文。
    - 对保留的记录从摘要抽取 `code_links`（GitHub / HuggingFace / 项目页等）。
    - 无标题的论文不参与去重，原样保留。"""
    groups: dict[str, list[dict]] = {}
    for papers in results.values():
        for p in papers:
            key = _normalize_title(p.get("title", ""))
            if not key:
                key = f"__notitle_{id(p)}"
            groups.setdefault(key, []).append(p)

    def _best_of(papers: list[dict]) -> dict:
        # 首要键：dblp 排最后（1 > 0）；次要键：信息完整度降序（取最全）。
        return min(papers, key=lambda p: (1 if p.get("source") == "dblp" else 0, -_paper_completeness(p)))

    deduped: dict[str, list[dict]] = {s: [] for s in results}
    for papers in groups.values():
        best = _best_of(papers) if len(papers) > 1 else papers[0]
        all_sources: list[str] = []
        for p in papers:
            s = p.get("source")
            if s and s not in all_sources:
                all_sources.append(s)
        best = dict(best)
        best["sources"] = all_sources
        best["code_links"] = _extract_code_links(best)
        primary = best.get("source") or (all_sources[0] if all_sources else "unknown")
        deduped.setdefault(primary, []).append(best)
    return deduped


# --- 扁平化与全局排序 ---------------------------------------------------------

# 规范顺序（信号由高到低）：跨源去重后的全部论文按此顺序归并，组内按日期降序。
_SOURCE_ORDER = [
    "semantic_scholar", "open_alex", "arxiv", "openreview",
    "crossref", "dblp", "deepxiv", "sciverse",
]


def _source_rank(source: str) -> int:
    """来源在规范顺序中的位置；未知来源排所有已知来源之后（保持稳定）。"""
    try:
        return _SOURCE_ORDER.index(source)
    except ValueError:
        return len(_SOURCE_ORDER)


def _flatten_and_sort(deduped_results: dict[str, list[dict]]) -> list[dict]:
    """把跨源去重后的 {source: [papers]} 扁平化为单一列表。

    排序：source 规范顺序（_SOURCE_ORDER），组内 publication_date 降序（新优先）。
    无 publication_date 者排组末（空串最小、reverse 后沉底）。"""
    flat: list[dict] = []
    for source in sorted(deduped_results, key=_source_rank):
        ordered = sorted(
            deduped_results[source],
            key=lambda p: p.get("publication_date") or "",
            reverse=True,
        )
        flat.extend(ordered)
    return flat


# --- 合并 markdown 表格渲染 ---------------------------------------------------

def _md_cell(text: str) -> str:
    """转义会破坏 markdown 表格结构的管道符。"""
    return (text or "").replace("|", "\\|")


def _format_authors(authors: list[str]) -> str:
    if not authors:
        return "—"
    if len(authors) <= 3:
        return _md_cell(", ".join(authors))
    return _md_cell(", ".join(authors[:3])) + " et al."


def _format_date(paper: dict) -> str:
    d = paper.get("publication_date") or ""
    if d:
        return d[:7]  # YYYY-MM
    y = paper.get("year")
    return str(y) if y else "—"


def _code_label(url: str) -> str:
    u = url.lower()
    if "huggingface.co" in u or "hf.co" in u:
        return "model"
    return "code"


def _format_code_links(links: list[str]) -> str:
    if not links:
        return "—"
    return " ".join(f"[{_code_label(u)}]({u})" for u in links)


def _format_sources(paper: dict) -> str:
    sources = paper.get("sources") or []
    if not sources:
        return _md_cell(paper.get("source") or "unknown")
    return _md_cell(", ".join(sources))


def _format_title(paper: dict) -> str:
    title = (paper.get("title") or "").strip() or "(untitled)"
    url = (paper.get("url") or "").strip()
    if url:
        return f"[{_md_cell(title)}]({url})"
    return _md_cell(title)


def _format_venue(paper: dict) -> str:
    v = paper.get("venue") or ""
    return _md_cell(v) if v else "—"


def _render_markdown_table(papers: list[dict]) -> str:
    """渲染合并后的单一 markdown 表格（7 列），序号 1..N 与列表下标一致。"""
    lines = [
        "| # | Title | Author | Date | Venue | Code/Resource | Source |",
        "|---|-------|--------|------|-------|---------------|--------|",
    ]
    for i, p in enumerate(papers, 1):
        lines.append(
            f"| {i} | {_format_title(p)} | {_format_authors(p.get('authors') or [])} "
            f"| {_format_date(p)} | {_format_venue(p)} "
            f"| {_format_code_links(p.get('code_links') or [])} "
            f"| {_format_sources(p)} |"
        )
    return "\n".join(lines)


def _render_data_json(papers: list[dict]) -> str:
    """渲染扁平 JSON 数组，保留全字段（含 abstract / citation_count）供 AI 分析。"""
    return json.dumps(papers, ensure_ascii=False, indent=2)


def _format_cli_output(papers: list[dict], total_before: int, k_sources: int) -> str:
    """组装 CLI 两段输出：DATA(JSON) + TABLE(markdown) + Total 行。

    DATA 段顺序与 TABLE 行序一致 → 序号 = DATA 下标 + 1（导览↔索引闭环）。"""
    data = _render_data_json(papers)
    table = _render_markdown_table(papers)
    m = len(papers)
    return (
        f"===DATA===\n{data}\n\n"
        f"===TABLE===\n{table}\n\n"
        f"Total: {m} unique papers ({total_before} hits before dedup) from {k_sources} sources."
    )


def _search_and_aggregate(
    query: str,
    start_year: int,
    end_year: int,
    max_results: int = 10,
    sources: Optional[list[str]] = None,
    parallel: bool = True,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> tuple[list[dict], int, int]:
    """跑全部来源 → 日期过滤 → 跨源去重 → 扁平排序。

    Args:
        query: Search query string.
        start_year: Filter papers published from this year (used in source queries).
        end_year: Filter papers published up to this year (used in source queries).
        max_results: Maximum number of papers to return per source.
        sources: List of source names to search. Defaults to all sources.
            Valid values: arxiv, dblp, open_alex, openreview, semantic_scholar,
            crossref, deepxiv, sciverse.
        parallel: Whether to query sources in parallel (default: True).
        start_date: Optional YYYY-MM-DD lower bound applied as a post-filter to all
            returned papers (finer-grained than start_year). Papers without a
            parseable publication_date are kept.
        end_date: Optional YYYY-MM-DD upper bound applied as a post-filter (inclusive).

    Returns:
        (flat_papers, total_before_dedup, k_sources_with_hits)
        - flat_papers：去重 + 排序后的扁平 list[dict]
        - total_before_dedup：日期窗口内、去重前的命中总数
        - k_sources_with_hits：返回 >0 条的来源数
    """
    sources = sources or ALL_SOURCES
    invalid = set(sources) - set(ALL_SOURCES)
    if invalid:
        raise ValueError(f"Unknown sources: {invalid}. Valid: {ALL_SOURCES}")

    start_d = _parse_date(start_date, "start_date")
    end_d = _parse_date(end_date, "end_date")
    if start_d and end_d and start_d > end_d:
        raise ValueError(f"start_date {start_d} is after end_date {end_d}")

    results: dict[str, list[dict]] = {}

    def _search(source: str) -> tuple[str, list[dict]]:
        try:
            func = _load_source_func(source)
        except Exception as e:
            # Missing optional dependency for this source — skip it, keep the others working.
            print(f"[{source}] unavailable (import failed: {e}); skipping this source.")
            return source, []
        try:
            papers = func(query, start_year, end_year, max_results)
        except Exception as e:
            print(f"[{source}] Error: {e}")
            papers = []
        return source, papers

    if parallel:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(sources)) as executor:
            futures = {executor.submit(_search, s): s for s in sources}
            for future in concurrent.futures.as_completed(futures):
                source, papers = future.result()
                results[source] = papers
    else:
        for source in sources:
            _, papers = _search(source)
            results[source] = papers

    if start_d or end_d:
        results = {s: _filter_by_date_range(ps, start_d, end_d) for s, ps in results.items()}

    total_before = sum(len(v) for v in results.values())
    k_sources = sum(1 for v in results.values() if v)

    deduped = _dedup_cross_source(results)        # 跨源去重 + code_links 提取
    flat = _flatten_and_sort(deduped)             # 扁平化 + 规范排序
    return flat, total_before, k_sources


def search_papers(
    query: str,
    start_year: int,
    end_year: int,
    max_results: int = 10,
    sources: Optional[list[str]] = None,
    parallel: bool = True,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list[dict]:
    """Search across multiple academic sources and return a flat, deduped, ordered list.

    Args: 同 _search_and_aggregate（query / start_year / end_year / max_results /
        sources / parallel / start_date / end_date）。

    Returns:
        扁平 list[dict]，跨源去重后按 source 规范顺序、组内日期降序排列。
        每个 paper dict 含：title, authors, year, abstract, url, venue,
        citation_count, publication_date, source, sources, code_links。
    """
    flat, _, _ = _search_and_aggregate(
        query=query, start_year=start_year, end_year=end_year,
        max_results=max_results, sources=sources, parallel=parallel,
        start_date=start_date, end_date=end_date,
    )
    return flat


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Search papers across multiple academic sources",
    )
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--start-year", type=int, required=True, help="Start year")
    parser.add_argument("--end-year", type=int, required=True, help="End year")
    parser.add_argument(
        "--max-papers", type=int, default=10,
        help="Max number of papers per source (default: 10)",
    )
    parser.add_argument(
        "--sources", nargs="+", default=None,
        choices=ALL_SOURCES,
        help=f"Sources to search (default: all). Choices: {', '.join(ALL_SOURCES)}",
    )
    parser.add_argument(
        "--no-parallel", action="store_true",
        help="Disable parallel querying of sources",
    )
    parser.add_argument(
        "--start-date", default=None,
        help="Optional YYYY-MM-DD lower bound; applied as a post-filter (finer than --start-year)",
    )
    parser.add_argument(
        "--end-date", default=None,
        help="Optional YYYY-MM-DD inclusive upper bound; applied as a post-filter",
    )
    args = parser.parse_args()

    flat, total_before, k_sources = _search_and_aggregate(
        query=args.query,
        start_year=args.start_year,
        end_year=args.end_year,
        max_results=args.max_papers,
        sources=args.sources,
        parallel=not args.no_parallel,
        start_date=args.start_date,
        end_date=args.end_date,
    )
    print(_format_cli_output(flat, total_before, k_sources))

# Example usage:
# python search_papers.py --query "data efficacy for LM training" --start-year 2024 --end-year 2026 --max-papers 20
# python search_papers.py --query "transformers" --start-year 2023 --end-year 2025 --sources arxiv semantic_scholar
