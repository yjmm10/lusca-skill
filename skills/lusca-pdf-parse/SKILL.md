---
name: lusca-pdf-parse
description: >-
  用 MinerU API 把 PDF / 图片 / DOCX 解析成结构化 Markdown（版面还原：双栏、
  表格、公式、图表、阅读顺序，图片自动抽取到本地）。支持本地文件与 URL
  （含 arXiv PDF），可批量。用户提到解析 PDF、PDF 转 markdown、提取 PDF 内容、
  版面还原、图片抽取、文档数字化、parse pdf、pdf to markdown 时使用本技能。
version: "1.0.1"
author: lusca
user-invocable: true
argument-hint: "[PDF 路径 / 图片 / URL / arXiv PDF 链接，可多个]"
allowed-tools: Read, Write, Bash
---

# lusca-pdf-parse — PDF 版面还原为结构化 Markdown

**核心理念：忠实还原版面，不解读内容。把扫描 / 双栏 / 公式密集的 PDF 变成干净、可编辑、可检索的 Markdown + 图片资源，供下游精读 / 翻译 / 检索 / 入库。**

通过 `${SKILL_DIR}/scripts/parse_pdf.py` 调用 **MinerU 精准解析 API**：本地文件批量上传或
URL 提交 → 轮询 → 下载结果包 → 解压为 **Markdown + 图片 + layout/content JSON**（结果包内含
HTML/DOCX/TeX 时一并保留）。脚本只做**结构化搬运**（版面、表格、公式、图、阅读顺序），不总结、
不评判——那是 `lusca-paper-read` 的事。

## 路径约定

- **`${SKILL_DIR}`**：本技能根目录（含本 `SKILL.md` 的文件夹）。Claude Code 下等价于
  `CLAUDE_SKILL_DIR`；经 symlink 发现层加载时即为 `skills/lusca-pdf-parse/`。
- 为简洁，下文用 `$PARSE` 指代 `${SKILL_DIR}/scripts/parse_pdf.py`。**始终用绝对路径调用**，
  避免 `cd scripts && ...` 在不同 cwd 下失效。
- 解析产出默认落盘到 `./outputs/lusca-pdf-parse/{slug}/`（用户指定路径时从其指定）。

## 与体系内其它 skill 的分工

| 场景 | 使用技能 |
|------|----------|
| 文献检索 / related work / prior art | `lusca-paper-search` |
| **PDF 版面还原为 Markdown（忠实结构化、图片抽取、批量）** | **本技能（lusca-pdf-parse）** |
| 精读一篇论文 / 批判性评估 / 阅读笔记（理解内容） | `lusca-paper-read` |
| 复盘本会话中 skill 暴露的问题 | `lusca` |

**与 `lusca-paper-read` 的边界**：`lusca-paper-read` 也能读 PDF，但产出是**阅读笔记**（理解 + 批判），
且长 PDF 靠 `Read` 分块读、对复杂版面的还原能力有限。本技能产出**忠实 Markdown**（双栏重排、表格
转写、公式保留、图片落盘），**不理解内容**。常见衔接：复杂版面论文 → 先用本技能还原成干净
Markdown + 图 → 再交 `lusca-paper-read` 基于该 Markdown 精读（更准、图不丢）。

---

## 触发条件

- 明确提及：解析 PDF、PDF 转 markdown、把 PDF 转成 md、提取 PDF 内容、版面还原、抽取图片、
  PDF 结构化、文档数字化、扫描件转文字
- 英文：parse pdf, pdf to markdown, extract pdf, layout recovery, digitize pdf
- 斜杠指令：`/lusca-pdf-parse`、`/解析pdf`
- 提供了 PDF / 图片路径或 URL，且要的是**可编辑全文 / 版面还原**而非内容理解

**不触发**：
- 想理解一篇论文并要阅读笔记（→ `lusca-paper-read`；若版面复杂可先本技能还原再精读）
- 只想检索相关论文（→ `lusca-paper-search`）
- 只读一小段 PDF 文字（直接 `Read` 即可，无需 API 解析）

