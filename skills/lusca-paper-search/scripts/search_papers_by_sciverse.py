#!/usr/bin/env python3
"""Search papers via Sciverse structured metadata search (meta-search endpoint).

Backend: https://api.sciverse.space/meta-search  (requires SCIVERSE_API_TOKEN, a "sv-..." token).
Returns paper-level records (title, authors, year, venue, abstract, doc_id).

Sciverse is API-only: it does not expose a public per-paper web URL, so when no canonical
URL is returned we fall back to a Google Scholar search for the title, keeping the result
clickable. The internal `doc_id` is preserved on each record for use with Sciverse's
read_content endpoint.

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

API_BASE = "https://api.sciverse.space"


def _http_post_json(url: str, payload: dict, token: str) -> dict:
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "PaperSearch/1.0",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    last_err: Exception | None = None
    for attempt in range(4):  # exponential backoff on 429: 1s -> 2s -> 4s
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code == 429 and attempt < 3:
                wait = 2 ** attempt
                print(f"Sciverse rate limited, retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
        except urllib.error.URLError as e:
            last_err = e
            if attempt < 3:
                time.sleep(2 ** attempt)
            else:
                raise
    if last_err:
        raise last_err
    return {}


def _fallback_url(title: str) -> str:
    """Sciverse has no public web page per doc_id; link to a Scholar search for the title."""
    return "https://scholar.google.com/scholar?q=" + urllib.parse.quote(title or "")


def search_papers_by_sciverse(
    query: str,
    start_year: int,
    end_year: int,
    max_results: int = 10,
) -> list[dict]:
    """Search for papers on Sciverse (structured metadata search).

    Args:
        query: Search query string (BM25 keyword; 1-2048 chars).
        start_year: Filter papers published from this year.
        end_year: Filter papers published up to this year.
        max_results: Maximum number of papers to return.

    Returns:
        List of paper dictionaries (standard schema used by search_papers.py).
    """
    token = os.environ.get("SCIVERSE_API_TOKEN")
    if not token:
        raise RuntimeError(
            "SCIVERSE_API_TOKEN is not set; cannot query Sciverse. "
            "Add it to your .env (see .env.template)."
        )

    # NOTE: /meta-search 不接受 year_from/year_to（服务端返回 400 extra_forbidden）；
    # 年份过滤改为客户端按 publication_published_year 执行。
    payload: dict = {
        "collection": "papers",
        "query": query,
        "page_size": min(50, max(1, int(max_results))),
    }

    data = _http_post_json(f"{API_BASE}/meta-search", payload, token)
    # Response shape: {"results": [ {title, author:[{name}], publication_published_year,
    #   abstract, locations:[{url}], citation_count, doc_id, publication_venue_name_unified}, ... ]}
    results = data.get("results") if isinstance(data, dict) else None
    if results is None:
        results = data if isinstance(data, list) else []

    papers: list[dict] = []
    for h in results:
        if not isinstance(h, dict):
            continue
        title = h.get("title", "")
        # author 是 [{orcid, name}, ...]，提取 name
        raw_authors = h.get("author", []) or []
        if isinstance(raw_authors, list):
            authors = [str(a.get("name", "")) if isinstance(a, dict) else str(a) for a in raw_authors]
        else:
            authors = [str(raw_authors)]
        year = h.get("publication_published_year")
        # 客户端年份过滤（服务端不支持 year_from/year_to）
        if year is not None:
            try:
                yi = int(year)
                if start_year and yi < int(start_year):
                    continue
                if end_year and yi > int(end_year):
                    continue
            except (TypeError, ValueError):
                pass
        # URL: 优先 locations[0].url，其次 access_oa_url，再次 doi
        url = ""
        locs = h.get("locations") or []
        if isinstance(locs, list) and locs and isinstance(locs[0], dict):
            url = locs[0].get("url", "") or ""
        if not url:
            url = h.get("access_oa_url", "") or ""
        if not url and h.get("doi"):
            url = "https://doi.org/" + str(h["doi"])
        if not url:
            url = _fallback_url(title)
        venue = h.get("publication_venue_name_unified", "") or h.get("publication_venue_type", "") or ""
        papers.append({
            "title": title,
            "authors": authors,
            "year": int(year) if year is not None else None,
            "abstract": h.get("abstract", "") or "",
            "url": url,
            "venue": venue,
            "citation_count": int(h.get("citation_count", 0) or 0),
            "publication_date": "",
            "source": "sciverse",
            "doc_id": h.get("doc_id", ""),
        })

    return papers[:max_results]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search papers on Sciverse")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--start-year", type=int, required=True, help="Start year")
    parser.add_argument("--end-year", type=int, required=True, help="End year")
    parser.add_argument("--max-papers", type=int, default=10, help="Max number of papers (default: 10)")
    args = parser.parse_args()

    papers = search_papers_by_sciverse(
        args.query, args.start_year, args.end_year, args.max_papers
    )
    print(papers[0] if papers else "No papers found.")

# python search_papers_by_sciverse.py --query "diffusion model" --start-year 2020 --end-year 2025 --max-papers 5
