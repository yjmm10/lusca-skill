# 环境参数管理

依据：The Twelve-Factor App「Config」原则（配置与代码严格分离、配置存于环境变量）及其现代补充（机密与普通配置分开处理）。

## 判断什么是「环境参数」

判据：**换一个部署环境（开发/测试/生产）值会不同的东西**。

- 算配置：数据库/缓存等外部服务地址与凭证、第三方 API key、每环境不同的主机名/端口/开关
- 不算配置（属于代码）：路由表、模块装配方式、不随部署变化的内部设置——即使它碰巧写在叫 config 的文件里
- 检验法：**代码库随时开源也不泄露任何凭证**，才算把配置分离干净

确定部署目标后，部署相关参数（域名、平台凭证、数据库、对象存储、邮件、OAuth、支付、AI API 等）的完整清单、获取入口与放置位置，见 `references/deploy-params.md`；本文件只管「参数如何管理」，那边管「要哪些、去哪拿」。

## 文件约定

- `.env.example`：参数**全集** + 行内注释 + 示例值（绝不含真实密钥），**进仓库**
- `.env`：本地真实值，**绝不进仓库**（`.gitignore` 必须包含 `.env`，已在 dir-structures 的 starter 里）
- `docs/environment.md`：参数总说明表，给人和 agent 看

## .env.example 示例（直接照此格式写）

```bash
# ===== 服务 =====
# 服务监听端口
PORT=8000
# 环境名：local | dev | prod（影响日志级别等行为开关）
APP_ENV=local

# ===== 数据库 =====
# PostgreSQL 连接串（生产从平台 secrets 注入，此处只放本地示例）
DATABASE_URL=postgres://postgres:postgres@localhost:5432/app

# ===== 第三方服务 =====
# 对象存储（公开桶）
S3_BUCKET=my-app-assets
# 对象存储访问密钥（机密：本地随便填，生产走 secrets）
S3_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
S3_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# ===== 前端可见（VITE_ 前缀会被打进产物，一律视为公开）=====
VITE_API_BASE=/api
```

## docs/environment.md 表格格式

| 参数 | 用途 | 默认值 | 示例 | 敏感级别 | 备注 |
|------|------|--------|------|----------|------|
| `PORT` | 服务监听端口 | `8000` | `8000` | 公开 | — |
| `DATABASE_URL` | 数据库连接串 | 无 | `postgres://user:pass@host:5432/db` | **机密** | 生产从部署平台 secrets 注入 |
| `VITE_API_BASE` | 前端 API 地址 | `/api` | `https://api.example.com` | 公开 | 前端可见 |

## 配置模块模板（业务代码统一从这里取，不散落读 env）

TypeScript（zod）：

```ts
// src/config.ts —— 业务代码只 import { config } from "./config"
import { z } from "zod";

const schema = z.object({
  PORT: z.coerce.number().default(8000),
  DATABASE_URL: z.string().url(),
  VITE_API_BASE: z.string().default("/api"),
});

export const config = schema.parse(process.env);
// 启动即校验，缺参/非法直接 fail-fast，错误信息列出全部缺失项
```

Python（pydantic-settings）：

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8000
    database_url: str          # 无默认值 → 未设置时启动即报错
    app_env: str = "local"

    model_config = {"env_file": ".env"}

settings = Settings()
```

## 规则（同时写入 agent 文件的变更检查清单）

1. 代码中新暴露一个环境参数 → **当次**同步更新 `.env.example` 与 `docs/environment.md`，缺一不可
2. 改名 / 删除参数 → 同一次提交里清理所有相关环境文件与文档
3. 启动时集中校验（`zod` / `pydantic-settings` / `envalid`），缺参数直接 fail-fast；业务代码不散落 `process.env.X` / `os.environ["X"]`，统一从配置模块取
4. 敏感分级：公开 / 内部 / 机密；机密只进部署平台 secrets，不进任何仓库文件
5. 前端可见的参数（`VITE_` / `NEXT_PUBLIC_` / `EXPO_PUBLIC_` 前缀）会被打进产物，**一律视为公开**，绝不放机密

## 部署平台 secrets 的具体用法（以 GitHub Actions 为例）

1. 仓库页 → Settings → Secrets and variables → Actions → New repository secret，逐个添加（如 `DATABASE_URL`）
2. workflow 里注入给部署/运行步骤：

```yaml
      - name: Run migration
        run: npm run db:migrate
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

3. 提醒用户：secrets 不会传给 fork 的 PR workflow；轮换密钥时仓库 secrets 与本地 `.env` 都要改

## 机密处理的现代补充（12-factor 的已知局限）

环境变量适合**普通配置**（地址、端口、开关），但对**真正的机密**要更小心——env var 会通过子进程继承、`/proc` 读取、崩溃上报、`docker inspect`、启动日志等多条路径泄露。因此：

- 普通配置 → 环境变量（本技能默认方案）
- 真机密 → 部署平台的 secret 管理（GitHub Actions Secrets、云平台 Secret Manager），注入方式优先「挂载文件」而非 env var（如平台支持）
- 本地开发用 `.env`（已 gitignore）即可，生产绝不用 `.env` 文件，由运维/平台注入

发现用户把密码、token 写进 `.env.example`、README、代码常量或提交历史时，**当场提醒并给迁移方案**（轮换密钥 + 改用 secrets 注入）。
