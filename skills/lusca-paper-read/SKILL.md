---
name: lusca-paper-read
description: >-
  精读一篇学术论文：输入 PDF / 链接 / arXiv ID / 文本，产出结构化阅读笔记（核心贡献、
  方法概要、批判性评估、可复用要点）。融合六维精读框架与多视角批判（含反方最强论证），
  立足读者视角——不是给作者的 referee report。用户提到读论文、精读这篇、帮我看看这篇论文、
  这篇讲了啥、值不值得读、paper read、read this paper 时使用本技能。
version: "1.5.0"
user-invocable: true
argument-hint: "[论文路径 / arXiv ID / URL / 粘贴文本]"
allowed-tools: Read, Write, Bash, WebFetch
---

# lusca-paper-read — 论文精读与批判性评估

**核心理念：读懂一篇论文，不是复述它说了什么，而是判断它为什么重要、哪里可信、哪里可疑、对我有什么用。**

输入一篇论文（PDF / `.tex` / `.md` / arXiv ID / URL / 粘贴文本），按**六维精读框架**逐层
拆解，再用**五个批判性视角**（含反方最强论证）压力测试，最终落盘一份结构化阅读笔记。
立足**读者视角**：目标是让自己（读者）真正吃透这篇论文并留下可复用的笔记，而非给作者写
referee report 或 accept/reject 决定。

## 与体系内其它 skill 的分工

| 场景 | 使用技能 |
|------|----------|
| 文献检索 / 找论文 / related work | `lusca-paper-search` |
| **精读一篇论文 / 批判性评估 / 阅读笔记** | **本技能（lusca-paper-read）** |
| 论文润色（已有初稿） | `paper-polish-skill` |
| 中国发明专利全流程 | `patent-skills` |
| 复盘本会话中 skill 暴露的问题 | `lusca` |

**与 `lusca-paper-search` 的衔接**：检索产出候选论文清单后，挑出值得深读的那篇，交给本技能
精读。检索负责"找全"，本技能负责"读透"。

---

## 触发条件

- 明确提及：读论文、精读、帮我看看这篇论文、这篇讲了啥、解读一下这篇、值不值得读、阅读笔记
- 英文：read this paper, paper read, deep read, walk me through this paper, is this paper worth reading
- 斜杠指令：`/lusca-paper-read`、`/读论文`
- 提供了 arXiv ID / 论文 URL / PDF 路径并希望理解其内容

**不触发**：
- 只想检索相关论文（→ `lusca-paper-search`）
- 已有初稿要润色（→ `paper-polish-skill`）
- 只想知道一个已知事实 / DOI 的详情（直接 WebFetch 即可，无需精读流程）
- 要给作者写 referee report 用于投稿决策（本技能是读者视角；可参考产出自行改写）

---

## 输入

论文来源**从 `$ARGUMENTS` 与上下文自动解析**；仅当完全找不到论文时，**追问一次**论文位置
（读论文没有输入则无法进行，这是唯一允许的追问）：

- **文件路径**：`/path/to/paper.pdf`、`./papers/foo.tex`、`bar.md` —— 用 `Read`（PDF 支持分页）
- **arXiv ID**：`2310.12345` 或 `arXiv:2310.12345` —— 优先 `WebFetch` 抓 `arxiv.org/html/<id>`
  （全文 HTML，最适合精读，且便于提取图表 URL 嵌入笔记）；无 HTML 版则下载 PDF 用 `Read`
  分块读；`abs` 页面仅补元信息
- **URL**：任意论文页面 —— `WebFetch` 抓取
- **粘贴文本**：用户直接把标题 + 摘要 / 正文贴进对话 —— 直接读

**读多深**（自动推断，不追问）：
- 短文（abstract + 4 页以内正文）：全文通读
- 长文（>10 页 PDF）：分块读（`Read` 的 `pages` 参数，每次 5 页），必读 abstract / intro /
  method / results / conclusion，related work 与 appendix 按需扫读
- 用户指明"只看方法"/"只看实验"时，聚焦对应章节但仍输出完整笔记骨架

---

## 主流程

```
locate → read-full → six-dim-read → critique-lenses → note → save
```

1. **定位论文**：解析 `$ARGUMENTS`；找不到 → **追问一次**论文位置后继续
2. **读全文**：按"读多深"策略读完；长 PDF 分块（`Read` 的 `pages` 参数，每次 5 页）；
   留意架构图与关键结果图（记下其 URL / 页码 / Figure 号，供 2.1 / 3.1 嵌入）
