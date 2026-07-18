# MinerU 精准解析 API 参考

本 skill 通过 `scripts/parse_pdf.py` 调用 MinerU（https://mineru.net）的精准解析 API v4，把 PDF / 图片 / DOCX 还原为结构化 Markdown。

## Token

- 环境变量 **`MINERU_TOKEN`**；由 `scripts/_env.py` 从仓库根 `.env` 自动加载（shell 已导出则优先）
- 申请：登录 https://mineru.net → 用户中心 / API Token
- 请求头：`Authorization: Bearer <token>`，`Content-Type: application/json`

## 端点

| 用途 | 方法 + 路径 |
|------|------------|
| 申请批量上传链接（本地文件） | `POST /api/v4/file-urls/batch` |
| 查批量任务详情（取 task_id） | `GET /api/v4/extract/batch/{batch_id}` |
| 提交 URL 解析任务 | `POST /api/v4/extract/task` |
| 查单任务状态 | `GET /api/v4/extract/task/{task_id}` |
| 结果包下载 | 任务 `data.full_zip_url`（GET，流式） |

## 两种入口

- **本地文件**：`POST /file-urls/batch`（`{files:[{name,data_id}], model_version}`）拿签名 URL → `PUT` 上传（不带 Content-Type）→ 系统自动提交解析 → `GET /extract/batch/{batch_id}` 取各 task_id → 逐个轮询 `wait_task`
- **URL**：`POST /extract/task`（`{url, model_version}`）→ 取 task_id → 轮询 `wait_task`

## model_version

- `vlm`：视觉语言模型（默认）。复杂版面、公式、表格、扫描件更优；较慢、消耗额度较多
- `auto`：传统流水线。更快；规整电子 PDF 表现良好

## 任务状态

轮询 `GET /extract/task/{task_id}` → `data.state`：

- `pending` / `running`：进行中（`extract_progress` 给 `extracted_pages` / `total_pages`）
- `done`：完成，取 `full_zip_url` 下载结果 zip
- `failed`：失败，看 `err_msg`

## 结果包结构

zip 解压后典型含：

- `*.md` — 主体 Markdown（版面还原，相对路径引用 `images/`）
- `images/` — 抽取的图片（Figure / Table 等）
- `layout_drawing.json` — 版面布局坐标
- `content_list.json` — 内容块顺序列表
- 可选 `*.html` / `*.docx` / `*.tex`

`parse_pdf.py` 的 `_find_files` 自动定位这些产物写入 `===RESULT===`。

## 限制与失败模式

- 单批本地文件 ≤ 50（`MAX_BATCH`）
- 单任务默认轮询超时 600s（`--timeout` 可调）；大 PDF / 扫描件可能更久，按需调大
- `get_batch_task_ids` 对字段路径做了容错（`task_ids` / `task_id_list` / `task_list[].task_id`）；若 MinerU 改了响应结构导致拿不到，会抛错并把原始响应片段写进消息——届时需更新此处与 `wait_task` 的字段路径
- 常见失败：token 过期 / 额度耗尽（鉴权或配额错误）、PDF 加密、URL 不可达、版面极乱导致还原质量差
- 上传用预签名 URL（`PUT`，不带 `Content-Type`）；含特殊字符的文件名上传前可重命名
