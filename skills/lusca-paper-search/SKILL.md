---
name: lusca-paper-search
description: >-
  多源并行文献检索：arXiv/DBLP/OpenAlex/OpenReview/Semantic Scholar/Crossref/
  DeepXiv/Sciverse 八大开源 API + 模型自身知识，覆盖英文 CS/理工与顶会
  (NeurIPS/ICLR/ICML)。用户提到搜论文、查文献、找 related work、prior art、
  近 X 年某主题发表时使用本技能。
version: "1.0.1"
user-invocable: true
argument-hint: "[可选：检索主题 / 年份范围 / 指定来源]"
allowed-tools: Read, Write, Bash, WebSearch
---

# lusca-paper-search — 多源并行文献检索

**核心理念：文献检索的价值在于完整召回——漏掉一篇可能意味着漏掉一条引用或一次重复研究。**

通过 `${SKILL_DIR}/scripts/search_papers.py` 在 **arXiv / DBLP / OpenAlex /
OpenReview（NeurIPS/ICLR/ICML）/ Semantic Scholar / Crossref / DeepXiv /
Sciverse** 八大开源 API 之间**并发**检索，并辅以模型自身知识源。结果按来源分组，
全部展示后再给综合摘要。

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

`search_papers()` 返回 dict，来源名 → 论文 dict 列表：

```
{
  "arxiv": [
    {
      "title": str,
      "authors": [str, ...],
      "year": int,
      "abstract": str,
      "url": str,
      "venue": str,
      "citation_count": int,
      "publication_date": str,
      "source": str
    }, ...
  ],
  "semantic_scholar": [...],
  ...
}
```

CLI 按来源分组打印，并附每源论文数汇总。

---

## 输出给用户

检索完成后，**展示每个来源的每一篇论文**，顺序为：
Semantic Scholar、OpenAlex、arXiv、OpenReview、Crossref、DBLP、Model Knowledge。
随后给出综合摘要。

**为何要完整召回**：调用本技能的用户在做文献综述、related-work 调研或 prior-art 核查。
价值来自看到完整命中集——漏掉一篇可能意味着漏掉一条引用或一次重复研究。摘要用来**补充**
完整表格，而非替代；不要"为节省篇幅"把结果折叠成摘要。用户能自己略读，但无法找回从未展示的论文。

### Step 1：展示每个来源的全部结果

**每个来源**用一张 **markdown 表格**展示全部论文，含标题、日期、会议、引用数。
每个来源单列一节，例如：

```
### arXiv (N papers)

| #   | Title       | Date    | Venue   | Citations |
|-----|-------------|---------|---------|-----------|
| [1](paper url) | Title here | 2024-03 | NeurIPS | 42 |
| [2](paper url) | Title here | 2023-11 | ICLR    | 10 |
```

某来源返回 0 结果时，**显式标注**（如"### OpenReview (0 papers) — 本窗口内无匹配"）。
检索过程出错时，脚本会把错误打到 stderr——**原样上报给用户，绝不隐瞒**。

### Step 2：全部结果的综合摘要

展示完所有论文后，给出**综合摘要**，按以下**固定顺序**的七节：

1. **Overview**：所用 query、年份范围、命中总数。一两句话框定语料覆盖范围。
2. **Trends**：时间分布（如"2024 年关注度激增"）、主导会议、方法演进、反复出现的作者群/实验室。
3. **Key themes**：跨全部结果的 3–6 个主要研究主题/聚类，每个配一行描述与 2–3 个代表论文编号。
4. **Keywords frequency**：从标题/摘要抽取的最高频技术术语/概念表，含计数，格式 `| Keyword | Count |`，取前 5。
5. **Most cited by accepted paper**：跨全部来源被引最高的 5 篇 accepted 论文，按引用数排序，格式 `| Rank | Title | Year | Citations |`。
6. **Most cited by first author**：按本结果集内累计引用数排名前 5 的第一作者，格式
   `| Rank | Author | Papers in set | Total citations |`。**Author 列只填姓名**（如 `Jane Doe`），
   不得附加论文标题、单位、会议等任何其它信息——论文数与引用总数各有其列。
7. **Recommendations for reading**：与用户原始 query 最相关、最有影响力的 3–5 篇，按阅读路径排序
   （奠基 → 最新），每篇配一行理由。

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

用与其它来源相同的表格布局，但 URL 列可链接到检索查询（如 arXiv 或 Google Scholar 检索）
而非规范论文 URL，因为无经验证链接：

```
### Model Knowledge (N papers, may include uncertain entries)

| #   | Title       | Year | Venue   | Notes |
|-----|-------------|------|---------|-------|
| [1](https://scholar.google.com/scholar?q=Title) | Title here | 2018 | NeurIPS | 奠基性；常被近期 X 工作引用 |
| [2](...) | Title here | 2024 | ICLR | (uncertain — verify) |
```

用"Notes"列替代"Citations"列，因为无法从记忆给出可靠引用数。

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

- **落盘检索报告。** 完成检索后，写一份 markdown 文件到
  `./outputs/lusca-paper-search/{YYYYMMDDHHmmss}_{slug}.md`。
  - 内容：完整的 **"Step 1：展示每个来源的全部结果"** 表格，紧接 **"Step 2：综合摘要"**，
    顺序如此，**不截断**。
- **完整报告同步内联展示。** 把完整详细报告内联返回——每篇论文、每张表，外加分析与推理。
  绝不把表格折叠成摘要，绝不"为省篇幅"缩写结果。
- **绝不追问确认。** 全部输入自动推断（见"输入"节）。首轮即跑。
- **错误原样上报。** 某来源失败时，把 stderr 消息如实报给用户，而非隐瞒或盲目重试。

---

## Reference 文件索引

| 文件 | 何时 Read |
|------|-----------|
| `references/sources.md` | 需要了解各 API 源依赖、Token 要求、失败模式时 |
| `references/programmatic_api.md` | 需要直接调用 `search_papers()` 函数、消费结构化 dict 时 |

---

## 版本管理

**当前版本**：见 frontmatter `version` 与 `CHANGELOG.md` 最新条目。

每次修改本技能**必须**：
1. 递增 `SKILL.md` frontmatter `version`
2. 写入 `CHANGELOG.md`（Added / Changed / Fixed / Removed）
3. 向用户说明版本号与变更要点

版本号规则：MAJOR（流程/输出规范 breaking）/ MINOR（新来源、新 prompt、新 reference）/ PATCH（措辞、typo）。
