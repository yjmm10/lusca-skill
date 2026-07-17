---
name: lusca-paper-search
description: >-
  多源并行文献检索：arXiv/DBLP/OpenAlex/OpenReview/Semantic Scholar/Crossref/
  DeepXiv/Sciverse 八大开源 API + 模型自身知识，覆盖英文 CS/理工与顶会
  (NeurIPS/ICLR/ICML)。用户提到搜论文、查文献、找 related work、prior art、
  近 X 年某主题发表时使用本技能。
version: "2.0.1"
author: lusca
user-invocable: true
argument-hint: "[可选：检索主题 / 年份范围 / 指定来源]"
allowed-tools: Read, Write, Bash, WebSearch
---

# lusca-paper-search — 多源并行文献检索

**核心理念：文献检索的价值在于完整召回——漏掉一篇可能意味着漏掉一条引用或一次重复研究。**

通过 `${SKILL_DIR}/scripts/search_papers.py` 在 **arXiv / DBLP / OpenAlex /
OpenReview（NeurIPS/ICLR/ICML）/ Semantic Scholar / Crossref / DeepXiv /
Sciverse** 八大开源 API 之间**并发**检索。脚本把结果**合并成一张表**（完整索引，
纯数据、脚本直出）；AI 据此产出**研究导览**（发展脉络 / 研究热点 / 推荐阅读）。

## 路径约定

- **`${SKILL_DIR}`**：本技能根目录（含本 `SKILL.md` 的文件夹）。Claude Code 下等价于
  `CLAUDE_SKILL_DIR`；经 symlink 发现层加载时即为 `skills/lusca-paper-search/`。
- 为简洁起见，下文用 `$SEARCH` 指代 `${SKILL_DIR}/scripts/search_papers.py`。
  **始终用绝对路径调用**，避免 `cd scripts && ...` 在不同 cwd 下失效。
- 检索报告默认落盘到 `./outputs/lusca-paper-search/{YYYYMMDDHHmmss}_{slug}.md`（用户指定路径时从其指定）。

## 与体系内其它 skill 的分工

| 场景 | 使用技能 |
|------|----------|
| **文献检索 / related work / prior art** | **本技能（lusca-paper-search）** |
| 精读一篇论文 / 批判性评估 / 阅读笔记 | `lusca-paper-read` |
| 已有初稿，润色论文表达与结构 | `paper-polish-skill` |
| 中国发明专利全流程 | `patent-skills` |
| 复盘本会话中 skill 暴露的问题 | `lusca` |

---

## 触发条件

- 明确提及：搜论文、查文献、查找文献、找 related work、prior art、近期发表、近 X 年某主题
- 英文：find papers, search papers, literature search, prior art, recent publications on X
- 斜杠指令：`/lusca-paper-search`、`/搜论文`
- 提及具体会议：NeurIPS / ICLR / ICML / ACL / CVPR 等

**不触发**：用户只是要查单个已知 DOI/URL 的详情（直接 WebFetch 即可），或在 `paper-polish-skill` 润色流程中引用已有文献（无需重新检索）。

---

## 输入（全部自动推断——绝不向用户追问确认）

从用户消息中自动推导，首轮即跑：

- **query**：把用户问题改写为一个聚焦的检索短语。
- **start_year**（int）：用户给出年份则直接用；说"近 2 年"则从今天回推。默认：2 年前。
- **end_year**（int）：默认：当前年份。
- **max_papers**（int）：每个来源返回条数。默认：10。
- **sources**：检索哪些来源。默认：8 个 API 源 + model_knowledge，按以下规范顺序（信号由高到低，让最优结果先渲染）：
  `semantic_scholar open_alex arxiv openreview crossref dblp deepxiv sciverse model_knowledge`。
  仅当用户明确要求时才收窄来源。

---

## 如何运行

首选：直接调用 CLI。基本检索：

