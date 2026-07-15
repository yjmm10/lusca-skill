# lusca-paper-search 输出体系重构设计（v2.0.0）

日期：2026-07-15
状态：已批准（用户确认体系与三项关键决策）
范围：重构 `lusca-paper-search` 的输出规范与 `search_papers.py` 聚合输出，从「分来源多表 + 七节摘要」收敛为「导览先行 + 单索引表」二段式体系
版本：`1.1.2` → `2.0.0`（breaking：输出结构、CLI 输出、函数式 API 返回值均变）

## 上位依据

延续 [2026-07-14-lusca-paper-search-design.md](./2026-07-14-lusca-paper-search-design.md)（迁入单一源 + 规范化）。本文件只管「输出体系」，不重复所有权 / 迁移规则。

## 动机：两个原理

1. **需求第一性**：用户检索文献不是为了得到一份论文清单，而是 ① 建立领域认知（脉络 / 热点）② 定位「要读的那几篇」③ 完整召回、不漏。下游消费的是「一份认知结论 + 一张可扫览的地图」。
2. **技能功能单一性**：本 skill = 检索召回 + 最小必要导览。不做精读（`lusca-paper-read`）、不做润色（`paper-polish-skill`）、不做综述写作。导览要克制——给路线，不展开每篇。

两原理导出职责边界：
- **脚本产出「事实」** → 完整索引（有什么），零 AI 介入。
- **AI 产出「认知」** → 研究导览（意味着什么、读什么）。

## 设计原则

| 原则 | 含义 |
|------|------|
| 表格纯数据 | 索引表完全由脚本从 API 的 JSON 产出；AI 原样采用，不重排、不分析、不打分。 |
| 导览克制 | AI 导览只做聚类 / 脉络 / 推荐，不展开单篇深度内容（那是 `lusca-paper-read` 的事）。 |
| 完整召回不妥协 | 索引表必须列出全部命中（去重后），不得为省篇幅折叠。 |
| 序号闭环 | 导览用 `[序号]` 引用索引表序号；脚本保证 JSON 列表顺序 = 表格顺序，序号稳定可引。 |

## 决策摘要

| 项 | 选择 |
|----|------|
| 表格结构 | 单张合并表（取消按来源分层） |
| 表格字段 | `# \| title(链接) \| author \| date \| venue \| code/resource \| source` |
| 表格产出方 | 脚本直出 markdown（AI 不渲染） |
| 表格排序 | source 规范顺序，组内 `publication_date` 降序 |
| abstract 列 | 移出表格（详情非索引）；完整 abstract 仅保留在脚本输出的 JSON 供 AI 分析 |
| Score 列 | 移出表格；融入「推荐阅读」理由 |
| Citations 列 | 不展示；`citation_count` 保留在 dict 供 AI 摘要用 |
| source 列 | 多源命中显示全部来源，主来源在前（逗号分隔） |
| 摘要节数 | 七节 → 三节（发展脉络 / 研究热点 / 推荐阅读） |
| 报告顺序 | 导览先行、索引附后（认知先行） |
| model_knowledge | 不进索引表；作为综合附录列出，标注 uncertain |
| 函数式 API | 返回值 `dict[source,list]` → `list[paper]`（扁平、已去重、已排序） |
| 版本 | breaking，`1.1.2` → `2.0.0` |

## 输出体系结构

一份检索报告 = 报告头 + **研究导览（AI）** + **完整索引（脚本）** + model_knowledge 附录。

```
# 文献检索报告：<query 简述>

> frontmatter
> 一句话总览：query / 年份范围 / 命中 N 个来源、去重后 M 篇（全部列于下方索引表）

## 一、研究导览（AI 分析，认知先行）

### 1. 技术发展脉络
<mermaid flowchart TD>
<三五句文字简述：起点 → 转折 → 主流 → 新兴>

### 2. 研究热点
| Theme | 描述 | 代表论文 | 趋势 | counts |
|-------|------|---------|------|--------|

### 3. 推荐阅读
<3–5 篇，奠基 → 最新，各一行理由，引用 [序号]>

## 二、完整索引（脚本直出，纯数据）

| # | Title | Author | Date | Venue | Code/Resource | Source |
|---|-------|--------|------|-------|---------------|--------|

## 附录：model_knowledge 补充候选（AI，可能含 uncertain 条目）
```

## 各部分规范

### 报告头

