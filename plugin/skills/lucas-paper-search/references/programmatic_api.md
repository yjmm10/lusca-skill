# Programmatic API

Most use cases are best served by the CLI in `scripts/search_papers.py` (which
prints a `===DATA===` JSON block plus a `===TABLE===` markdown block). Reach for
the function-call interface only when you need to consume the structured list
directly.

```bash
cd scripts && python -c "
from search_papers import search_papers
papers = search_papers(
    query='<QUERY>',
    start_year=2024,
    end_year=2026,
    max_results=10,
    sources=['semantic_scholar', 'open_alex', 'arxiv', 'openreview'],
    parallel=True,
)
print(len(papers), 'papers')
for p in papers:
    print(f'  - {p[\"title\"]} ({p[\"year\"]})')
"
```

`search_papers()` returns a **flat `list[dict]`**: cross-source deduped and
ordered by source canonical order, then by `publication_date` descending within
each source. Each paper dict contains: `title`, `authors`, `year`, `abstract`,
`url`, `venue`, `citation_count`, `publication_date`, `source`, `sources`
(all sources that matched this paper), `code_links` (GitHub/HuggingFace/etc.
extracted from the abstract).

For the pre-dedup hit count and number of sources with hits, use the internal
`_search_and_aggregate(...)` which returns `(flat_papers, total_before_dedup,
k_sources_with_hits)`.