---

## 输入（自动推断——绝不追问确认）

从 `$ARGUMENTS` 解析，首轮即跑：

- **本地文件路径**：`/path/to/x.pdf`、`./scan.png`、`report.docx` —— 可多个，脚本批量上传
- **URL**：`http(s)://...` —— 当作远程文件提交给 MinerU（如 `https://arxiv.org/pdf/2310.12345`）
- **混合**：本地与 URL 可同批给出，脚本分类处理（URL 逐个提交、本地批量上传）
- **model_version**：`vlm`（默认；视觉语言模型，复杂版面 / 公式 / 表格更优）或 `auto`（传统流水线，
  更快）；仅当用户明确要求时改用 `auto`

存在性校验：本地路径不存在时**如实报错**（不静默跳过）。

## Token 配置

脚本从环境变量 **`MINERU_TOKEN`** 读凭证（`scripts/_env.py` 自动加载仓库根 `.env`，shell 已导出
则优先）。未配置时脚本直接退出并提示——**绝不无 token 空跑**。申请方式见
`references/mineru_api.md`。

---

## 如何运行

```bash
python "$PARSE" <input> [<input> ...] [--model-version vlm] [--output-dir ./outputs/lusca-pdf-parse]
```

- `input`：本地路径或 URL，可多个；`http(s)://` 开头按 URL 处理
- `--model-version`：`vlm`（默认）/ `auto`
- `--output-dir`：默认 `./outputs/lusca-pdf-parse`
- `--timeout`：单任务轮询超时（秒，默认 600）
- `--poll-interval`：轮询间隔（秒，默认 5）
- `--max-workers`：本地文件上传并发（默认 5）

CLI 输出两段（AI 一次拿全）：

- `===RESULT===`：JSON 数组，每项含 `input` / `slug` / `state` / `output_dir` / `files`
  （`markdown` / `images_dir` / `layout_json` / `content_json` / `html` …）
- `===SUMMARY===`：`成功 X / 失败 Y`

某任务失败：脚本把错误写进对应结果的 `error` 字段并打到 stderr——**原样上报，绝不隐瞒**。

---

## 输出 schema（脚本 `===RESULT===` 单项）

```
{
  "input": str,            # 原输入（路径或 URL）
  "slug": str,             # kebab-case，用作子目录名
  "task_id": str,
  "state": "done" | "failed",
  "output_dir": str,       # .../{slug}/parsed，MinerU 结果解压目录（仅 done）
  "zip": str,              # .../{slug}/{slug}.zip，原始结果包（保留，便于核对）
  "files": {               # 定位到的关键文件（路径字符串；仅 done）
    "markdown": str,       # 主体 Markdown
    "images_dir": str,     # 抽取的图片目录
    "layout_json": str,    # 版面布局 JSON（若有）
    "content_json": str,   # 内容列表 JSON（若有）
    "html" | "docx" | "tex": str  # 结果包内含则列出
  },
  "error": str             # 仅 state=failed
}
```

---

## 主流程

```
parse-inputs → run-script → locate-markdown → report → save
```

1. **解析输入**：从 `$ARGUMENTS` 拆出本地路径 / URL；本地路径不存在的如实报错
2. **跑脚本**：`python "$PARSE" <inputs> --model-version <v>`（默认 vlm）
3. **定位产出**：读 `===RESULT===`，拿到每篇的 `files.markdown` 与 `images_dir`
4. **（可选）速览质量**：`Read` markdown 头部几屏，确认版面 / 表格 / 公式还原正常；异常在报告里标注
5. **落盘解析报告**：`Read` `assets/parse-report-template.md`，按模板填一份轻量报告
   （frontmatter + 输入 / 模型 / 文件清单 / 一句话内容概述 / 质量备注），写到
   `./outputs/lusca-pdf-parse/{slug}/{YYYYMMDDHHmmss}_{slug}_parse-report.md`
6. **交付**：产出目录 + markdown 路径 + 一两句要点（解析了什么、质量如何）；**不内联重复粘贴
   完整 Markdown**——结果已落盘，再贴一遍是冗余噪声；附一句后续衔接建议（见 §后续衔接）

