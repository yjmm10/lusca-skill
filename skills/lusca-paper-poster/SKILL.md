---
name: lusca-paper-poster
description: >-
  基于 lusca-paper-read 阅读笔记生成会议尺寸可编辑海报（60×36in）：提炼文案、只用以有 imgs/、
  生成 QR、固定 HTML 模板、FULL 90% 门控最多 3 轮、导出 poster.pptx。用户提到从阅读笔记做海报、
  论文海报、paper poster、出海报 pptx、/lusca-paper-poster 时使用。不替代 ResearchStudio paper2poster 全链。
version: "0.1.0"
author: lusca
user-invocable: true
argument-hint: "[lusca-paper-read 笔记.md 或 slug 目录]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# lusca-paper-poster — 阅读笔记 → 可编辑会议海报

**定位**：`lusca-paper-read` 落盘之后的旁支交付。上游只吃笔记 + `imgs/`；中间固定 HTML（60×36 in）；
主交付 **可编辑 `poster.pptx`**。保留 QR 与 **FULL 90% 门控（最多 3 轮）**；不做旁白、机构 logo 抓取、多轴样式随机、paper2assets 抽图。

## 与体系内其它 skill 的分工

| 场景 | 技能 |
|------|------|
| 精读 / 阅读笔记 | `lusca-paper-read`（上游） |
| **从笔记出海报 pptx** | **本技能** |
| ResearchStudio 原版全链海报（多轴 + 长 fill） | 第三方 `paper2poster`（不经本技能） |

## 触发 / 不触发

- 触发：从阅读笔记做海报、论文海报、poster pptx、`/lusca-paper-poster`
- 不触发：裸 PDF 要跑完整 ResearchStudio 流水线 → 用 `/paper2poster`；只要精读 → `/lusca-paper-read`

## 主流程

```
resolve note → distill poster_copy.json → validate (≤2)
  → copy_figures → make_qr → fill_html
  → slack gate loop (≤3, FULL 90%) → export_pptx → report
```

1. **Resolve**：`python3 skills/lusca-paper-poster/scripts/resolve_note.py <path> --json`
2. **Read** 笔记 + `Glob` `imgs/*`；按 `references/distill-guide.md` / `figure-pick.md` / `copy-budget.md` **Write**  
   `outputs/lusca-paper-poster/{slug}/poster_copy.json`
3. **Validate**：`validate_copy.py … --note-dir <note_dir>`；失败则改短 JSON，**最多 2 次**
4. **Figures**：`copy_figures.py --copy … --note-dir … --outdir …`
5. **QR**：`make_qr.py --copy … --outdir …`（无 URL 时 exit 1 可继续，扫描区隐藏）
6. **HTML**：`fill_html.py --copy … --outdir …` → `poster.html`
7. **Fill 门控（最多 3 轮）**：见 `references/fill-loop.md`  
   `run_slack_gate.py <outdir>/poster.html`  
   - exit 0 → 进入导出  
   - 非 0 → 按 slack 报告改 `poster.html`，**累计 ≤ 3 次** gate；第 3 次仍失败则带警告继续导出
8. **PPTX**：`export_pptx.py --html <outdir>/poster.html --out <outdir>/poster.pptx`
9. **交付**：pptx（+ html）绝对路径；用图与 QR 说明；文末三行出处；后续衔接一句

### 画幅

- 设计画布 / HTML `@page`：**60×36 in**（与 paper2poster landscape 一致）
- 导出 PPTX 时 OOXML 单边上限 56 in：`html2pptx` 会等比缩到约 **56×33.6 in**（设计视口仍按 60×36 量测）
- v0.1 **不做** portrait A0

### 明确不做（v0.1）

- 旁白 TTS、机构 logo 抓取、style/theme/header 多轴 random
- PDF 抽图 / paper2assets
- 超过 3 轮的 staged-fill；html2pptx 视觉审计环（本技能调用 one-shot `html_to_pptx`）

## 输出布局

```text
outputs/lusca-paper-poster/{slug}/
├── poster_copy.json
├── poster.html
├── poster.pptx
├── imgs/
└── assets/qr/{paper,code}.png
```

## Reference 文件索引

| 文件 | 何时 Read |
|------|-----------|
| `references/distill-guide.md` | 写 `poster_copy.json` 前 |
| `references/copy-budget.md` | 提炼 / validate 失败改短时 |
| `references/figure-pick.md` | 选 `figures.*` 时 |
| `references/fill-loop.md` | `fill_html` 之后跑 slack 门控时 |
| `assets/poster_copy.schema.json` | 对照字段（validate 脚本已强制） |
| `assets/templates/poster_landscape_60x36.html` | 勿手改源模板；由 `fill_html.py` 写出到 outdir |

## 后续衔接

- 主交付即为海报 pptx；旁支可用 `/lusca` 复盘本技能门控/提炼问题

## 文末出处（落盘 md 附录若有；对话交付可省略 md 文件）

```
> 作者：lusca
> 版本：lusca-paper-poster v0.1.0
> 出处：https://github.com/yjmm10/lusca-skill/tree/main/skills/lusca-paper-poster
```
