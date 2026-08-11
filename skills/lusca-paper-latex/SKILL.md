---
name: lusca-paper-latex
description: >-
  把润色后的学术文稿（Markdown / 粘贴文本 / 已有 .tex 草稿）转成可编译的 LaTeX：
  中文稿先做学术翻译转成英文再排版，英文稿直接排版不重写内容；保护数学公式、
  \cite/\ref/\label 与自定义宏，特殊字符正确转义，标题/列表/图表/表格/引用合法映射，
  选对文档类与宏包，并实际编译验证（三平台 LaTeX 环境安装见 references/setup-latex.md）。
  绝不臆造数据/引用/论断，只转格式不改内容。用户提到转 latex、
  生成 tex、排版成 LaTeX、论文转 LaTeX、中文稿转英文 latex、导出 tex、整理成 LaTeX、
  出一份 tex 投稿、markdown to latex、convert to tex、make it a tex paper、typeset as latex
  时使用本技能——哪怕用户只说"把这篇整理成能编译的 tex"也走本技能。
version: "1.1.0"
author: lusca
user-invocable: true
argument-hint: "[润色稿文件路径 / 粘贴文本 / .tex 草稿]"
allowed-tools: Read, Write, Edit, Bash, Glob
license: CC-BY-NC-SA-4.0
---

# lusca-paper-latex — 润色稿转 LaTeX

**核心理念：把作者写好的内容忠实地搬进一份能编译的 LaTeX——只换容器，不换内容；中文稿多走一道学术翻译，英文稿原样排版。**

输入润色后的学术文稿（Markdown / 粘贴文本 / 已有 `.tex` 草稿），产出可编译的 LaTeX 文档，并**实际编译验证**。正文是中文时，先做学术翻译转成英文再排版；正文是英文时直接排版，**不重写、不润色语言**（润色是 `lusca-paper-polish` 的事）。数学公式、`\cite`/`\ref`/`\label` 与自定义宏一律保护，特殊字符正确转义，Markdown 结构合法映射到 LaTeX 环境。

本技能的定位是一位严谨的排版工兼译者——把作者已经定稿的话放进能编译的 LaTeX 骨架，中文顺手译成可投稿的英文；**不是**再次润色，**不**替作者改论断、补数据、加引用。

## 与体系内其它 skill 的分工

| 场景 | 使用技能 |
|------|----------|
| 文献检索 / 找论文 | `lusca-paper-search` |
| 精读一篇论文 / 阅读笔记 | `lusca-paper-read` |
| PDF / 图片 / DOCX 解析成 Markdown | `lusca-pdf-parse` |
| 已有初稿，润色表达 / 去 AI 腔 / 中转英 | `lusca-paper-polish` |
| **把润色稿排成可编译 LaTeX（中→英翻译 + 排版 / 英文排版）** | **本技能（lusca-paper-latex）** |
| 复盘本会话中 skill 暴露的问题 | `lusca` |

> 本技能是论文线的**旁支**下游：承接 `lusca-paper-polish` 的产出（润色稿 → LaTeX 定稿），处理的是**作者自己的**稿子。它与 `lusca-pdf-parse`（PDF→Markdown）方向相反，与 `lusca-paper-polish`（改语言）职责互斥——本技能只转格式，英文稿的语言问题交还 polish。

---

## 触发条件

- 明确提及：转 latex、生成 tex、排版成 LaTeX、论文转 LaTeX、中文稿转英文 latex、导出 tex、整理成 LaTeX、出一份 tex、做成能编译的 tex、markdown 转 latex
- 英文：convert to latex, generate tex, markdown to latex, make a tex file, typeset as latex, export as tex, build the latex source
- 斜杠指令：`/lusca-paper-latex`、`/转latex`
- 用户给出了润色稿（MD / txt / `.tex` 草稿 / 粘贴文本），希望得到 LaTeX 源

