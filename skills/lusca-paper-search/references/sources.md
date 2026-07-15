# 各检索来源：依赖、Token 与失败模式

本文件汇总 `lusca-paper-search` 八大 API 来源的运行依赖、凭证要求与失败行为。
模型知识源（`model_knowledge`）无 API 调用，其用法见 `SKILL.md`「model_knowledge 源」。

## 依赖总览

| 来源 | 依赖 | 凭证 |
|:---|:---|:---|
| arXiv | 仅标准库（arXiv API） | 无 |
| DBLP | DBLP API | 无 |
| OpenAlex | OpenAlex API | 无 |
| OpenReview | `pip install openreview-py` | 可选（`_env.py` 读 `.env`） |
| Semantic Scholar | Semantic Scholar API | 无 |
| Crossref | Crossref API | 无 |
| DeepXiv | 仅标准库（Agentic Data Interface @ `data.rag.ac.cn`） | Token 可选（`DEEPXIV_TOKEN`） |
| Sciverse | 仅标准库（`api.sciverse.space/meta-search`） | 必需（`SCIVERSE_API_TOKEN`，`sv-...`） |

## 失败模式与降级

- **聚合器行为**：`search_papers.py` 用 `ThreadPoolExecutor` 并发查询各来源。
  某来源失败时，聚合器捕获异常、把错误打到 stderr、**继续**其余来源——不会因单一来源崩溃而整检索中止。
  脚本还**惰性导入**各来源模块：某来源的可选依赖缺失（如未装 `openreview-py`）只跳过该来源，不影响其它。
- **绝不明重试**：某来源出错时，把 stderr 消息原样上报用户，而非盲目重试。
- **OpenReview**：未装 `openreview-py` 时该来源被跳过并打印 import 失败提示；装好后通过 `_env.py`
  读取 `.env`（`OPENREVIEW_USERNAME` / `OPENREVIEW_PASSWORD` 等）。
- **DeepXiv**：Token 可选。`DEEPXIV_TOKEN` 解锁全部查询；无 Token 时仅三个免费查询
  （`transformer`、`attention mechanism`、`large language model`）可用，其余返回 401。
- **Sciverse**：必需 `SCIVERSE_API_TOKEN`（`sv-...` 前缀）；缺失会抛出明确错误。Sciverse 纯 API 检索，
  每条结果的 `doc_id` 被保留，`url` 回退为 Google Scholar 标题检索以保持可点击。

## 凭证配置

凭证统一由 `scripts/_env.py` 的 `load_env_once()` 在聚合器启动前加载（读 `scripts/.env` 或 skill 根 `.env`，
找不到则 no-op）。这样即便经 bash 直接调用、未 source `.env`，聚合器仍能取到凭证。

涉及的环境变量：

| 变量 | 用途 | 必需性 |
|:---|:---|:---|
| `DEEPXIV_TOKEN` | DeepXiv 全量查询 | 可选（无则限三个免费查询） |
| `SCIVERSE_API_TOKEN` | Sciverse 检索 | 必需 |
| `OPENREVIEW_USERNAME` / `OPENREVIEW_PASSWORD` | OpenReview 登录态 | 可选（影响命中率） |

## 已存在但聚合器未默认启用的脚本

`scripts/` 下还保留了两个来源脚本，但 `search_papers.py` 的 `_SOURCE_MODULE` **未**默认启用：

- `search_papers_by_google_scholar.py`：需 `scholarly`，默认禁用（聚合器中注释掉）。
- `search_papers_by_exa.py`：保留备用，未接入聚合器。

需要时可手动调用这两个脚本，或在 `_SOURCE_MODULE` 中取消注释接入。
