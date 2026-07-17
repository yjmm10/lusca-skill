# Changelog

本文件记录 lusca-paper-search 的版本演进。版本号规则见 `SKILL.md`「版本管理」。

## [2.0.1] — 2026-07-17

### Added
- frontmatter 新增 `author: lusca` 字段（项目统一署名，主页 https://github.com/yjmm10）
- 落盘检索报告新增文末出处块：`assets/report-template.md` 末尾加占位、`SKILL.md`「重要约定」新增条目——作者 / 版本 / 远程出处链接（`https://github.com/yjmm10/lusca-skill/tree/main/skills/lusca-paper-search`），遵 CLAUDE.md「文档输出规范」

## [2.0.0] — 2026-07-15

Breaking：输出体系从「分来源多表 + 七节摘要」重构为「研究导览 + 完整索引」二段式。

### Changed
- 输出结构：导览（AI：发展脉络 mermaid / 研究热点 / 推荐阅读）先行 → 完整索引（脚本直出 7 列合并表）附后 → model_knowledge 附录。
- `search_papers()` 返回值：`dict[source, list]` → 扁平 `list[paper]`（去重 + 排序）。
- CLI 输出：取消按来源分组打印，改为 `===DATA===`(JSON) + `===TABLE===`(markdown) 两段 + Total 行。
- 索引表合并为单表，按 source 规范顺序、组内日期降序，全局连续编号。

### Removed
- 分来源多张表格（合并为一张）。
- Score 列（移入「推荐阅读」理由）。
- abstract 列（详情非索引；abstract 仅留 `===DATA===` 供 AI 分析）。
- Citations 展示列（`citation_count` 留 dict 供 AI）。
- 七节摘要中的 Overview / Keywords frequency / Most cited by accepted paper / Most cited by first author（裁为三节导览）。
- model_knowledge 独立表格（改为附录）。

### Added
- `search_papers.py`：`_flatten_and_sort` / `_render_markdown_table` / `_render_data_json` / `_format_cli_output` / `_search_and_aggregate`。
- `scripts/test_search_papers.py`：聚合与渲染的单元测试（10 例）。

## [1.1.2] — 2026-07-14

### Fixed
- `search_papers_by_open_alex.py`：`search.semantic`（语义端点，常 504 超时）改为 `search`（关键词，
  稳定 1.5s）；`requests.get` 加 `timeout=30` 并对超时/5xx 各重试一次（原无 timeout 会无限等）；
  支持 `OPENALEX_MAILTO`（polite pool）。修正 paper 的 `source` 字段 `openalex`→`open_alex`，
  与 `_SOURCE_MODULE` key 一致——此前跨源去重会把 OpenAlex 结果分裂到 `openalex` 幽灵 key，
  显示为 `open_alex: 0` + `openalex: 10`。
- `search_papers_by_dblp.py`：长/带连字符 query（如 "training-free document understanding"）在 DBLP
  精确匹配 0 命中；新增 query 回退（原 query → 去首词 → 末两词，首个有命中者即用），并将单次搜索
  抽为 `_dblp_query_once`；`requests.get` 加 `timeout=30` + 重试。修复后该 query 0→9 篇。

## [1.1.1] — 2026-07-14

### Fixed
- `search_papers_by_sciverse.py` 适配 Sciverse `/meta-search` 新 schema，修复配置 token 后仍 400 的问题：
  - 移除服务端不接受的 `year_from`/`year_to` 请求字段（返回 400 `extra_forbidden`），
    年份过滤改为客户端按 `publication_published_year` 执行。
  - 响应解析从 `hits` 改为 `results`；适配字段名（`author`→name、`publication_published_year`→year、
    `locations[0].url`→url、`publication_venue_name_unified`→venue），改用真实 `citation_count`
    （原硬编码 0）；year/citation_count 强制 int，避免浮点显示（如 `2024.0`）。
  - 修正 `.env.template` 注释中 Sciverse token 前缀说明（实际为 `sci_`，非 `sv-`）仅在本 connector
    docstring 标注，template 位于 3rdparty 暂未同步。

## [1.1.0] — 2026-07-14

### Added
- 跨源标题去重：`search_papers.py` 聚合后自动合并标题相同的重复论文，保留信息最全的版本，
  新增 `sources` 字段记录全部命中来源（无标题论文不参与去重，原样保留）。
- 代码 / 项目链接提取：从摘要正则抽取 GitHub / HuggingFace / GitLab / Bitbucket 链接，
  存入新字段 `code_links`，在 Step 1 表格 Code/Resources 列展示。
- 综合评分（Score = relevance + value，0–10）：每篇论文一个综合分，相关度 + 价值合成，
  写在 Step 1 表格 Score 列，作为 Step 2 推荐与热点判定的依据。
- 落盘报告 frontmatter 规范：检索报告 md 顶部必须有基础信息块
  （query / sources / year_range / total_hits / unique_papers / generated_at / generator）。
- `assets/report-template.md`：落盘报告骨架模板，含 frontmatter + Step 1 + Step 2 七节。

### Changed
- Step 1 表格新增 Score、Code/Resources 列；标题必须为可点击链接（每篇必给出处 URL）；
  序号跨来源全局连续。
- Step 2 的 Trends 强化为「技术发展脉络」（时间线 + 方法演进），Key themes 强化为
  「研究热点」（聚类 + ↑/→/↓ 趋势方向）。
- 版本 1.0.1 → 1.1.0。

## [1.0.1] — 2026-07-14

### Changed
- 分工表补 `lusca-paper-read`（精读论文）交叉引用，明确"找→读"衔接。

## [1.0.0] — 2026-07-14

### Added
- 初始版本：由散落的根目录 `paper_search/` 迁入工作区单一源 `skills/lusca-paper-search/`（方案 A）。
- 多源并发文献检索，覆盖 arXiv / DBLP / OpenAlex / OpenReview / Semantic Scholar / Crossref / DeepXiv / Sciverse 八大开源 API + model_knowledge 模型知识源。
- `SKILL.md` 中文化重写，路径改用 `${SKILL_DIR}`，报告落盘改为可追溯的 `./outputs/lusca-paper-search/{ts}_{slug}.md`。
- `references/sources.md`：从原 `SKILL.md` 抽出的各源依赖 / Token 要求 / 失败模式说明。
- `references/programmatic_api.md`：函数式调用接口（迁移自原 skill）。
- `scripts/`：12 个检索脚本（聚合器 + 10 个来源脚本 + `_env.py`）原样迁移。

### Changed
- 命名统一：目录与 frontmatter `name` 均为 `lusca-paper-search`（原 `paper_search` / `paper-search` 下划线与连字符混用）。
- 体系内 `skills/lusca/` 的文献检索引用由 `paper_search` 改指 `lusca-paper-search`。

### Removed
- 删除散落的根目录 `paper_search/`（内容已迁入本 skill）。