**不触发**：
- 润色表达 / 改措辞 / 去 AI 腔 / 中转英改写 → `lusca-paper-polish`（本技能不改语言；英文稿的语言问题不在本技能范围内）
- 从零写论文内容 / 帮我想思路 → 本技能需要已有文稿，不写内容
- 只想把 PDF 解析成 Markdown → `lusca-pdf-parse`
- 已有 `.tex`，想做审稿式体检 / 列格式问题清单 → 本技能产出的是"整理好的 .tex"，不是问题清单

---

## 输入

从 `$ARGUMENTS` 与上下文自动解析；输入是"已有文字"，没有文字则无法转（唯一允许的追问）：

- **文件路径**：`./polished.md`、`./draft.tex`、`./intro.txt` —— 用 `Read` 读入；Markdown / LaTeX / 纯文本均可
- **粘贴文本**：用户直接把文稿贴进对话 —— 直接处理
- **范围**：用户指明"只转 abstract / 只转 Method"时聚焦该部分，但仍整体把握结构与交叉引用
- **附带资源**：源稿引用了图片（`figures/*.png`）或已有 `references.bib` 时，一并纳入输出目录（图片路径保留，见 §输出与存放）

**输出语言**（自动判定，不追问）：正文是中文则翻译成英文 LaTeX（默认）；正文是英文则原样排版。**不要**从用户提问所用语言推断——很多人用中文讨论、稿子却是英文。用户明确要中文 LaTeX 时，改用 xelatex + xeCJK 并配中文字体（见 §语言判定）。

---

## 主流程

```
read → detect-lang → protect → (translate) → map-structure → escape → emit → restore → compile → save
```

1. **读懂源稿**：`Read` 源文件，摸清章节层级、图表、公式、引用、代码块，以及正文叙述语言。读不懂的结构（损坏的表格、嵌在图里的公式）如实标记，不猜。
2. **判定语言**：看**正文叙述语言**——中文（含中英混合、以中文叙述为骨架）走翻译支路；英文跳过翻译。判定不看用户提问语言、不看术语 / 公式 / 引用里的英文。
3. **保护敏感片段（关键）**：动笔译或转义之前，先把以下片段抽成占位符（如 `[[M0]]` `[[C0]]`），译文与转义都不碰它们——这是 LaTeX 合法性命门：
   - 数学环境：`$...$`、`\(...\)`、`$$...$$`、`\[...\]`、`equation`/`align`/`gather`/`eqnarray`/`multline` 及带 `\label` 的公式
   - 交叉引用与文献命令：`\cite` `\citep` `\citet` `\ref` `\eqref` `\autoref` `\label` `\url` `\href` `\pageref`
   - 代码与等宽：代码块、`` `inline code` ``
   - 已有 LaTeX 命令与自定义宏：`\newcommand` 定义、`\usepackage{...}`、源稿里已有的 `\textbf{}` 等