3. **六维精读（指导）**：`Read` `references/reading-dimensions.md`，按六维入口**审视**论文——
   这是解读时的内化指导，**不是笔记的输出结构**；不必逐维对号入座填表
4. **批判性视角（指导）**：`Read` `references/critique-lenses.md`，用五视角**找问题**——同样
   是指导而非输出结构；把真正有价值的发现**融入自然的批判性叙述**，不贴视角标签
5. **落盘笔记**：`Read` `assets/reading-note-template.md`，**严格对照模板逐节填写**（含 YAML
   frontmatter）；某节无内容写 `n/a` 并说明原因，**不删节**；写到
   `./outputs/lusca-paper-read/{YYYYMMDDHHmmss}_{slug}.md`（用户指定路径时从其指定）
6. **交付**：笔记路径 + 内联展示完整笔记 + 末尾一行 verdict（推荐深读 / 选读 / 跳过）

---

## 六维精读框架（摘要）

**定位**：六维是解读时的**审视入口**（指导你全面看论文），不是笔记的输出结构——笔记的批判性评估写自然叙述，不逐维对号入座。详见 `references/reading-dimensions.md`。

| 维度 | 回答的问题 | 读者收益 |
|------|-----------|----------|
| 1. 定位与贡献 | 研究问题是什么？核心 claim？与已有工作差在哪？ | 知道这篇在领域里的位置 |
| 2. 方法与设计 | 怎么做的？关键假设？数据/实验设置？ | 能判断方法是否靠谱、能否复用 |
| 3. 结果与证据 | 主要发现？证据强度？结论是否被数据支撑？ | 区分"证明了"与"暗示了" |
| 4. 逻辑与论证 | 论证链完整吗？有跳跃/过度泛化吗？反方最强反驳？ | 不被流畅写作带偏 |
| 5. 写作与呈现 | 清晰吗？图表自洽？notation 一致？ | 评估可信度的一个侧面信号 |
| 6. 可复用性与影响 | 对我有什么用？可借鉴的方法/数据/idea？值得引用吗？ | 把论文变成自己的资产 |

---

## 批判性视角（摘要）

**定位**：五视角是解读时的**挑刺方法**（指导你找问题），不是笔记的输出结构——发现融入批判性叙述，不贴视角标签、不对号入座。详见 `references/critique-lenses.md`。五个视角作为审视思路：

| 视角 | 做什么 |
|------|--------|
| 假设压力测试 | 找出论文成立所依赖的关键假设，逐个问"若不成立会怎样" |
| 反方最强论证 | 站在对立面，构造对论文核心 claim 最有力的反驳（吸收自 academic-paper-reviewer 的 Devil's Advocate） |
| cherry-picking / 确认偏误检测 | 检查是否只挑有利结果、隐藏不利实验、措辞引导 |
| "so what" 测试 | 若论文结论完全成立，对领域/实践到底改变了什么 |
| 替代解释 | 同样的结果有没有别的解释（混杂、选择偏倚、baseline 偏弱） |

---

## 输出与存放

- **目录**：`./outputs/lusca-paper-read/`（与 `lusca-paper-search` 的输出目录平级）；用户指定路径时从其指定
- **命名**：`{YYYYMMDDHHmmss}_{slug}.md`，slug 取自论文标题或 arXiv ID
  - 示例：`20260714143022_diffusion-policy-robotics.md`
- **模板**：`assets/reading-note-template.md`（复制即用）；笔记带 YAML frontmatter
  （`title`/`authors`/`year`/`venue`/`arxiv`/`doi`/`read_date`/`verdict`/`slug`/`tags`），
  便于后续按 verdict / tag 检索
- **内联展示**：落盘后把完整笔记内联返回给用户，不折叠、不截断

---

## 阅读笔记结构

笔记结构与字段**以 `assets/reading-note-template.md` 为准**——生成时严格对照模板逐节填写。
元信息**只写在 YAML frontmatter**，正文不重复。主体节：

