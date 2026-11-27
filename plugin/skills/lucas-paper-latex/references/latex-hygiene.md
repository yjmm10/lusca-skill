# LaTeX 卫生：转义、保护、符号、宏包、编译

做转义、Unicode 符号替换、选宏包、编译排错时查本文件。核心纪律：**正文保留字符必转义，数学 / 命令内部零误伤**。

## 1. 保护先行（翻译 / 转义前的必做步骤）

翻译与正文转义都会误伤 LaTeX 片段。动笔前先把下列片段抽成占位符（如 `[[M0]]` `[[C0]]` `[[V0]]`），处理完正文再还原：

| 类别 | 内容 |
|------|------|
| 数学（`[[M]]`） | `$...$`、`\(...\)`、`$$...$$`、`\[...\]`、`equation`、`align`、`gather`、`multline`、`eqnarray` 及任何带 `$` 定界的片段 |
| 命令（`[[C]]`） | `\cite` `\citep` `\citet` `\ref` `\eqref` `\autoref` `\pageref` `\label` `\url` `\href` `\usepackage` `\newcommand` `\renewcommand` 及源稿里已有的任意 `\xxx{...}` |
| 代码（`[[V]]`） | 代码块、`` `inline code` `` |

还原后必须 `grep` 占位标记（如 `grep -n '\[\[' main.tex`）确认零残留——残留的 `[[M0]]` 会编译报错。

## 2. 正文保留字符转义

只在**正文**里转义；数学环境、命令参数、代码块内部**不转义**（它们已被保护）。

| 字符 | 转义 | 说明 |
|------|------|------|
| `&` | `\&` | 表格里是列分隔符，不转义；正文 ampersand 转义 |
| `%` | `\%` | 注释符；正文百分号必转义（"准确率 90\%"） |
| `$` | `\$` | 数学定界；正文美元必转义 |
| `#` | `\#` | 宏参数符；正文井号转义 |
| `_` | `\_` | 下标符；正文下划线转义（文件名 `file\_v2`） |
| `{` | `\{` | 分组 |
| `}` | `\}` | 分组 |
| `~` | `\textasciitilde{}` | 不可断空格；正文波浪号 |
| `^` | `\textasciicircum{}` | 上标符；正文脱字符 |
| `\` | `\textbackslash{}` | 转义符本身 |

易错点：
- 百分号最常漏：`准确率 90%` → `90\%`；数学里 `90\%` 写成 `$90\%$` 也可，但通常正文直接 `90\%`。
- 下划线：文件名、变量名里的 `_` 在正文要转义（`file\_name`），在数学里是下标（`$x_i$`，不转义），在 `\texttt{}` 里用 `\verb` 或 `underscore` 宏包。
- 引号：中文 `""` 与英文直引号 `"` → LaTeX 的 ``` ``...'' ```（左两个反引号、右两个单引号）；单引号 `'...'` → `` `...` ``。

## 3. Unicode 数学符号 → LaTeX 命令

中文稿（尤其从 Word / 网页复制来的）常带 Unicode 数学符号，正文转义时顺手替换。英文稿若也有（粘贴所致）同样处理。替换前确认该符号不在被保护的数学环境里——数学环境里的 Unicode 符号若存在，说明源稿数学本身不规范，需在数学环境内一并替换（数学环境内的替换不属于"转义"，属于"符号规整"，照常做）。

**运算**
| Unicode | LaTeX |
|---------|-------|
| × | `\times` |
| ÷ | `\div` |
| ± | `\pm` |
| ∓ | `\mp` |
| · | `\cdot` |
| ∘ | `\circ` |

**关系**
| Unicode | LaTeX |
|---------|-------|
| ≤ | `\leq` / `\le` |
| ≥ | `\geq` / `\ge` |
| ≠ | `\neq` |
| ≈ | `\approx` |
| ≡ | `\equiv` |
| ∼ / ~ | `\sim`（数学相似；正文波浪另用 `\textasciitilde{}`） |
| ∝ | `\propto` |
| ≪ / ≫ | `\ll` / `\gg` |

**箭头**
| Unicode | LaTeX |
|---------|-------|
| → | `\to` / `\rightarrow` |
| ← | `\leftarrow` / `\gets` |
| ↔ | `\leftrightarrow` |
| ⇒ | `\Rightarrow` / `\implies` |
| ⇐ | `\Leftarrow` |
| ⇔ | `\Leftrightarrow` / `\iff` |
| ↦ | `\mapsto` |