4. **翻译（仅中文稿）**：对占位之外的中文叙述做学术翻译（原则见 `references/zh-to-en-latex.md`）；顺手把 Unicode 数学符号转成 LaTeX 命令（表见 `references/latex-hygiene.md`）。
5. **结构映射**：把 Markdown 结构映射到 LaTeX 环境（映射表见 `references/markdown-to-latex.md`）：标题 → `\section`/`\subsection`、列表 → `itemize`/`enumerate`、表格 → `tabular` + `booktabs`、图片 → `figure`、代码块 → `lstlisting`/`verbatim`、公式原样。
6. **正文转义**：正文里的 LaTeX 保留字符（`& % $ # _ { } ~ ^ \`）转义；**数学环境内部与命令参数内部不转义**（它们已在第 3 步被保护）。
7. **套模板**：选文档类与宏包（默认 `article`；用户指定会议 / 期刊用对应类，见 `assets/templates/README.md`），把正文塞进 `\begin{document}...\end{document}`；宏包加载顺序见 `references/latex-hygiene.md`（`hyperref` 最后加载）。
8. **还原占位**：把第 3 步的占位符还原成原始 LaTeX 片段，确认无残留。
9. **编译验证（需 LaTeX 环境，必做）**：`which latexmk pdflatex xelatex` 检测——有则实际编译（英文稿 `latexmk -pdf main.tex`、中文稿 `latexmk -xelatex main.tex`），读 `.log` 修可修的；**无 LaTeX 环境时按 `references/setup-latex.md` 给用户对应平台（Windows / Linux / macOS）的安装指引**，并先跑一轮静态检查（`grep` 未转义 `&%/_`、未配对 `\begin/\end`、未定义 `\cite/\ref`、占位符残留），告知"已静态检查，装好 LaTeX 后请本地 `latexmk -pdf` 复验"。详见 §编译验证。
10. **落盘 + 交付**：写到 `./outputs/lusca-paper-latex/{slug}/main.tex`（`references.bib` / `figures/` 按需同目录），给路径 + 要点（源语言、目标语言、模板、编译状态、待补占位符）。

---

## 最高准则：只换容器，不换内容

这条凌驾于一切转换考量。转换是排版与（必要时）翻译，**不是**重写或补全。

- 不增删作者的论断、数据、阈值、实验结果；原文没有的一律不加。
- 翻译不改变含义：与 `lusca-paper-polish` 的中译英同准则——只换语言外壳，不加强 / 削弱结论、不把相关改成因果、不悄悄去掉限定语。
- 源稿里的占位符与待补项（`[仓库地址待补充]`、`[数据集许可待确认]`）如实保留并在交付时列出，不编、不留到 silently。
- 拿不准某处该不该改时，一律保持原样并标注。

判定标准：转换完成后，逐段对照源稿与 `.tex`，问"这段话的科学内容，和作者写下的是同一回事吗？"每一处"不太一样"都必须回退或标注。

## LaTeX 合法性是硬底线

输出必须能编译（或在没有 LaTeX 的环境里通过静态检查）。常见致命错误都在「保护」与「转义」两步：

- **数学环境不被破坏**：`$...$`、`equation`、`align` 等内容原样保留，翻译时不译内部、转义时不转义内部。
- **命令不被破坏**：`\cite{key}`、`\ref{sec:x}`、`\label{...}`、`\url{...}` 整体保留；翻译不能把 `key` 译掉、转义不能把 `\` 变成 `\textbackslash{}`。
- **正文保留字符必转义**：正文里的 `& % $ # _ { } ~ ^ \` 转义（表见 `references/latex-hygiene.md`）；但表格里的 `&`（列分隔）、`\\`（换行）、数学里的 `_` `^` 是语法的一部分，**不转义**。
- **环境配对**：每个 `\begin{x}` 都有 `\end{x}`；`{}`、`$$`、`\[\]` 配对。
- **宏包顺序**：`hyperref` 最后（或接近最后）加载，`xurl` 在 `hyperref` 之后，`natbib`/`biblatex` 在 `hyperref` 之前。
- **引擎匹配内容**：纯英文用 `pdflatex`；含中文或特殊 Unicode 用 `xelatex` + `xeCJK`。

## 保护敏感片段

翻译与转义都会误伤 LaTeX 片段——译者的"翻译冲动"会去译 `\cite` 里的 key，转义程序会把数学里的 `_` 变成 `\_`。防御办法是**先抽占位、最后还原**（主流程第 3、8 步）：

- 用不会出现在正文里的标记做占位符（如 `[[M0]]` 表示第 0 段数学、`[[C0]]` 表示第 0 个命令）。
- 翻译、Unicode 符号替换、正文转义都只在非占位文本上进行。
- 还原后 `grep` 一遍占位符标记，确认无残留——残留的 `[[M0]]` 会直接编译报错。

这一步是把"翻译 / 转格式"与"LaTeX 合法性"解耦的关键，不可省。

## 语言判定与中译英

**判定**：看正文叙述语言。常见情形：

- 全中文 → 翻译成英文 LaTeX（默认动作）
- 全英文 → 直接排版，不译、不润色
- 中英混合（中文叙述夹英文术语 / 公式 / 引用）→ 按中文处理，译中文叙述、保留英文术语与所有 LaTeX 片段
- 用户明确要中文 LaTeX → 不译，改用 `xelatex` + `\usepackage{xeCJK}\setCJKmainfont{...}`，并告知用户需本地有对应中文字体