```bash
python "$SEARCH" \
    --query "<QUERY>" \
    --start-year <YYYY> \
    --end-year <YYYY> \
    --max-papers 10
```

限制特定来源：

```bash
python "$SEARCH" \
    --query "<QUERY>" \
    --start-year 2024 --end-year 2026 \
    --sources arxiv semantic_scholar openreview
```

关闭并发（极少需要）：

```bash
python "$SEARCH" \
    --query "<QUERY>" \
    --start-year 2024 --end-year 2026 \
    --no-parallel
```

需要消费结构化 dict 而非 CLI 文本时，可直接调用函数（较少需要，见 `references/programmatic_api.md`）。

---

## 有效来源

| 来源 | Key |
|:---|:---|
| arXiv | `arxiv` |
| DBLP | `dblp` |
| OpenAlex | `open_alex` |
| OpenReview | `openreview` |
| Semantic Scholar | `semantic_scholar` |
| Crossref | `crossref` |
| DeepXiv（arXiv/bioRxiv/medRxiv 语义检索） | `deepxiv` |
| Sciverse（结构化元数据检索） | `sciverse` |
| 模型知识（LLM 自回忆，无 API 调用） | `model_knowledge` |

各来源的依赖、Token 要求与失败模式见 `references/sources.md`。

---

## 输出 schema

`search_papers()` 返回**扁平 `list[dict]`**，跨源去重后按 source 规范顺序、组内
`publication_date` 降序排列。每条 paper：

```
{
  "title": str,
  "authors": [str, ...],
  "year": int,
  "abstract": str,
  "url": str,
  "venue": str,
  "citation_count": int,
  "publication_date": str,
  "source": str,                 # 主来源（信息最全那条的原 source）
  "sources": [str, ...],        # 跨源去重后所有命中来源（含主来源）
  "code_links": [str, ...]      # 从摘要提取的 GitHub / HuggingFace / 项目页链接
}
```

CLI 一次输出两段（AI 一次拿全）：

- `===DATA===`：上述扁平 JSON 数组，**含完整 abstract / citation_count** → 供 AI 读做导览分析。
- `===TABLE===`：合并 markdown 表格（7 列）→ 供 AI 原样贴报告。
- 末行：`Total: <M> unique papers (<H> hits before dedup) from <K> sources.`

两段顺序一致：`===DATA===` 第 i 条 ≡ `===TABLE===` 第 i+1 行 → 导览用 `[序号]` 引用表格、序号稳定。

---

## 去重与链接提取（脚本自动）

聚合器在返回前对全部来源做两道自动处理，LLM 无需手工干预：

1. **跨源标题去重**：标题归一化（小写、去标点、压缩空白）后相同者合并为一条，
   **保留信息最全的版本**（按字段完整度加权：摘要 3、URL 2、其余元数据各 1；
   `citation_count=0` 视为有效字段）。合并后的记录在其主来源下展示，并以 `sources`
   字段记录所有命中来源。无标题的论文不参与去重，原样保留。
   - **仅合并标题相同的跨源重复项，不按分数删除任何论文**（见 §重要约定）。
2. **代码 / 项目链接提取**：对保留的每条记录，从摘要中正则抽取 GitHub、HuggingFace、
   GitLab、Bitbucket 等链接，存入 `code_links`，供 Step 1 的 Code/Resources 列展示。

> 这两步由 `search_papers.py` 完成；**语义相关度评分与技术脉络分析**是 LLM 的工作（见下文），不进脚本。

---

## 输出给用户

检索完成后，输出顺序为：**研究导览（AI 分析）先行 → 完整索引（脚本直出）附后 →
model_knowledge 附录**。认知先行，完整索引保证不漏召回。

**为何要完整召回**：调用本技能的用户在做文献综述、related-work 调研或 prior-art 核查。
价值来自看到完整命中集——漏掉一篇可能意味着漏掉一条引用或一次重复研究。导览用来**补充**
完整索引，而非替代；不要"为节省篇幅"把索引折叠。用户能自己略读，但无法找回从未展示的论文。

