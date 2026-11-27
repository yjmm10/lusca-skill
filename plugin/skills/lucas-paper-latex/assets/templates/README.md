# 模板索引 —— 何时用哪个

`article.tex` 是默认骨架（通用英文 article，pdflatex 即可编译）。用户**明确指定**会议 / 期刊时，改用对应文档类与必要宏包；本目录的 `article.tex` 是排版起点，**不是**官方模板的替代——官方 `.cls` / `.sty` 仍需从会议官网获取并放进编译目录。

## 文档类速查

| 场景 | 文档类 | 要点与陷阱 |
|------|--------|-----------|
| 通用预印本 / 未知期刊 / arXiv | `\documentclass[11pt,a4paper]{article}` | 默认；pdflatex 可编译；用 `article.tex` |
| IEEE 会议 / 期刊 | `\documentclass[conference]{IEEEtran}` | 双栏；作者用 `\IEEEauthorblockN` / `\IEEEauthorblockA`；`\bibliographystyle{IEEEtran}`；关键词 `\begin{IEEEkeywords}` |
| ACM | `\documentclass[acmsmall]{acmart}` | 需 `acmart.cls`；`\bibliographystyle{ACM-Reference-Format}`；CCS 概念码 `\ccsdesc`；版权语句 `\setcopyright{...}` |
| NeurIPS | 官方 `neurips_202X.sty` + `article` 类 | 需官方 sty；宽高固定；匿名投稿期去掉 `\neuripsfinal` |
| ICML | 官方 `icml_202X.sty` + `article` 类 | 需官方 sty；`\icmlauthor` 填作者 |
| Springer LNCS | `\documentclass{llncs}` | 需 `llncs.cls`；`\bibliographystyle{splink}`；无 `\section` 编号上限较严 |
| APA（社科） | `\documentclass[man,12pt,natbib]{apa7}` | 需 `apa7.cls`；`man` 模式**默认 raggedright**，需 `\usepackage{ragged2e}` + `\justifying` 恢复两端对齐；`\shorttitle` 设页眉 |
| 学位论文 | 校方模板（`uthesis` / `thuthesis` / `sjtuthesis` 等） | 按校规；中文论文用 xelatex |

## 切换文档类的固定动作

1. 文档类行换成对应 `\documentclass{...}`（参数按会议要求：`[conference]` / `[acmsmall]` / `[man,12pt]`）。
2. 作者 / 标题块换成该类要求的命令：
   - IEEE：`\IEEEauthorblockN{Name}` + `\IEEEauthorblockA{Affiliation\\Email}`
   - ACM：`\author{...}` + `\affiliation{...}` + `\email{...}` + CCS 概念码
   - apa7：`\shorttitle{...}` + `\author{...}` + `\affiliation{...}` + `\authornote{...}`
   - NeurIPS / ICML：官方 sty 的 `\author{...}` 或 `\icmlauthor{...}`
3. `\bibliographystyle{...}` 换成该会议要求的样式（IEEEtran / ACM-Reference-Format / splink / plainnat / unsrtnat）。
4. 关键词环境换：IEEE 用 `IEEEkeywords`，ACM / article 用 `\noindent\textbf{Keywords:}` 或 `keywords` 环境。
5. **不要**在没有官方 `.cls` / `.sty` 时强行用 IEEE / ACM / NeurIPS / LNCS 类——编译会因缺类文件失败；此时退回 `article`，在交付时明确告知"需从官网取官方模板后替换文档类"，并在 `.tex` 顶部加注释标明目标模板。
6. 中文 / 含中文片段时，引擎从 pdflatex 换 xelatex，启用 `\usepackage{xeCJK}` + `\setCJKmainfont{...}`（见 `article.tex` 注释块）。

## 引擎选择

| 内容 | 引擎 | 命令 |
|------|------|------|
| 纯英文 / 拉丁字符 | pdflatex | `latexmk -pdf main.tex` |
| 含中文 / CJK / 复杂 Unicode | xelatex | `latexmk -xelatex main.tex` |
| 含大量脚本 / 特殊字体 | lualatex | `latexmk -lualatex main.tex` |

本 skill 默认产物是英文（中文稿会先翻译），因此默认 pdflatex + `article`；仅当用户明确要中文 LaTeX 时才 xelatex + xeCJK。

## 宏包加载顺序铁律

不论用哪个文档类，宏包顺序都要守（详见 `references/latex-hygiene.md`）：

1. 编码 / 字体（inputenc / fontenc / lmodern，或 xelatex 下的 fontspec + xeCJK）
2. 页面（geometry）
3. 数学（amsmath / amssymb / mathtools）
4. 图表（graphicx / booktabs / caption / float）
5. 代码（listings）
6. 文献（natbib / biblatex）
7. **`hyperref` 最后加载**（`xurl` 在其后）

顺序错了（尤其 hyperref 不在最后）会出各种诡异报错。

## 选择流程

```
用户指定会议/期刊？
├─ 是 → 对应文档类（需官方 cls/sty）
│       ├─ 本地有官方类文件 → 用之，按上述"固定动作"调整
│       └─ 本地无 → 退回 article，告知用户需自取官方模板
└─ 否 → article.tex（默认），pdflatex 编译
```

无论选哪个，源稿内容（章节、公式、图表、引用）原样搬入，只换文档类与 preamble。