**翻译原则**（详见 `references/zh-to-en-latex.md`）：先取义再造句、补回被中文语序藏起来的逻辑转折、术语全文稳定一个译法、修常见中式英语（冠词 / 复数 / 时态 / 冗余范畴词）、不注水（谨慎的中文不等于可以改成更强的英文）。翻译是"学术翻译"，不是逐句直译，也不是再次润色。

## Markdown → LaTeX 结构映射

常见映射（完整表与边界情形见 `references/markdown-to-latex.md`）：

| Markdown | LaTeX |
|----------|-------|
| `#` H1 | `\title{}`（正文顶层标题用 `\section`） |
| `##` `###` | `\section{}` `\subsection{}` |
| `**粗**` `*斜*` | `\textbf{}` `\textit{}` |
| `` `code` `` | `\texttt{}` 或 `\verb||` |
| ``` 代码块 ``` | `lstlisting` / `verbatim` |
| `- ` / `1.` | `itemize` / `enumerate` |
| `![alt](path)` | `\begin{figure}...\end{figure}` |
| `\|表\|格\|` | `tabular` + `booktabs` 三线表 |
| `[text](url)` | `\href{url}{text}` |
| `> 引用` | `\begin{quote}` |
| `$...$` `$$...$$` | 原样保留 |

## 模板与文档类

默认 `article`（通用预印本 / 未知期刊 / arXiv），骨架见 `assets/templates/article.tex`。用户指定会议 / 期刊时换对应文档类（IEEEtran / acmart / NeurIPS / ICML / llncs / apa7 等），切换要点与陷阱见 `assets/templates/README.md`。**没有官方 `.cls`/`.sty` 时不要强行用 IEEE/ACM/NeurIPS 类**（编译会失败），退回 `article` 并在交付时告知用户需自行替换文档类。

## 参考文献处理

- 源稿带 `references.bib` → 用 `\cite` + `\bibliography{references}`，编译走 `bibtex` 序列（见 `references/latex-hygiene.md`）。
- 源稿只有 `[1]` / `(Smith, 2024)` / 脚注式引用、无 `.bib` → 转 `\cite{key}`，按源稿信息生成**占位 `.bib` 条目**并标注"待补全"（作者 / 题名 / 出版年缺哪项标哪项），**绝不臆造**完整著录信息。
- 源稿是 Markdown 链接 `[text](url)` → 转 `\href{url}{text}`；裸 URL → `\url{...}`。

## 编译验证（需 LaTeX 环境）

本 skill 产出的是要能编译的 `.tex`，编译验证是**必做环节**，不是可选项。先检测、按结果分支：

1. **检测**：`which latexmk pdflatex xelatex`——三平台均用此命令。
2. **有 LaTeX**：实际编译（英文稿 `latexmk -pdf main.tex`、中文稿 `latexmk -xelatex main.tex`），读 `.log` 捕获 warning / error，修可修的（未配对环境、未转义字符、缺宏包——缺包用 `tlmgr` / MiKTeX on-the-fly 补，见 `references/setup-latex.md`）；把无法自动判定的（缺 `.bib` 条目、缺图片、缺中文字体）列给用户。生成 `main.pdf` 即通过。
3. **无 LaTeX**：按 `references/setup-latex.md` 给用户**对应平台**（Windows / Linux / macOS）的安装指引，并先跑一轮静态检查作为兜底——`grep` 未转义的 `& % _`、未配对的 `\begin/\end`、`??` 式未定义引用、占位符残留、`hyperref` 是否最后加载。明确告知"已静态检查、装好 LaTeX 后请本地 `latexmk -pdf main.tex` 复验"。
4. **不谎称已编译**：没跑过 `latexmk` 就不要说"编译通过"；只能说"静态检查通过、待本地复验"。

> 当前会话环境若无 LaTeX，编译维度无法在本会话完成——这是现实限制。把 `.tex` 交付给用户、给好安装指引，让用户本地复验，是可接受的交付；但**不要**把"静态检查"说成"已编译"。

## 长文档

长稿和短稿同样认真，不前精后粗。必须分块时给每块标号（"第 i / N 部分"），每块都是完整可编译或可拼接的产物。整篇拼好后做一次完整的结构与转义自检，不谎称已完成。