**集合与逻辑**
| Unicode | LaTeX |
|---------|-------|
| ∈ | `\in` / `\in` |
| ∉ | `\notin` |
| ⊂ / ⊆ | `\subset` / `\subseteq` |
| ⊃ / ⊇ | `\supset` / `\supseteq` |
| ∪ / ∩ | `\cup` / `\cap` |
| ∅ | `\emptyset` / `\varnothing` |
| ∀ / ∃ | `\forall` / `\exists` |
| ¬ | `\neg` / `\lnot` |
| ∧ / ∨ | `\wedge` / `\vee` |

**希腊字母**
| Unicode | LaTeX | | Unicode | LaTeX |
|---------|-------|-|---------|-------|
| α | `\alpha` | | Γ | `\Gamma` |
| β | `\beta` | | Δ | `\Delta` |
| γ | `\gamma` | | Θ | `\Theta` |
| δ | `\delta` | | Λ | `\Lambda` |
| ε / ε | `\epsilon` / `\varepsilon` | | Ξ | `\Xi` |
| ζ | `\zeta` | | Π | `\Pi` |
| η | `\eta` | | Σ | `\Sigma` |
| θ / ϑ | `\theta` / `\vartheta` | | Φ | `\Phi` |
| ι | `\iota` | | Ψ | `\Psi` |
| κ | `\kappa` | | Ω | `\Omega` |
| λ | `\lambda` | | | |
| μ | `\mu` | | | |
| ν | `\nu` | | | |
| ξ | `\xi` | | | |
| π / ϖ | `\pi` / `\varpi` | | | |
| ρ / ϱ | `\rho` / `\varrho` | | | |
| σ / ς | `\sigma` / `\varsigma` | | | |
| τ | `\tau` | | | |
| υ | `\upsilon` | | | |
| φ / φ | `\phi` / `\varphi` | | | |
| χ | `\chi` | | | |
| ψ | `\psi` | | | |
| ω | `\omega` | | | |

**大型算子与杂项**
| Unicode | LaTeX |
|---------|-------|
| ∑ | `\sum` |
| ∏ | `\prod` |
| ∫ | `\int` |
| ∮ | `\oint` |
| ∬ | `\iint` |
| ⋃ / ⋂ | `\bigcup` / `\bigcap` |
| ∞ | `\infty` |
| √ | `\sqrt{}`（带参数） |
| ∂ | `\partial` |
| ∇ | `\nabla` |
| ∠ | `\angle` |
| ⊥ | `\perp` |
| ∥ | `\parallel` |
| ° | `^{\circ}`（如 `$20^{\circ}$`） |
| ′ / ″ | `'` / `''`（或 `\prime`） |
| ℏ | `\hbar` |
| ℓ | `\ell` |
| ℕ ℤ ℚ ℝ ℂ | `\mathbb{N}` `\mathbb{Z}` `\mathbb{Q}` `\mathbb{R}` `\mathbb{C}`（需 `amssymb`） |

