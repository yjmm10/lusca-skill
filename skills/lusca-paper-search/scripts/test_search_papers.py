"""单元测试：lusca-paper-search 聚合器（扁平化 / 排序 / 渲染）。

只测纯逻辑（不触发真实 API）。从仓库根运行：
    python -m pytest skills/lusca-paper-search/scripts/test_search_papers.py -v
"""
import os
import sys

# 让 `from search_papers import ...` 在任意 cwd 下可用
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


from search_papers import _flatten_and_sort, _source_rank


def test_source_rank_follows_canonical_order():
    # 规范顺序：semantic_scholar → open_alex → arxiv → openreview → crossref → dblp → deepxiv → sciverse
    assert _source_rank("semantic_scholar") < _source_rank("open_alex")
    assert _source_rank("open_alex") < _source_rank("arxiv")
    assert _source_rank("arxiv") < _source_rank("openreview")
    assert _source_rank("dblp") < _source_rank("sciverse")
    # 未知来源排所有已知来源之后
    assert _source_rank("sciverse") < _source_rank("unknown_source")


def test_flatten_sorts_by_source_order_then_date_desc():
    deduped = {
        "arxiv": [
            {"title": "Older", "publication_date": "2024-01-01", "source": "arxiv"},
            {"title": "Newer", "publication_date": "2025-05-01", "source": "arxiv"},
        ],
        "semantic_scholar": [
            {"title": "S2Paper", "publication_date": "2024-06-01", "source": "semantic_scholar"},
        ],
    }
    flat = _flatten_and_sort(deduped)
    titles = [p["title"] for p in flat]
    # semantic_scholar 组先（规范顺序），arxiv 组后；arxiv 组内 date 降序 Newer>Older
    assert titles == ["S2Paper", "Newer", "Older"]


def test_flatten_paper_without_date_goes_last_in_group():
    deduped = {
        "arxiv": [
            {"title": "NoDate", "publication_date": "", "source": "arxiv"},
            {"title": "HasDate", "publication_date": "2023-03-03", "source": "arxiv"},
        ],
    }
    flat = _flatten_and_sort(deduped)
    assert [p["title"] for p in flat] == ["HasDate", "NoDate"]


from search_papers import _render_markdown_table


def test_table_header_is_seven_columns():
    lines = _render_markdown_table([]).splitlines()
    assert lines[0] == "| # | Title | Author | Date | Venue | Code/Resource | Source |"
    assert lines[1] == "|---|-------|--------|------|-------|---------------|--------|"


def test_table_row_formats_all_fields():
    papers = [{
        "title": "Great Paper",
        "authors": ["Alice", "Bob", "Carol", "Dan"],
        "publication_date": "2024-03-15",
        "venue": "NeurIPS",
        "url": "https://arxiv.org/abs/2401.00001",
        "code_links": ["https://github.com/x/y", "https://huggingface.co/z"],
        "sources": ["arxiv", "semantic_scholar"],
    }]
    row = _render_markdown_table(papers).splitlines()[2]
    assert row.startswith("| 1 |")
    assert "[Great Paper](https://arxiv.org/abs/2401.00001)" in row
    assert "Alice, Bob, Carol et al." in row
    assert "2024-03" in row
    assert "NeurIPS" in row
    assert "[code](https://github.com/x/y)" in row
    assert "[model](https://huggingface.co/z)" in row
    assert "arxiv, semantic_scholar" in row


def test_table_empty_fields_show_dash_and_fallback_source():
    papers = [{
        "title": "Bare",
        "authors": [],
        "publication_date": "",
        "year": None,
        "venue": "",
        "url": "",
        "code_links": [],
        "sources": [],
        "source": "dblp",
    }]
    row = _render_markdown_table(papers).splitlines()[2]
    # author / date / venue / code 均空 → 至少 3 个 em-dash（U+2014）占位
    assert row.count("—") >= 3
    # 无 url → 纯文本标题，不渲染 markdown 链接
    assert "[Bare]" not in row
    # sources 空 → 回退到 source 字段
    assert "dblp" in row


import json
from search_papers import _render_data_json, _format_cli_output


