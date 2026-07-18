---
title: "PDF 解析：<文件名 / slug>"
source_input: "<原始输入：本地路径或 URL>"
model_version: "vlm"
task_id: "<MinerU task_id>"
parse_date: "<YYYY-MM-DD HH:MM:SS>"
page_count: <N 或 n/a>
generator: "lusca-pdf-parse@1.0.0"
---

# PDF 解析报告：<文件名>

> 输入 `<source_input>`，模型 `<model_version>`；产出落盘于 `outputs/lusca-pdf-parse/<slug>/parsed/`。

## 文件清单

| 产物 | 路径 |
|------|------|
| 主体 Markdown | `parsed/<name>.md` |
| 图片目录 | `parsed/images/` |
| 版面布局 JSON | `parsed/layout_drawing.json` |
| 内容列表 JSON | `parsed/content_list.json` |
| 原始结果包 | `<slug>.zip` |

## 内容概述

一两句话说明文档是什么（类型 / 主题 / 篇幅），基于解析出的 Markdown。

## 质量备注

版面 / 表格 / 公式 / 图片还原是否正常；明显问题在此列出（表格错位、公式乱码、缺图等）；无问题写「版面还原良好」。

---

> 作者：lusca ｜ 版本：lusca-pdf-parse v<version> ｜ 出处：https://github.com/yjmm10/lusca-skill/tree/main/skills/lusca-pdf-parse