---

## 输出与存放

- **目录结构**（每个输入一个 slug 目录，图片在 `parsed/images/` 下保证 Markdown 可直接显示）：
  ```
  outputs/lusca-pdf-parse/{slug}/
    ├── parsed/                          # MinerU 结果包解压
    │   ├── *.md                         # 主体 Markdown（版面还原）
    │   ├── images/                      # 抽取的图片（Figure / Table）
    │   ├── layout_drawing.json          # 版面布局（若有）
    │   ├── content_list.json            # 内容列表（若有）
    │   └── *.html / *.docx / *.tex      # 结果包内含则保留
    ├── {slug}.zip                       # 原始结果包（保留，便于重解压 / 核对）
    └── {YYYYMMDDHHmmss}_{slug}_parse-report.md   # 解析报告（AI 生成）
  ```
  - slug 取自文件名 / URL 末段（kebab-case）；用户指定路径时从其指定
- **图片引用保持原样**：MinerU 产出的 Markdown 已用相对路径引用 `images/`，**不重写**；仅在确需
  跨目录引用时按需调整
- **frontmatter 保留**：若输入是带 frontmatter 的 md（少见），处理时保留其 frontmatter
- **交付精简**：落盘后只返回产出目录 + markdown 路径 + 一两句要点，**不内联重复展示完整 Markdown**
- **文末出处块**：解析报告结尾附一行出处（遵 CLAUDE.md「文档输出规范」）：
  `> 作者：lusca ｜ 版本：lusca-pdf-parse v<version> ｜ 出处：https://github.com/yjmm10/lusca-skill/tree/main/skills/lusca-pdf-parse`

---

## 后续衔接

本技能产出**原料**（忠实 Markdown + 图），是「检索→解析→精读」主链的**中间环节**——把"理解"留给下游：

- **`/lusca-paper-read`**（最常见，主链下一步）：基于这份 Markdown 精读 / 批判性评估——比直接读 PDF 更准，复杂版面（双栏 / 表格 / 公式）不乱、图不丢
- **`/lusca`**：复盘本次解析中 skill 暴露的问题（还原质量、参数选择、错误处理）

> 话术示例：产出目录 + 要点后补一句「如需精读批判可接着用 `/lusca-paper-read` 基于这份 Markdown 做（比直接读 PDF 更准、图不丢）」。

---

## 质量底线

- **忠实搬运，不改写**：MinerU 产出的 Markdown 是版面还原结果，**不擅自改写、不总结、不"润色"**；
  发现明显还原错误（表格错位、公式乱码、图缺失）时在报告里标注，**不偷偷改原文**
- **基于产出，不臆造**：报告里的一句话概述与质量备注基于实际解析出的 Markdown；没解析成功的不编内容
- **错误原样上报**：任务失败时把 `error` 字段如实报给用户，不隐瞒、不盲目重试
- **不替代精读**：本技能产出是原料（Markdown + 图）；要理解、批判、做笔记请走 `lusca-paper-read`

---

## Reference 文件索引

| 文件 | 何时 Read |
|------|-----------|
| `references/mineru_api.md` | 需要了解 MinerU API 端点、token 申请、任务状态、限制与失败模式时 |
| `assets/parse-report-template.md` | 落盘解析报告时，复制为本次报告骨架（含 frontmatter） |

---

## 版本管理

**当前版本**：见 frontmatter `version` 与 `CHANGELOG.md` 最新条目。

每次修改本技能**必须**：
1. 递增 `SKILL.md` frontmatter `version`
2. 写入 `CHANGELOG.md`（Added / Changed / Fixed / Removed）
3. 向用户说明版本号与变更要点
4. 本 skill 源目录或 frontmatter 有增删 / 重命名时，按工作区规范跑 `link-project.sh` 同步发现层

版本号规则：MAJOR（流程 / 输出规范 breaking）/ MINOR（新参数、新 reference、脚本能力扩展）/ PATCH（措辞、typo）。
