# lusca-paper-search 迁入单一源设计

日期：2026-07-14
状态：已批准（用户确认全部待定点）
范围：将散落于仓库根的 `paper_search/` 迁入目标布局的 `skills/` 单一源，规范化为 `lusca-paper-search`

## 上位依据

本设计是 [2026-07-14-lusca-skill-workspace-design.md](./2026-07-14-lusca-skill-workspace-design.md)（方案 A：`skills/` 唯一源 + symlink 发现层）的一次具体执行：把一个尚未收拢的散落 skill 按目标布局归位。本文件只补充 `lusca-paper-search` 特有的迁移与规范化决策，不重复上位设计已锁定的所有权规则。

## 背景

- 仓库根 `paper_search/` 是一个功能完整的多源文献检索 skill（8 个开源 API + 模型自身知识），但散落在 `skills/` 之外，不符合方案 A「唯一源」约定。
- 根 `skills/lusca/`（已迁入并 symlink）的分工表已把「文献检索」指向 `paper_search`，并在 `CHANGELOG` / `references` 中多处以其为示例。
- 命名上，散落目录 `paper_search` 与其 `SKILL.md` frontmatter `name: paper-search` 不一致（下划线 vs 连字符），需借迁移统一为 `lusca-paper-search`。

## 决策摘要

| 项 | 选择 |
|----|------|
| 目标位置 | 仓库根 `skills/lusca-paper-search/`（方案 A 唯一源） |
| skill name | `lusca-paper-search`（目录名 = frontmatter `name`，符合 §1 命名规则） |
| 迁移性质 | 同一 git 仓库内（`paper_search/` 与 `skills/` 同属顶层 `lusca-skill` 仓库） |
| scripts | 整体迁移 12 个脚本文件，原样保留 |
| 结构粒度 | 扁平 + 轻量体系化：SKILL.md 自洽保留输出规范；仅把各源依赖/失败模式抽到 `references/sources.md` |
| eval | 本阶段不做（上位设计 §1 规则 5、§3 明确不做） |
| 报告落盘 | `./outputs/lusca-paper-search/{YYYYMMDDHHmmss}_{slug}.md`（可追溯） |
| 引用更新 | 更新根 `skills/lusca/` 下全部 `paper_search` 引用 |
| 原 `paper_search/` | 迁移后删除 |
| symlink | 手动建 `.claude/skills/lusca-paper-search → ../../skills/lusca-paper-search` |
| 不动项 | `ResearchStudio/`（独立子仓，含自己的 `skills/paper_search`）；`scripts/link-project.sh` 整体实现；Cursor |

## §1 目录与迁移

### 目标布局

```
skills/lusca-paper-search/
├── SKILL.md              # 中文重写
├── CHANGELOG.md          # v1.0.0
├── scripts/              # 迁移自 paper_search/scripts/（原样，12 文件）
│   ├── _env.py
│   ├── search_papers.py
│   └── search_papers_by_{arxiv,dblp,open_alex,openreview,semantic_scholar,
│                         crossref,deepxiv,sciverse,exa,google_scholar}.py
└── references/
    ├── programmatic_api.md   # 迁移自原 paper_search/references/
    └── sources.md            # 新建：8 源依赖/失败模式/Token 说明
```

### 迁移方式

- `scripts/`、`references/programmatic_api.md`：用文件复制迁入（内容原样，不改脚本逻辑）。
- `SKILL.md`：不复制原文，按 §2 重写为中文并适配路径。
- `references/sources.md`：从原 `SKILL.md` 的「Dependencies & failure modes」段抽出扩写。
- 原根 `paper_search/` 在内容迁入、引用更新完成后删除。

## §2 SKILL.md 设计

### frontmatter