- **frontmatter**（至少）：`title` / `query` / `sources` / `year_range` / `total_hits`（去重前）/ `unique_papers`（去重后）/ `generated_at` / `generator: "lusca-paper-search@2.0.0"`。
- **一句话总览**：写明 query、年份、命中来源数、去重后篇数，并显式提示「全部 M 篇列于下方索引表，请扫览确认无遗漏」——保证用户不跳过索引。

### 一、研究导览（AI 产出）

> 数据依据：脚本输出的 `===DATA===` JSON（含完整 abstract / citation_count / year / venue）。AI 据此分析，克制展开。

**1. 技术发展脉络**
- 用 mermaid `flowchart TD`：节点为关键论文或方法名（建议标注 `[序号]`），边为演进关系，按时间自上而下分层（奠基在上，新兴在下）。
- 图下附三五句文字：起点（奠基工作）→ 关键转折 → 当前主流 → 新兴方向；点出主导会议与引用量级随时间的变化。不展开单篇细节。

**2. 研究热点**
- 跨全部命中聚类 3–6 个主题，每行一字段：
  - `Theme`：主题名
  - `描述`：一行说明
  - `代表论文`：索引表序号，如 `[1][3]`
  - `趋势`：↑ 上升 / → 平稳 / ↓ 降温
  - `counts`：该主题聚类内论文数
- 热点判定参考聚类内论文数、citation_count 与时间分布。

**3. 推荐阅读**
- 与用户原始 query 最相关、最有影响力的 3–5 篇，按阅读路径排序（奠基 → 最新）。
- 每篇：`[序号] 标题 —— 一行理由`。理由结合语义相关度、`citation_count`、会议声望——**原 Score 的判断融入此处**，不再单列分数列。
- model_knowledge 来源中浮出的、API 漏掉的奠基文，可在此处提及并标注「需核实」。

### 二、完整索引（脚本产出）

- 一张合并 markdown 表格，列出跨源去重后**全部**论文，全局连续编号。
- 字段与规范：

| 列 | 规范 |
|----|------|
| `#` | 全局连续序号，与 `===DATA===` JSON 列表下标 +1 一一对应 |
| `Title` | 论文标题，**可点击链接**指向 `url`；无 `url` 时纯文本（罕见，不丢弃以保完整） |
| `Author` | 作者列表，超过 3 人用 `et al.`（如 `A, B, C et al.`） |
| `Date` | `publication_date` 取 `YYYY-MM`（无则展示 `year`，再无则 `—`） |
| `Venue` | `venue` 字段，空则 `—` |
| `Code/Resource` | 取自 `code_links`，逐个可点击（`[code](...)`）；无则 `—` |
| `Source` | `sources` 字段全部命中来源，主来源在前，逗号分隔（如 `arxiv, semantic_scholar`） |

- **排序**：source 规范顺序 `semantic_scholar → open_alex → arxiv → openreview → crossref → dblp → deepxiv → sciverse`，组内 `publication_date` 降序（新优先；不依赖 citation，避免 arXiv 恒 0 全沉底）。无 `publication_date` 者排组末。
- 某来源 0 命中：不在索引表占行，仅在报告头总览里隐含（命中来源数体现）。
- 脚本运行错误：原样打到 stderr，AI 原样上报，绝不隐瞒。

### 附录：model_knowledge 补充候选

- CLI 返回后，AI 从训练数据回忆 0–10 篇匹配 query 与年份、且未已被 API 命中的论文，作为**附录**列出（不再作为索引表的一行）。
- 字段精简：`标题(检索链接) | 主要作者 | 年份 | venue | 一行相关性理由`，可疑条目标 `(uncertain — verify)`。
- 与 API 结果去重；不足 5 篇可少给或不给——诚实优先，绝不虚构。

### 导览 ↔ 索引闭环

- 导览（脉络节点 / 热点代表论文 / 推荐阅读）统一用 `[序号]` 引用索引表。
- 序号稳定性由脚本保证：`===DATA===` JSON 列表顺序 ≡ `===TABLE===` 表格行顺序；AI 以 JSON 下标 +1 作为引用序号。

## 脚本改造：`scripts/search_papers.py`

### 聚合输出变更

- `_dedup_cross_source()` 之后，**新增一步**：把 `dict[source, list[paper]]` 扁平化为单一 `list[paper]`，按上述排序规则排序。每条 paper 的 `sources` / `code_links` 字段维持现有去重逻辑。
- `search_papers()` 函数返回值由 `dict[source, list[paper]]` **改为** `list[paper]`（扁平、去重、排序）。这是 breaking，同步更新 `references/programmatic_api.md`。
- 新增内部函数 `_flatten_and_sort(deduped_results) -> list[paper]`，封装扁平化 + 排序。

