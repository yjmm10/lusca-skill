# 从 lusca-paper-read 笔记提炼 poster_copy.json

读完整笔记后 **Write 一次** `poster_copy.json`，对照 `assets/poster_copy.schema.json` 与 `copy-budget.md`。

## 字段映射

| JSON | 笔记来源 |
|------|----------|
| `meta.*` | YAML frontmatter（title / authors / venue+year / slug） |
| `problem` | §1.1 研究问题、痛点（浓缩，不抄长段） |
| `contribution` | §1.2 核心贡献 |
| `method` | §2 整体流程 + 2.2 要点（不写伪代码全文） |
| `results` | §3 主要发现 + 关键数字 |
| `takeaway` | TL;DR 结论句 |
| `caveat` | TL;DR caveat 或 §4.1 最关键一句 |
| `figures.method` / `.result` | 见 `figure-pick.md`（相对笔记目录的 `imgs/...`） |
| `qr.paper_url` / `code_url` | 资源链接块或 frontmatter `source`/`arxiv`/`doi`；无则 `null` |

## 禁止

- 编造数字、引用、结论
- 从 PDF / 笔记外补图
- 把 §4 长批判整段上墙
- 直贴笔记原文超预算段落（必须提炼）
