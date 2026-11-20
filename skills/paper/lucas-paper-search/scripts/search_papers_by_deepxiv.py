#!/usr/bin/env python3
"""Search papers via DeepXiv semantic retrieval over arXiv / bioRxiv / medRxiv.

Backend: https://data.rag.ac.cn/arxiv/?type=retrieve  (Agentic Data Interface).
A handful of free queries ("transformer", "attention mechanism", "large language model",
case-insensitive exact match) work WITHOUT a token. For everything else, set
DEEPXIV_TOKEN (a Bearer token; 10,000 free requests/day).

Uses only the Python standard library (urllib) so it adds no new dependency.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

API_BASE = "https://data.rag.ac.cn/arxiv/"

# Queries that the API serves without authentication (case-insensitive exact match).
_FREE_QUERIES = {"transformer", "attention mechanism", "large language model"}


def _http_get_json(url: str, headers: dict) -> dict:
    req = urllib.request.Request(url, headers=headers)
    last_err: Exception | None = None
    for attempt in range(4):  # initial try + 3 retries with backoff 3s -> 6s -> 12s
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429 and attempt < 3:
                wait = 3 * (2 ** attempt)
                print(f"DeepXiv rate limited, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
        except urllib.error.URLError as e:  # transient network error
            last_err = e
            if attempt < 3:
                time.sleep(3 * (2 ** attempt))
            else:
                raise
    if last_err:
        raise last_err
    return {}


def _year_from_date(date_str) -> int | None:
    if not date_str:
        return None
    try:
        return int(str(date_str)[:4])
    except (ValueError, TypeError):
        return None


def _detect_venue(record: dict) -> str:
    if record.get("biorxiv_id"):
        return "bioRxiv"
    if record.get("medrxiv_id"):
        return "medRxiv"
    return "arXiv"


def search_papers_by_deepxiv(
    query: str,
    start_year: int,
    end_year: int,
    max_results: int = 10,
) -> list[dict]:
    """Search for papers on DeepXiv (semantic retrieval over arXiv/bioRxiv/medRxiv).

    Args:
        query: Search query string (max 500 chars).
        start_year: Filter papers published from this year.
        end_year: Filter papers published up to this year.
        max_results: Maximum number of papers to return.

    Returns:
        List of paper dictionaries (standard schema used by search_papers.py).
    """
    token = os.environ.get("DEEPXIV_TOKEN")
    params: dict = {
        "type": "retrieve",
        "query": query,
        "source": "arxiv",
        "top_k": min(100, max(1, int(max_results))),
    }
    # DeepXiv native date filter; we also post-filter on the response as a safety net.
    if start_year and end_year and start_year <= end_year:
        params["date_search_type"] = "between"
        params["date_str"] = [str(start_year), str(end_year)]
    if token:
        params["token"] = token

    url = API_BASE + "?" + urllib.parse.urlencode(params, doseq=True)
    headers = {"User-Agent": "PaperSearch/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = _http_get_json(url, headers)
    # Response shape: {"status": "success", "total_count": N, "result": [...]}
    results = data.get("result") if isinstance(data, dict) else None
    if results is None:
        results = data if isinstance(data, list) else []

    papers: list[dict] = []
    for r in results:
        if not isinstance(r, dict):
            continue
        authors = [
            a.get("name", "")
            for a in r.get("authors", [])
            if isinstance(a, dict)
        ]
        year = _year_from_date(r.get("date"))
        abstract = r.get("abstract") or r.get("tldr") or ""
        papers.append({
            "title": r.get("title", ""),
            "authors": authors,
            "year": year,
            "abstract": abstract,
            "url": r.get("url", ""),
            "venue": _detect_venue(r),
            "citation_count": int(r.get("citation_count", 0) or 0),
            "publication_date": (r.get("date") or "")[:10],
            "source": "deepxiv",
        })

    # Post-filter by year (keep papers whose year is unknown — can't prove out-of-range).
    if start_year or end_year:
        kept: list[dict] = []
        for p in papers:
            y = p.get("year")
            if y is None:
                kept.append(p)
            elif (not start_year or y >= start_year) and (not end_year or y <= end_year):
                kept.append(p)
        papers = kept

    return papers[:max_results]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search papers on DeepXiv")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--start-year", type=int, required=True, help="Start year")
    parser.add_argument("--end-year", type=int, required=True, help="End year")
    parser.add_argument("--max-papers", type=int, default=10, help="Max number of papers (default: 10)")
    args = parser.parse_args()

    papers = search_papers_by_deepxiv(
        args.query, args.start_year, args.end_year, args.max_papers
    )
    print(papers[0] if papers else "No papers found.")

# python search_papers_by_deepxiv.py --query "transformer" --start-year 2023 --end-year 2025 --max-papers 5