### 第一步：跑脚本，拿 DATA + TABLE

```bash
python "$SEARCH" --query "<QUERY>" --start-year <YYYY> --end-year <YYYY> --max-papers 10
```

输出含 `===DATA===`（JSON）与 `===TABLE===`（markdown 表）。**TABLE 原样采用**，不重排、
不分析、不打分。索引表字段：

| # | Title | Author | Date | Venue | Code/Resource | Source |
|---|-------|--------|------|-------|---------------|--------|

- **#**：全局连续序号（与 DATA 下标 +1 一致）。
- **Title**：论文 URL 的可点击链接；无 URL 时纯文本。
- **Author**：≤3 人全列；>3 人列前 3 加 `et al.`。
- **Date**：`YYYY-MM`；无则 `year`；再无则 `—`。
- **Code/Resource**：取自 `code_links`（GitHub→`[code]`、HuggingFace→`[model]`）；无则 `—`。
- **Source**：所有命中来源，主来源在前，逗号分隔。

某来源检索出错：脚本把错误打到 stderr——**原样上报，绝不隐瞒**。

### 第二步：研究导览（AI 分析，认知先行）

读完 `===DATA===` 后，按**固定顺序**写三节。所有论文引用用索引表 `[序号]`。

1. **技术发展脉络**：用 mermaid `flowchart TD`，节点为关键论文/方法（标 `[序号]`），边为
   演进关系，按时间自上而下分层（奠基在上、新兴在下）。图下附三五句：起点（奠基工作）→
   关键转折 → 当前主流 → 新兴方向；点出主导会议与引用量级随时间的变化。**克制，不展开单篇**
   （深度精读是 `lusca-paper-read` 的事）。
2. **研究热点**：跨全部命中聚类 3–6 主题，每行 `Theme | 一行描述 | 代表论文[序号] | 趋势(↑→↓)
   | counts(该主题论文数)`。判定参考聚类内论文数、`citation_count` 与时间分布。
3. **推荐阅读**：与用户原始 query 最相关、最有影响力的 3–5 篇，按奠基 → 最新排序，每篇
   `[序号] 标题 —— 一行理由`。理由结合语义相关度、`citation_count`、会议声望——**这是评分
   判断的归宿**，不再单列分数列。

---

## model_knowledge 源

`model_knowledge` 与其它来源不同：无 API、无脚本调用。CLI 检索返回后，从自身训练数据中
再回忆 5–10 篇匹配 query 与年份范围的论文，作为独立来源呈现。

### 为何纳入

API 检索高精度但低召回，在两种可预见场景下尤其明显：
1. **奠基性旧文**：从业者总引用但关键词检索漏掉的（如检索某近期变体时漏掉原始 BERT / ResNet 论文）。
2. **跨学科经典**：活在 API 索引较差的会议里。

模型回忆补充 API，浮现那些"人人都知道"但新鲜关键词检索未必返回的论文。

### 如何填充

CLI 跑完后：

1. 回顾你对 query 主题的所知。
2. 列出至多 10 篇符合 query 与年份范围的训练数据论文，含：标题、主要作者、年份、会议、一行相关性理由。
3. 与 API 结果**去重**——若某篇已出现在任一 API 来源，不要在 `model_knowledge` 下重复。
4. **诚实标注置信度**。model_knowledge 列无引用数、无实时 URL；若不确定某篇是否确切如你记忆所是，
   在表中标注 `(uncertain — verify)`，而非当作已确认。

### 为何诚实至关重要

虚构论文标题是本任务的经典 LLM 失败模式。一个假的"Smith et al., 2023, NeurIPS"在 markdown
表里与真实的一模一样，用户无从分辨。本来源的目的是浮现 **API 漏掉的真实论文**，而非凑数。
若无法以合理置信度回忆 ≥5 篇，就少给；model_knowledge 节为空是诚实且可接受的。