```yaml
---
name: lusca-paper-search
description: >-
  多源并行文献检索：arXiv/DBLP/OpenAlex/OpenReview/Semantic Scholar/Crossref/
  DeepXiv/Sciverse 八大开源 API + 模型自身知识，覆盖英文 CS/理工与顶会
  (NeurIPS/ICLR/ICML)。用户提到搜论文、查文献、找 related work、prior art、
  近 X 年某主题发表时使用本技能。
version: "1.0.0"
user-invocable: true
argument-hint: "[可选：检索主题 / 年份范围 / 指定来源]"
allowed-tools: Read, Write, Bash, WebSearch
---
```

### 正文结构（中文，技术术语/API 名保留英文）

1. **核心理念** + 与体系内其它 skill 的分工表（本 skill = 文献检索入口）。
2. **触发条件 / 不触发**。
3. **输入**（全部自动推断，绝不追问）：`query` / `start_year` / `end_year` / `max_papers` / `sources`。
4. **如何运行**：路径改用 `${SKILL_DIR}/scripts/search_papers.py`（替换原 `${CLAUDE_PROJECT_DIR}/skills/paper_search/...`）。`${SKILL_DIR}` = `SKILL.md` 所在目录。
5. **有效来源**表（8 API 源 + model_knowledge）。
6. **输出规范**（完整迁移自原 paper_search）：
   - Step 1：每个来源全量 markdown 表格（# / Title / Date / Venue / Citations），0 结果显式标注，错误 verbatim 上报。
   - Step 2：七节摘要（Overview / Trends / Key themes / Keywords frequency / Most cited by paper / Most cited by author / Recommendations），顺序与字段固定。
7. **model_knowledge 源**：LLM 自回忆 5–10 篇，去重 API 结果，不确定标 `(uncertain — verify)`，不足 5 篇可少给。
8. **各源依赖与失败模式** → 引用 `references/sources.md`。
9. **重要约定**：
   - 报告落盘 `./outputs/lusca-paper-search/{YYYYMMDDHHmmss}_{slug}.md`（完整表格 + 七节摘要，不截断）。
   - 完整报告同步内联展示给用户，绝不省略表格。
   - 全部输入自动推断，首轮即跑。
   - 错误 verbatim 上报，不盲重试。

## §3 引用更新（根 `skills/lusca/`，`paper_search` → `lusca-paper-search`）

| 文件 | 位置 | 处理 |
|------|------|------|
| `skills/lusca/SKILL.md` | 分工表「文献检索」行 | 指向 `lusca-paper-search` |
| `skills/lusca/SKILL.md` | 关联判定示例（2 处） | 示例 skill 名替换 |
| `skills/lusca/CHANGELOG.md` | skill-linkage 条目 | 名称替换 |
| `skills/lusca/references/skill-linkage.md` | 正反例标题与正文（2 处） | 名称替换 |
| `skills/lusca/references/dimensions.md` | 归属维度示例（`scripts/search_papers_by_arxiv.py`） | 路径前缀同步（仍指本 skill 内脚本） |

## §4 symlink

手动建（对齐已有 `lusca` symlink 模式）：

```
.claude/skills/lusca-paper-search -> ../../skills/lusca-paper-search
```

`scripts/link-project.sh` 的幂等批量实现属于工作区基础设施，不在本任务范围。

## 验证清单

1. `skills/lusca-paper-search/SKILL.md` frontmatter `name: lusca-paper-search`、目录名一致。
2. `scripts/` 12 文件齐备，`search_papers.py` 可 `--help` 正常执行。
3. 原 `paper_search/` 已删除，`grep -rn paper_search skills/ docs/` 仅余 `lusca-paper-search` 自身与无关注释。
4. `skills/lusca/` 下不再有裸 `paper_search` 引用。
5. `.claude/skills/lusca-paper-search` symlink 正确指向源、可穿透到 `SKILL.md`。
6. 新开 cc 会话后，触发话术（「搜一下近两年 diffusion policy 的论文」）能命中本 skill。

## 不做项

- `ResearchStudio/` 内 `skills/paper_search`（独立子仓，上游形态）。
- `scripts/link-project.sh` / `link-global.sh`、`CLAUDE.md`、`README.md`（工作区基础设施，后续）。
- eval / 基准脚本（上位设计明确本阶段不做）。
- Cursor 挂载。
