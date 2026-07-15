# Changelog

本文件记录 lusca-paper-search 的版本演进。版本号规则见 `SKILL.md`「版本管理」。

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
