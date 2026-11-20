# 环境参数管理

## 文件约定

- `.env.example`：参数**全集** + 行内注释 + 示例值（绝不含真实密钥），**进仓库**
- `.env`：本地真实值，**绝不进仓库**（`.gitignore` 必须包含 `.env`）
- `docs/environment.md`：参数总说明表，给人和 agent 看

## docs/environment.md 表格格式

| 参数 | 用途 | 默认值 | 示例 | 敏感级别 | 备注 |
|------|------|--------|------|----------|------|
| `PORT` | 服务监听端口 | `8000` | `8000` | 公开 | — |
| `DATABASE_URL` | 数据库连接串 | 无 | `postgres://user:pass@host:5432/db` | **机密** | 生产从部署平台 secrets 注入 |
| `VITE_API_BASE` | 前端 API 地址 | `/api` | `https://api.example.com` | 公开 | 前端可见 |

## 规则（同时写入 agent 文件的变更检查清单）

1. 代码中新暴露一个环境参数 → **当次**同步更新 `.env.example` 与 `docs/environment.md`，缺一不可
2. 改名 / 删除参数 → 同一次提交里清理所有相关环境文件与文档
3. 启动时集中校验（`zod` / `pydantic-settings` / `envalid`），缺参数直接 fail-fast；业务代码不散落 `process.env.X` / `os.environ["X"]`，统一从配置模块取
4. 敏感分级：公开 / 内部 / 机密；机密只进部署平台 secrets，不进任何仓库文件
5. 前端可见的参数（`VITE_` / `NEXT_PUBLIC_` / `EXPO_PUBLIC_` 前缀）会被打进产物，**一律视为公开**，绝不放机密
