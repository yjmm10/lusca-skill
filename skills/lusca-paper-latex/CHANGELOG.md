# Changelog — lusca-paper-latex

本文件记录 lusca-paper-latex 的变更。版本号规则：MAJOR（流程 / 输出规范 breaking）/ MINOR（新 reference、新指导、新模板）/ PATCH（措辞、typo）。

## v1.1.0 — 2026-08-04

### Added
- `references/setup-latex.md`：LaTeX 工具链三平台（Windows / Linux / macOS）安装指引——发行版选择（MiKTeX / TeX Live / MacTeX / BasicTeX）、包管理器命令（apt / dnf / pacman / brew / winget / tlmgr / mpm）、PATH 配置、缺宏包处理、本 skill 常用宏包清单、编译验证。

### Changed
- 编译从"尽力而为"升级为**必做环节**：主流程第 9 步、§编译验证、§重要约定、§质量底线统一为"有 LaTeX 则实际编译生成 `main.pdf`，无 LaTeX 则按平台给安装指引 + 静态检查兜底"。
- description 补"实际编译验证（三平台安装见 setup-latex.md）"。
- Reference 文件索引新增 `setup-latex.md`（编译验证前 Read）。
- 输出目录结构补 `main.pdf`（编译产物）；交付要点与话术示例区分"已编译通过 / 仅静态检查"。

## v1.0.0 — 2026-08-04

### Added
- 初始版本：把润色后的学术文稿（Markdown / 粘贴文本 / 已有 `.tex` 草稿）转为可编译 LaTeX。
- 中文稿自动做学术翻译转成英文，英文稿直接排版不重写；语言判定看正文叙述语言，不看用户提问语言。
- 「先保护、再译/转义、最后还原」的主流程：数学环境、`\cite`/`\ref`/`\label`、代码、自定义宏先占位，避免被翻译或转义误伤。
- LaTeX 保留字符正文转义；数学 / 命令内部不转义；Unicode 数学符号 → LaTeX 命令。
- Markdown → LaTeX 结构映射（标题 / 列表 / 表格 / 图片 / 代码 / 公式 / 引用 / 链接）。
- 默认 `article` 骨架 + IEEE / ACM / NeurIPS / ICML / LNCS / apa7 切换指引；引擎选择（pdflatex / xelatex）。
- 参考文献处理：有 `.bib` 用 `\bibliography`，无 `.bib` 生成占位条目标注待补，绝不臆造著录信息。
- 编译自检：有 `latexmk` 则实际编译，无则静态检查（`grep` 未转义字符 / 未配对环境 / 占位残留），不谎称已编译。
- 文档输出：`.tex` 末尾以注释形式加出处块（不影响编译、投稿前可删）；一篇一目录，不就地改作者润色稿。
- `references/`：`markdown-to-latex.md`、`latex-hygiene.md`、`zh-to-en-latex.md`。
- `assets/templates/`：`article.tex` + `README.md`。
