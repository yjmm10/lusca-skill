# Markdown → LaTeX 结构映射

做结构映射时查本表。原则：**忠于源稿结构**——源稿几级标题、几个并列项、几张表，LaTeX 就对应几级、几项、几表，不擅自合并 / 拆分 / 升降级。映射只换"语法容器"，不换内容。

## 标题层级

| Markdown | LaTeX | 说明 |
|----------|-------|------|
| `# Title`（文档顶层，全文仅一个） | `\title{...}` + `\maketitle` | H1 是文档标题，进 preamble；不要写成 `\section` |
| `## 一级章节` | `\section{...}\label{sec:...}` | 章节大标题 |
| `### 二级` | `\subsection{...}` | |
| `#### 三级` | `\subsubsection{...}` | |
| `##### 四级` | `\paragraph{...}` | 行内小标题，不带编号 |
| `###### 五级` | `\subparagraph{...}` | 极少用 |

注意：
- `article` 类默认给 `\section` 编号；会议模板（IEEE/ACM/NeurIPS）的编号规则各异，按模板默认走，不要手动加 `1.` `2.`。
- 每个 `\section` 配一个 `\label{sec:short-name}`，方便正文 `\ref{sec:short-name}` 交叉引用；label 用稳定的短名，不用数字。
- 源稿标题里的 Markdown 强调（`**`）→ LaTeX 里 `\section{\textbf{...}}` 通常不必要，标题自身已加粗，去掉强调标记即可。

## 段落与强调

| Markdown | LaTeX |
|----------|-------|
| 空行分段 | 空行分段（LaTeX 忽略单换行，与 Markdown 一致） |
| `**粗体**` `__粗体__` | `\textbf{...}` |
| `*斜体*` `_斜体_` | `\textit{...}`（强调语气用 `\emph{...}`） |
| `***粗斜***` | `\textbf{\textit{...}}` |
| `` `行内代码` `` | `\texttt{...}`；含特殊字符（`#` `_` `%` 等）用 `\verb|...|` |
| `~~删除线~~` | `\sout{...}`（需 `\usepackage[normalem]{ulem}`） |
| 行尾两个空格 = 强制换行 | `\\` 或 `\newline`（少用，学术正文一般靠分段） |

## 列表

| Markdown | LaTeX |
|----------|-------|
| `- ` / `* ` 无序列表 | `\begin{itemize}\item ...\end{itemize}` |
| `1.` 有序列表 | `\begin{enumerate}\item ...\end{enumerate}` |
| 嵌套列表 | 嵌套 `itemize`/`enumerate`，缩进即可 |
| 任务列表 `- [ ]` | `\usepackage{hyperref}` 后用 `\item[\textcolor{...}{$\square$}]`，或 `easylist` 宏包 |

注意：
- 每个 `\item` 写一行（遵"段落不硬换行"）。
- 列表前后要有正常段落或标题承接，不要孤立。
- 列表项之间不要空行（除非要分段）；`itemize` 项间间距用 `\itemsep` 调，学术稿一般保持默认。

## 表格

Markdown 表格 → `tabular` + `booktabs` 三线表（`\toprule` `\midrule` `\bottomrule`），不用 `\hline`（`booktabs` 更专业、线条粗细合规）。

```markdown
| Method | Acc | F1 |
|--------|-----|----|
| Base   | 0.72 | 0.70 |
| Ours   | **0.89** | **0.87** |
```
→
```latex
\begin{table}[H]
  \centering
  \caption{Results on the benchmark.}
  \label{tab:results}
  \begin{tabular}{lcc}
    \toprule
    Method & Acc & F1 \\
    \midrule
    Base & 0.72 & 0.70 \\
    Ours & \textbf{0.89} & \textbf{0.87} \\
    \bottomrule
  \end{tabular}
\end{table}
```

要点：
- 对齐符号 `l`/`c`/`r` 按列内容选；长文本列用 `p{宽度}` 或 `>{\raggedright\arraybackslash}p{宽度}`。
- `\caption` 在 `\tabular` **之上**（`table` 浮动体的惯例：表标题在表上方、图标题在图下方）。
- `\label` 紧跟 `\caption`，引用用 `Table~\ref{tab:results}`（`~` 防断行）。
- 跨页长表用 `\usepackage{longtable}`。
- 表格单元里的 `%` `_` `&` 要转义（` \% ` `\_ ` `\&`）；表格分隔符 `&` 与换行 `\\` 是语法，不转义。

## 图片

| Markdown | LaTeX |
|----------|-------|
| `![架构图](figures/arch.png)` | `\begin{figure}...\includegraphics...\caption...\label...\end{figure}` |