## 读不了的内容

源稿里有读不了的部分（Word 导出里以图片嵌的公式、损坏的表格、看不清的图）：**不要猜内容再写一段 plausible 的 LaTeX 塞进去**。明确告诉作者这个元素在哪、需要人工核查，对应位置留 `% TODO: 原文 <元素> 无法解析，待人工核查` 注释。

---

## 交付

- 先给落盘路径（`main.tex` + 同目录 `references.bib` / `figures/`），再给三五条要点：源语言 → 目标语言、文档类、**编译状态（已编译通过 / 仅静态检查 + 已给安装指引）**、待补占位符清单。
- **不内联重复完整 `.tex`**——`.tex` 动辄数百行，落盘后再贴一遍是冗余噪声；用户要看直接给路径。
- 含义风险改动（翻译时拿不准是否改变原意的句子）、待补占位符、读不了的内容，**逐项列出**让作者拍板，不要默默处理。

## 输出与存放

- **一篇论文一个目录**：`./outputs/lusca-paper-latex/{slug}/`，`slug` 取自论文标题 / 主题（kebab-case，**不带时间戳**）；同篇多次转换累积到同一目录，已存在则更新 `main.tex` 与 `references.bib`，**不就地改作者润色稿**（润色稿是 polish 的产出，本技能另存）。
- **目录结构**：
  ```
  outputs/lusca-paper-latex/{slug}/
    ├── main.tex            # LaTeX 源（最终产物）
    ├── references.bib      # 源稿有引用时生成（占位条目标注待补）
    ├── figures/            # 复用源稿引用的图片（保留原文件名）
    └── main.pdf            # 编译产物（环境有 LaTeX 时生成）
  ```
- **图片路径保留**：源稿引用的 `figures/*.png` 等随文交付，其相对路径在 `.tex` 里保留（`figures/arch.pdf`），便于本地直接编译；这是与「自解耦」规范的约定例外——图表路径是编译所需，不是开发痕迹。
- **frontmatter**：`.tex` 不加 YAML frontmatter（LaTeX 无此惯例）；源稿若有 frontmatter（如 polish 产出），将其中的标题 / 作者 / 日期 / 摘要映射到 `\title` `\author` `\date` `\begin{abstract}`，不剥离、不重写已有信息。
- **出处块（LaTeX 注释）**：`.tex` 末尾以 LaTeX 注释加出处三要素（注释不影响编译、不污染正文，投稿前可整段删除）。`.tex` 是 LaTeX 源、英文是其生态通用语，且英文注释在 pdflatex / xelatex 下都零风险——因此本 skill 的出处块默认用**英文注释**（中文 pdflatex 稿若塞中文注释可能触发 `Unicode character` 报错；仅当用户明确要中文出处、且用 xelatex + xeCJK 时才换中文）：
  ```
  % Typeset with lusca-paper-latex (comments; safe to delete before submission).
  % Author: lusca
  % Version: lusca-paper-latex v1.1.0
  % Source: https://github.com/yjmm10/lusca-skill/tree/main/skills/lusca-paper-latex
  ```
- **段落不硬换行**：遵 CLAUDE.md——`.tex` 正文段落写在一行（LaTeX 本就以空行分段、忽略单换行），不在句中按列宽折行；列表项每个 `\item` 一行。
- **交付精简**：落盘后只给路径 + 要点 + 待补项，**不内联重复完整 `.tex`**。

---

## 后续衔接

LaTeX 落盘后，按常用度排序：

- **`/lusca-paper-polish`**：中译英后的英文稿若想再过一遍润色（措辞校准、去 AI 腔、句法打磨），把 `main.tex` 的英文正文交给 polish——本技能只负责"译到位 + 排合法"，不抢 polish 的活。
- **`/lusca`**：复盘本次转换中 skill 暴露的问题（翻译是否逐句直译了、数学 / 命令保护是否漏了、转义是否误伤、模板选择是否合理、编译报错是否处理到位）。