### CLI 输出（`__main__`）

- 去掉「按来源分组打印」逻辑。
- 一次运行输出两段，用稳定分隔标记，AI 一次拿全：

```
===DATA===
<扁平 JSON 数组，每条含全字段：title, authors, year, abstract, url, venue,
 citation_count, publication_date, source, sources, code_links>

===TABLE===
| # | Title | Author | Date | Venue | Code/Resource | Source |
|---|-------|--------|------|-------|---------------|--------|
| 1 | [..](url) | .. | .. | .. | .. | .. |
...

Total: <M> unique papers (<H> hits before dedup) from <K> sources.
```

- DATA 段供 AI 读做导览分析（abstract / citation_count 在此）；TABLE 段供 AI 原样贴报告。
- 末行 `M` = 去重后篇数（填 frontmatter `unique_papers`），`H` = 去重前命中总数（填 `total_hits`），`K` = 有命中的来源数。`H` 在扁平化前由各来源论文数求和得到。
- 两段顺序一致（DATA[i] 对应 TABLE 第 i+1 行），保证序号闭环。
- 保留现有 CLI 参数（`--query` / `--start-year` / `--end-year` / `--max-papers` / `--sources` / `--no-parallel` / `--start-date` / `--end-date`）。

### 不动的部分

- 各来源脚本（`search_papers_by_*.py`）**不改**：仍返回各自的 `list[paper]`，字段不变。
- `_dedup_cross_source()` / `_extract_code_links()` / `_filter_by_date_range()` 逻辑不变，只在下游接扁平化。

## 砍掉的内容（两原理裁员）

| 砍掉 | 理由 |
|------|------|
| 分来源多张表 | 合并为单表，去分层 |
| Score 列 | AI 主观分；判断融入「推荐阅读」理由 |
| Citations 列（展示） | 不展示；`citation_count` 留 dict 供 AI |
| abstract 列 | 详情非索引，妨碍扫览；JSON 里保留供 AI |
| Overview 节 | 并入报告头一句话总览 |
| Keywords frequency | 与研究热点重叠，机械统计价值低 |
| Most cited by accepted paper | 与推荐阅读重叠 |
| Most cited by first author | 偏学者分析，偏离检索目的 |
| model_knowledge 独立表 | 无 JSON；移为附录 |

## 受影响文件

| 文件 | 改动 |
|------|------|
| `skills/lusca-paper-search/SKILL.md` | 重写「输出给用户」「输出 schema」「model_knowledge 源」「重要约定」「示例」等节；frontmatter `version: "2.0.0"` |
| `skills/lusca-paper-search/scripts/search_papers.py` | 扁平化 + 排序；CLI 输出 DATA/TABLE 两段；函数返回值改 `list[paper]` |
| `skills/lusca-paper-search/assets/report-template.md` | 重写为新二段式骨架（导览 + 索引 + 附录） |
| `skills/lusca-paper-search/references/programmatic_api.md` | 返回值示例改 `list[paper]` |
| `skills/lusca-paper-search/CHANGELOG.md` | 追加 2.0.0 条目（Changed / Removed） |

## 验证清单

1. `search_papers.py --help` 正常；`search_papers()` 返回 `list[paper]`、已去重、已按规范排序。
2. CLI 运行一次，输出含 `===DATA===`（JSON 数组，含 abstract/citation_count）与 `===TABLE===`（合并表，表头 7 列）两段，且 DATA 顺序与 TABLE 行序一致。
3. 表格 `#` 列自 1 起连续；`source` 列多源命中者显示多来源；无 `publication_date` 者排组末。
4. 各来源脚本未改动，仍可独立 `python search_papers_by_arxiv.py ...` 运行。
5. `SKILL.md` 正文与新 `report-template.md` 结构一致：报告头 → 导览三节 → 索引表 → model_knowledge 附录。
6. 落盘一份示例报告到 `./outputs/lusca-paper-search/`，内联展示完整（索引表不截断、导览三节齐全）。
7. 新开 cc 会话，触发话术（「搜一下近两年 diffusion policy 的论文」）命中本 skill，产出符合新体系。

## 不做项

- 不改各来源脚本的字段抓取逻辑（tags 已决定不要；abstract/citation_count 现有字段足够）。
- 不做 eval / 基准（延续上位设计）。
- 不改 `_dedup_cross_source` / `_extract_code_links` 核心算法。
- 不触碰其它 skill（`lusca-paper-read` / `lusca` / polish 等）。