- **TL;DR**：2–3 句可独立传播的总结（核心 claim + 关键证据 + 主要 caveat）
- **1. 研究内容**（含小点：1.1 研究问题与动机 / 1.2 核心贡献 / 1.3 相关工作脉络——后者用 mermaid 流程图展示相关工作发展到本文的过程）
- **2. 方法概要**（含 2.1 架构图——mermaid 重绘简化架构，可附原图链接）：方法路线、关键步骤、关键假设、数据/实验设置
- **3. 关键结果**（含 3.1 关键结果图——引用原文图表 URL 或用表格重现关键数据）：主要发现、证据强度、最支撑结论的证据
- **4. 批判性评估与价值**（合并细分）：4.1 批判性评估（自然叙述，六维+五视角作内化指导）+ 4.2 Limitations 与复现性 + 4.3 可复用与后续
- **Verdict**：推荐深读 / 选读 / 跳过 + 理由

第 1–3 节是论文内容解读，事实层、**饱满不可简化**；第 4 节是读者评估。

---

## 模板使用约定

- **元信息只在 frontmatter**：title/authors/year/venue/arxiv/doi/source/read_date/verdict/slug/tags 写进 YAML；正文不再单列元信息节
- **逐节填写，不删节**：模板每一节（含小点）都要在笔记里出现；无内容写 `n/a` 并说明原因
- **frontmatter 必填**：`title`/`read_date`/`verdict`/`slug` 必填；其它字段无则留空字符串/空数组
- **批判性评估是自然叙述**：六维与五视角是**内化指导**，不作为固定输出结构对号入座、不贴框架标签；发现融入叙述；若反方论证有力可单独引出（非强制）；综合可信度必出
- **事实 vs 评估**：第 1–3 节（研究内容 / 方法概要 / 关键结果）是客观陈述；第 4 节（批判性评估与价值）是读者评估，用"评估："前缀或明确语气区分
- **论文解读饱满、评估节细分**：研究内容 / 方法概要 / 关键结果要写足；第 4 节合并批判性评估 + Limitations/复现性 + 可复用/后续三个小点，其中 4.2/4.3 每条一行不展开
- **相关工作用流程图**：1.3 节用 mermaid 流程图展示相关工作发展到本文的脉络，节点标"工作 + 作者年份"，箭头表示发展/启发关系，本文方法作为终点突出
- **图表呈现**：2.1 架构图用 mermaid 重绘简化架构（求快速回忆、不求精确还原）；3.1 关键结果图优先嵌入原文图 URL（arXiv HTML 等来源可获取），仅有 PDF 时用 markdown 表格重现关键数据并标注"见原文 Figure/Table X"；每节挑 1–2 张最关键的，不求全
- **不确定必标**：没读懂的、臆测的，标 `(uncertain)`

## 质量底线

- **基于原文，不臆造**：每条评估尽量指到具体章节/图表/公式；读不清的地方明说"此处未读清"，绝不编造细节
- **区分事实与判断**：论文陈述的内容用客观语气，读者评估用"评估："前缀，不混为一谈
- **批判要构造性地给**：指出问题的同时给出"若要复用/借鉴此工作，需先验证 X"
- **读者视角**：不产出 accept/reject 决定，不写 referee report 语气；笔记是给自己未来回看用的
- **诚实标注不确定**：对论文某部分理解不充分时，在笔记里标 `(uncertain)`，不假装读懂
- **不替代检索**：精读中发现需要查 related work / 找更多同类论文时，引导用户用
  `lusca-paper-search`，而非自行 WebFetch 检索——本技能只读给定的一篇

---

## Reference 文件索引

| 文件 | 何时 Read |
|------|-----------|
| `references/reading-dimensions.md` | 六维精读时，各维度判据、红旗、示例 |
| `references/critique-lenses.md` | 批判性视角执行时，五视角的方法与示例 |
| `assets/reading-note-template.md` | 落盘时，复制为本次阅读笔记 |

---

## 版本管理

**当前版本**：见 frontmatter `version` 与 `CHANGELOG.md` 最新条目。

每次修改本技能**必须**：
1. 递增 `SKILL.md` frontmatter `version`
2. 写入 `CHANGELOG.md`（Added / Changed / Fixed / Removed）
3. 向用户说明版本号与变更要点
4. 本 skill 源目录或 frontmatter 有增删/重命名时，按工作区规范跑 `link-project.sh` 同步发现层

版本号规则：MAJOR（流程/输出规范 breaking）/ MINOR（新维度、新视角、新 reference）/ PATCH（措辞、typo）。
