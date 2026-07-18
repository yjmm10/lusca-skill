# Changelog

本文件记录 lusca-pdf-parse 的版本演进。版本号规则见 `SKILL.md`「版本管理」。

## [1.0.1] — 2026-07-17

### Added
- 「后续衔接」节 + 主流程 Step 6 交付补"附后续衔接建议"：交付时附一句本 skill 产出在主依赖链（`lusca-paper-search`→`lusca-pdf-parse`→`lusca-paper-read`）中的下一步——`/lusca-paper-read` 基于 Markdown 精读（比直接读 PDF 更准、图不丢），另附 `/lusca` 复盘；遵 CLAUDE.md 新增「后续衔接提示（所有 skill 适用）」约定

## [1.0.0] — 2026-07-17

### Added
- 初始版本：基于 MinerU 精准解析 API v4 的 PDF / 图片 / DOCX → 结构化 Markdown 还原。
- `scripts/parse_pdf.py`：统一 CLI（本地批量上传 / URL 提交 → 轮询 → 下载解压 → 定位产物），
  从环境变量 `MINERU_TOKEN` 读凭证（`_env.py` 自动加载仓库根 `.env`，shell 已导出优先）；
  输出 `===RESULT===`（JSON）+ `===SUMMARY===`；字段路径容错；错误原样上报。
- `scripts/_env.py`：轻量 `.env` 加载器（移植自 `lusca-paper-search`）。
- `assets/parse-report-template.md`：落盘解析报告骨架（含 frontmatter + 文末出处块）。
- `references/mineru_api.md`：MinerU API 端点 / token / 状态 / 限制与失败模式参考。
- `SKILL.md`：定位「忠实版面还原（不解读内容）」，明确与 `lusca-paper-read`（理解 + 笔记）的边界与衔接。