不在表里的少见符号：查 [Detexify](https://detexify.kirelabs.org/) 或 `comprehensive` 符号表（`texdoc comprehensive`）。拿不准时不要臆造命令，保留原 Unicode 并加 `% TODO: 符号 <U+xxxx> 待确认 LaTeX 命令` 注释。

## 4. 宏包加载顺序

错误顺序会引发诡异报错。推荐顺序（从上到下）：

1. `inputenc` / `fontenc` / `lmodern`（或 `fontspec`——xelatex 下）
2. `geometry`（页面）
3. `microtype`（微调）
4. `amsmath` `amssymb` `amsthm` `mathtools`（数学）
5. `graphicx` `booktabs` `caption` `subcaption` `float`（图表）
6. `listings`（代码）
7. `natbib` / `biblatex`（文献）
8. `xurl`（紧跟 hyperref 前/后均可，用于长 URL 断行）
9. **`hyperref` 最后加载**（或接近最后）——它要重定义许多命令，晚加载才正确
10.（可选）`cleveref` —— 在 `hyperref` **之后**

铁律：`hyperref` 必须最后（或几乎最后）。`xurl` 在 `hyperref` 之后才能正确扩展 URL 断行规则。

## 5. 文档类选择

| 场景 | 文档类 | 说明 |
|------|--------|------|
| 通用 / 预印本 / arXiv | `\documentclass[11pt,a4paper]{article}` | 默认，pdflatex 可编译 |
| IEEE 会议 / 期刊 | `\documentclass[conference]{IEEEtran}` | 双栏；需 `IEEEtran.cls` |
| ACM | `\documentclass[acmsmall]{acmart}` | 需 `acmart.cls`；CCS 概念码 |
| NeurIPS | 官方 `neurips_202X.sty` + `article` | 需官方 sty |
| ICML | 官方 `icml_202X.sty` + `article` | 需官方 sty |
| Springer LNCS | `\documentclass{llncs}` | 需 `llncs.cls` |
| APA（社科） | `\documentclass[man,12pt]{apa7}` | `man` 模式默认 raggedright，需 `\justifying` |
| 学位论文 | 校方模板（`uthesis` / `thuthesis` 等） | 按校规 |

切换文档类的固定动作见 `assets/templates/README.md`。**没有官方 `.cls`/`.sty` 时不要强行用 IEEE/ACM/NeurIPS 类**——编译必失败，退回 `article` 并告知用户。

## 6. 引擎选择

| 内容 | 引擎 | 编译命令 |
|------|------|----------|
| 纯英文 / 拉丁字符 | pdflatex | `latexmk -pdf main.tex` |
| 含中文 / CJK / 复杂 Unicode | xelatex | `latexmk -xelatex main.tex` |
| 含大量脚本 / 特殊字体 | lualatex | `latexmk -lualatex main.tex` |

中文 LaTeX 必备：
```latex
\usepackage{xeCJK}
\setCJKmainfont{Noto Serif CJK SC}      % 或系统可用之中文字体
\setCJKsansfont{Noto Sans CJK SC}
\setCJKmonofont{Noto Sans Mono CJK SC}
```
编译用 xelatex。本 skill 默认产物是英文（中文稿会先翻译），所以默认 pdflatex；仅当用户明确要中文 LaTeX 时才 xelatex + xeCJK。

## 7. 编译序列（带参考文献）

BibTeX 工作流要跑四遍：
```bash
pdflatex main.tex      # 1. 生成 .aux
bibtex main            # 2. 处理文献
pdflatex main.tex      # 3. 解析引用
pdflatex main.tex      # 4. 定页码
```
或用 `latexmk` 自动处理（推荐）：
```bash
latexmk -pdf main.tex        # 英文
latexmk -xelatex main.tex    # 中文
latexmk -c main.tex          # 清辅助文件
```

## 8. 常见编译错误与修复

| 错误信息 | 原因 | 修复 |
|----------|------|------|
| `Undefined control sequence` | 命令拼错 / 宏包没加 | 检查命令拼写；确认对应宏包已 `\usepackage` |
| `! Misplaced &` | 正文 `&` 未转义 / 表格 `&` 在数学环境里 | 正文 `\&`；表格 `&` 不转义 |
| `! Missing $ inserted` | 正文用了 `_` `^` 等数学符未进数学环境 | 转义为 `\_` `\textasciicircum{}`，或包进 `$...$` |
| `! Undefined references` / `[?]` | 引用未解析 | 再跑一遍 / 跑 `bibtex`；确认 `.bib` 里有对应 key |
| `! LaTeX Error: File 'xxx.cls' not found` | 缺官方模板文件 | 退回 `article`，告知用户需自取官方 `.cls` |
| 中文显示为方框 / 消失 | 用了 pdflatex 编译中文 | 换 xelatex + xeCJK + 中文字体 |
| `! Too many }'s` | `{}` 不配对 | 逐个核对分组括号 |
| `! Float too large` | 图表超页 | 调 `width` 比例、加 `[htbp]` 或 `\clearpage` |
| hyperref 相关诡异报错 | hyperref 未最后加载 | 把 `hyperref` 移到 `\usepackage` 列表末尾 |
| 表格溢出页边 | `p{0.3\linewidth}` 忽略 `tabcolsep` | 用 `p{(\linewidth - N\tabcolsep)*\real{比例}}` 公式 |

## 9. 编译自检操作

```bash
# 检测本地是否有 LaTeX
which latexmk pdflatex xelatex 2>/dev/null

# 有 latexmk：实际编译
latexmk -pdf main.tex 2>&1 | tee build.log
# 看最后是否生成 main.pdf，以及 .log 里的 Warning / Error

# 无 LaTeX：静态检查
# 正文未转义的 & % _（排除数学/命令行）
grep -nE '(^|[^\\])[&%_]' main.tex
# 未配对的 \begin/\end
grep -nE '\\(begin|end)\{' main.tex
# 占位符残留
grep -nE '\[\[' main.tex
# 未定义引用（编译后的 .log 里更准；静态只能看 \ref/\cite 是否有明显 key）
grep -nE '\\(ref|cite|citep|citet|eqref)\{[^}]*\}' main.tex
```

无论哪种，**如实告知用户编译状态**：已编译通过 / 仅静态检查（建议本地复验）/ 哪些待修。