> 话术示例：「`main.tex` 已落盘 `outputs/lusca-paper-latex/{slug}/main.tex`（`main.pdf` 一并生成），中文已译成英文、用 article 类、`latexmk -pdf` 编译通过，2 处 `\cite` 的 bib 条目待你补全（见 `references.bib` 标注）。本会话无 LaTeX 时改为"静态检查通过、装好环境后请 `latexmk -pdf` 复验"，安装见 `references/setup-latex.md`。想让英文再地道一点，可接着用 `/lusca-paper-polish` 过一遍。」

---

## 重要约定

- **只换容器不换内容**：转换是排版 + 必要时翻译，不重写、不补全、不改论断。
- **先保护再译/转义**：数学环境与命令先占位，最后还原；`grep` 确认无占位残留。
- **正文转义、数学内部不转义**：LaTeX 保留字符只在正文转义；表格 `&`/`\\`、数学 `_`/`^` 是语法，不动。
- **英文稿不润色**：英文输入只转格式，语言问题交还 polish；本技能不越界改表达。
- **编译是必做环节**：产出必须实际编译验证（`latexmk`）；环境无 LaTeX 时按 `references/setup-latex.md`（三平台安装）引导用户，并先静态检查、如实标注"未编译、待复验"——绝不把静态检查说成已编译。
- **绝不臆造引用**：无 `.bib` 时生成占位条目并标注待补，不编著录信息。
- **一处目录、不就地改润色稿**：产出落在 `outputs/lusca-paper-latex/{slug}/`，作者润色稿保持不动。
- **出处以注释形式加在 `.tex` 末尾**：不影响编译、投稿前可删。

## 质量底线

- **逐段对照源稿自检内容**：每段问"科学内容和作者写下的是同一回事吗"，每一处"不太一样"都回退或标注。
- **数学 / 命令 / 宏零误伤**：编译或静态检查无"数学环境被译 / 被转义""`\cite` 的 key 被改"类错误。
- **占位符零残留**：还原后 `grep` 占位标记，必须清零。
- **转义零误伤**：正文保留字符全转义，数学 / 命令内部零误转义。
- **编译验证（尽力实际编译）**：有 LaTeX 则编译通过、生成 `main.pdf`；无 LaTeX 则静态检查清零 + 给安装指引，如实标注未编译。
- **长稿不划水**：全文同等认真，分块时每块完整，不谎称已完成。

---

## Reference 文件索引

| 文件 | 何时 Read |
|------|-----------|
| `references/setup-latex.md` | 编译验证前：检测 / 安装 LaTeX 工具链（Windows / Linux / macOS 三平台）、缺宏包处理、验证编译 |
| `references/markdown-to-latex.md` | 做结构映射时（标题/列表/表格/图片/代码/公式/引用的完整映射表与边界情形） |
| `references/latex-hygiene.md` | 转义、保护、Unicode 符号替换、宏包顺序、文档类、编译与常见错误时（保留字符转义表、Unicode→LaTeX 符号表、编译序列、错误修复） |
| `references/zh-to-en-latex.md` | 中文稿翻译时（学术翻译原则、保护片段流程、术语稳定、中式英语修正、标点与数字处理） |
| `assets/templates/README.md` | 选文档类 / 切换模板时（article/IEEE/ACM/NeurIPS/ICML/LNCS/apa7 的切换要点与陷阱、引擎选择） |
| `assets/templates/article.tex` | 用默认 article 骨架时（通用英文 article 起点，pdflatex 可编译） |

---

## 版本管理

**当前版本**：见 frontmatter `version` 与 `CHANGELOG.md` 最新条目。

每次修改本技能**必须**：
1. 递增 `SKILL.md` frontmatter `version`
2. 写入 `CHANGELOG.md`（Added / Changed / Fixed / Removed）
3. 向用户说明版本号与变更要点
4. 本 skill 源目录或 frontmatter 有增删 / 重命名时，按工作区规范跑 `./scripts/link-project.sh` 同步发现层

版本号规则：MAJOR（流程 / 输出规范 breaking）/ MINOR（新 reference、新指导、新模板）/ PATCH（措辞、typo）。