def test_data_json_is_valid_array_preserving_full_fields():
    papers = [{
        "title": "X", "abstract": "long abstract text", "citation_count": 5,
        "authors": ["A"], "year": 2024, "publication_date": "2024-01-01",
        "venue": "V", "url": "u", "source": "arxiv",
        "sources": ["arxiv"], "code_links": [],
    }]
    data = json.loads(_render_data_json(papers))
    assert isinstance(data, list) and len(data) == 1
    assert data[0]["abstract"] == "long abstract text"
    assert data[0]["citation_count"] == 5


def test_cli_output_has_data_then_table_in_same_order():
    papers = [
        {"title": "First", "authors": [], "publication_date": "2024-01-01",
         "venue": "", "url": "u1", "source": "arxiv", "sources": ["arxiv"], "code_links": []},
        {"title": "Second", "authors": [], "publication_date": "2023-01-01",
         "venue": "", "url": "u2", "source": "arxiv", "sources": ["arxiv"], "code_links": []},
    ]
    out = _format_cli_output(papers, total_before=5, k_sources=2)
    assert out.startswith("===DATA===")
    assert "===TABLE===" in out
    data_part, table_part = out.split("===TABLE===")
    # DATA 段顺序与 TABLE 行顺序一致：First 在前 → 表格第 1 行
    assert data_part.index("First") < data_part.index("Second")
    assert "| 1 |" in table_part
    assert "Total: 2 unique papers (5 hits before dedup) from 2 sources." in out


import search_papers as sp


def test_search_papers_returns_flat_list(monkeypatch):
    fake = [{"title": "P", "source": "arxiv"}]
    monkeypatch.setattr(
        sp, "_search_and_aggregate",
        lambda **kw: (fake, 1, 1),
    )
    result = sp.search_papers(query="q", start_year=2024, end_year=2025)
    assert isinstance(result, list)
    assert result == fake


def test_aggregate_dedups_flattens_and_counts(monkeypatch):
    # 伪造两个来源：arxiv 2 条（含 1 条与 semantic_scholar 标题重复）、s2 1 条（更全）
    def fake_loader(source):
        if source == "arxiv":
            return lambda q, sy, ey, m: [
                {"title": "Dup", "source": "arxiv", "publication_date": "2024-01-01"},
                {"title": "OnlyArxiv", "source": "arxiv", "publication_date": "2024-06-01"},
            ]
        return lambda q, sy, ey, m: [
            {"title": "Dup", "source": "semantic_scholar",
             "publication_date": "2024-01-01", "abstract": "fuller record"},
        ]
    monkeypatch.setattr(sp, "_load_source_func", fake_loader)
    flat, total_before, k = sp._search_and_aggregate(
        query="q", start_year=2024, end_year=2025, max_results=5,
        sources=["arxiv", "semantic_scholar"], parallel=False,
    )
    # 去重前 3 条（arxiv 2 + s2 1）
    assert total_before == 3
    assert k == 2  # 两个来源都有命中
    # 去重后 2 条（Dup 合并）
    assert len(flat) == 2
    # Dup 主来源 = 信息更全的 semantic_scholar（规范顺序在前）→ 排首位
    assert flat[0]["title"] == "Dup"
    assert set(flat[0]["sources"]) == {"arxiv", "semantic_scholar"}
    assert flat[1]["title"] == "OnlyArxiv"


def test_dedup_drops_dblp_when_any_non_dblp_dup(monkeypatch):
    # dblp 与 s2 标题重复：即便 dblp 字段更全，去重也保留 s2（dblp 无原生摘要、优先级最低）
    def fake_loader(source):
        if source == "dblp":
            return lambda q, sy, ey, m: [
                {"title": "Dup", "source": "dblp", "publication_date": "2024-01-01",
                 "abstract": "x", "venue": "V", "url": "u", "authors": ["A"], "year": 2024,
                 "citation_count": 5},
            ]
        return lambda q, sy, ey, m: [
            {"title": "Dup", "source": "semantic_scholar",
             "publication_date": "2024-01-01", "abstract": "fuller"},
        ]
    monkeypatch.setattr(sp, "_load_source_func", fake_loader)
    flat, total_before, k = sp._search_and_aggregate(
        query="q", start_year=2024, end_year=2025, max_results=5,
        sources=["dblp", "semantic_scholar"], parallel=False,
    )
    assert len(flat) == 1
    # dblp 字段更全（venue/url/citation_count 齐全），仍被丢弃，保留 s2
    assert flat[0]["source"] == "semantic_scholar"
    assert set(flat[0]["sources"]) == {"dblp", "semantic_scholar"}