### 展示格式

model_knowledge **不进索引表**（无 JSON、无脚本介入）。CLI 跑完后，AI 把回忆到的论文作为
报告末尾的**附录**列出，与 API 索引表分离：

```
## 附录：model_knowledge 补充候选（N papers，可能含 uncertain 条目）

| Title | 主要作者 | Year | Venue | 一行相关性理由 |
|-------|---------|------|-------|---------------|
| [Title](https://scholar.google.com/scholar?q=Title) | Jane Doe | 2018 | NeurIPS | 奠基性；常被近期 X 工作引用 |
| [Title](...) | .. | 2024 | ICLR | (uncertain — verify) |
```

标题可链接到检索查询（Google Scholar / arXiv 检索）而非规范 URL，因为无经验证链接。

---

## 示例

用户："找一下 2023 到 2024 年机器人 diffusion policy 的论文。"

执行（`$SEARCH` 见"路径约定"）：
```bash
python "$SEARCH" \
    --query "diffusion policy robotics" \
    --start-year 2023 --end-year 2024 \
    --max-papers 10
```

只检索特定来源：
```bash
python "$SEARCH" \
    --query "diffusion policy robotics" \
    --start-year 2023 --end-year 2024 \
    --sources arxiv openreview semantic_scholar \
    --max-papers 10
```

随后读输出并按上述规则汇总。

---

## 重要约定

- **落盘检索报告。** 完成检索后，按 `assets/report-template.md` 的模板写一份 markdown 文件到
  `./outputs/lusca-paper-search/{YYYYMMDDHHmmss}_{slug}.md`。
  - **顶部必须有 frontmatter**：至少含 `title`、`query`、`sources`、`year_range`、`total_hits`
    （去重前，取 CLI 末行 `H`）、`unique_papers`（去重后，取 `M`）、`generated_at`、
    `generator`（本技能名与版本）。
  - 正文顺序：**研究导览（三节）→ 完整索引（脚本 TABLE 原样）→ model_knowledge 附录**，不截断。
- **表格纯数据。** 索引表 = 脚本 `===TABLE===` 原样采用，AI 不重排、不打分、不增删列。
  打分/聚类/脉络判断**只在导览里**出现。
- **完整报告同步内联展示。** 把完整报告内联返回——导览三节 + 完整索引表 + 附录，绝不折叠。
- **去重 ≠ 删除。** 脚本跨源去重只合并标题相同的重复条目（保留信息最全的），不丢弃任何论文。
- **绝不追问确认。** 全部输入自动推断（见「输入」节）。首轮即跑。
- **错误原样上报。** 某来源失败时，把 stderr 消息如实报给用户，而非隐瞒或盲目重试。
- **文末出处块。** 落盘报告正文结尾附一行出处（遵 CLAUDE.md「文档输出规范」）：`> 作者：lusca ｜ 版本：lusca-paper-search v<version> ｜ 出处：https://github.com/yjmm10/lusca-skill/tree/main/skills/lusca-paper-search`

---

## Reference 文件索引

| 文件 | 何时 Read |
|------|-----------|
| `references/sources.md` | 需要了解各 API 源依赖、Token 要求、失败模式时 |
| `references/programmatic_api.md` | 需要直接调用 `search_papers()` 函数、消费结构化 dict 时 |
| `assets/report-template.md` | 落盘检索报告时，复制为本次报告骨架（含 frontmatter） |

---

## 版本管理

**当前版本**：见 frontmatter `version` 与 `CHANGELOG.md` 最新条目。

每次修改本技能**必须**：
1. 递增 `SKILL.md` frontmatter `version`
2. 写入 `CHANGELOG.md`（Added / Changed / Fixed / Removed）
3. 向用户说明版本号与变更要点

版本号规则：MAJOR（流程/输出规范 breaking）/ MINOR（新来源、新 prompt、新 reference）/ PATCH（措辞、typo）。