```latex
\begin{figure}[htbp]
  \centering
  \includegraphics[width=0.8\linewidth]{figures/arch}
  \caption{Overview of the architecture. The encoder maps raw input to a latent representation before the decoder reconstructs it.}
  \label{fig:arch}
\end{figure}
```

要点：
- `\includegraphics` 的文件名**不写扩展名**（写 `figures/arch` 而非 `figures/arch.png`）——LaTeX 会自动选 `.pdf`/`.png`/`.jpg`；这样矢量 `.pdf` 与位图能互换。
- `width=0.8\linewidth` 用相对宽度，不要写绝对尺寸。
- `\caption` 在 `\includegraphics` **之下**（图标题在图下方）。
- `\label` 紧跟 `\caption`，引用用 `Figure~\ref{fig:arch}`。
- alt 文本（`![alt](...)`）→ caption 的基础，但要扩成完整陈述句（首字母大写、句末句号），不要照搬简短 alt。
- 子图用 `\usepackage{subcaption}` 的 `\subfigure` 或 `\begin{subfigure}`。
- 图片浮动位置 `[htbp]`（here/top/bottom/page）足够；`[H]`（强制）需 `\usepackage{float}`，只在绝对必要时用。

## 代码块

| Markdown | LaTeX |
|----------|-------|
| ` ```python ... ``` ` | `\begin{lstlisting}[language=Python]...\end{lstlisting}` |
| ` ``` ... ``` `（无语言） | `\begin{verbatim}...\end{verbatim}` |

`lstlisting`（`listings` 宏包）支持语法高亮与行号，推荐：

```latex
\usepackage{listings}
\lstset{basicstyle=\ttfamily\small, breaklines=true, frame=single, language=Python}
\begin{lstlisting}[language=Python, caption={Training loop.}, label={lst:train}]
for epoch in range(E):
    for batch in loader:
        loss = model(batch)
        loss.backward()
\end{lstlisting}
```

要点：
- 代码块**整体保护**（在主流程"保护敏感片段"步抽占位），正文转义不碰代码内部——代码里的 `_` `#` `$` 是代码字符，不是 LaTeX 语法。
- 显示数学公式（`$$...$$`）里的代码另当别论；普通代码块用 `lstlisting`/`verbatim` 原样保留。
- 长代码考虑附录而非正文。

## 引用块与脚注

| Markdown | LaTeX |
|----------|-------|
| `> 引用文字` | `\begin{quote}...\end{quote}`（短）或 `quotation`（多段） |
| `[^1]` 脚注 | `\footnote{...}` |

学术正文少用引用块（那是别人的话）；确需引用他人原话用 `quote` 并配 `\cite`。

## 链接

| Markdown | LaTeX |
|----------|-------|
| `[text](url)` | `\href{url}{text}`（需 `hyperref`） |
| 裸 URL `https://...` | `\url{https://...}`（需 `url` 或 `hyperref`） |

要点：
- `\href` 的 URL 不转义（`hyperref` 处理）；长 URL 加 `\usepackage{xurl}` 自动断行。
- 邮箱 `\href{mailto:a@b.com}{a@b.com}`。

## 公式

| Markdown | LaTeX |
|--------|-------|
| `$inline$` | `$inline$`（原样保留，不转义） |
| `$$display$$` | `\begin{equation}...\end{equation}`（带编号）或 `\[...\]`（无编号） |
| 多行对齐 | `\begin{align}...\end{align}` |

**公式整体保护**，主流程第 3 步抽占位、第 8 步还原。公式内部的 `_` `^` `\frac` `\sum` 等是数学语法，不转义、不翻译。

引用公式用 `Equation~\eqref{eq:loss}`（`\eqref` 自动加括号）。每个独占公式配 `\label{eq:short-name}`。

## 分隔线与特殊

| Markdown | LaTeX |
|----------|-------|
| `---` 分隔线 | 学术正文一般不用；确需分段用 `\hrulefill` 或 `\par\noindent\rule{\linewidth}{0.4pt}` |
| `#` 重复的"装饰性"标题 | 去掉装饰，用正常 `\section` |

## 源稿本身已是 LaTeX 时

源稿是 `.tex` 草稿时，结构映射基本是"原样保留 + 卫生修复"：
- 保留所有 `\section`/`\begin{...}`/`\cite`/`\ref`/数学环境原样。
- 补齐缺失的 preamble（文档类、宏包、`\title`/`\author`/`\begin{document}`）。
- 修明显的卫生问题（正文未转义的 `&%_`、`hyperref` 未最后加载、缺 `\bibliographystyle`）。
- **不重写已正确的 LaTeX**——草稿里的 `\textbf`、自定义宏、特定宏包用法照搬。
