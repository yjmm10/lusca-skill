# 部署参数清单与获取指引

用法：第 4 / 6 步确定部署目标与依赖服务后，按本清单逐项和用户确认「**谁去申请、在哪申请、申请完放到哪**」。原则：公开参数进仓库（`.env.example` / workflow env），**机密参数只进平台 secrets 或用户本地 `.env`**。

## 0. 通用（无论部署到哪）

| 参数 | 用途 | 在哪获取 | 敏感级别 | 放到哪 |
|------|------|----------|----------|--------|
| 域名 | 访问地址 | 注册商：阿里云/腾讯云、Namecheap、Cloudflare Registrar（成本价、自带 DNS） | 公开 | README、DNS 控制台 |
| DNS 解析记录 | 把域名指向部署平台 | 域名所在控制台加 A / CNAME 记录（记录值见下方各平台） | 公开 | DNS 控制台 |
| Git 仓库 | CI 拉代码 | github.com 新建（或用户已有） | 公开 | README、workflow |

## 1. GitHub Pages（纯前端静态）——几乎零参数

`GITHUB_TOKEN` 由 Actions **自动注入**，不需要也不应该手动创建。需要人工做的只有：

1. 仓库 **Settings → Pages → Source 选「GitHub Actions」**（不选则部署 job 403）
2. 构建期需要公开参数（如 `VITE_API_BASE`）→ 直接写进 workflow 的 build step：
   ```yaml
   - name: Build
     run: npm run build
     env:
       VITE_API_BASE: https://api.example.com
   ```
3. 构建期需要机密（少见，如拉私有包的 token）→ 仓库 **Settings → Secrets and variables → Actions → New repository secret**，workflow 里用 `secrets.XXX` 引用
4. 自定义域名：DNS 加 CNAME 记录指向 `<user>.github.io`；产物根放 `CNAME` 文件（内容=域名）；Settings → Pages 填域名并开启 **Enforce HTTPS**

## 2. Vercel（前端 / Serverless 全栈）

推荐「Git 集成」：GitHub 仓库连上 Vercel 后 push 自动部署，**可以不需要 token**。以下参数仅在用 GitHub Actions 手动部署时需要：

| 参数 | 用途 | 在哪获取 | 敏感级别 |
|------|------|----------|----------|
| `VERCEL_TOKEN` | API 部署凭证 | vercel.com → 右上头像 → **Account Settings → Tokens → Add**，创建后只显示一次 | 机密 |
| `VERCEL_ORG_ID` | 团队/个人空间 ID | 项目 **Settings → General**；或首次本地 `vercel` 部署后查看生成的 `.vercel/project.json` | 内部 |
| `VERCEL_PROJECT_ID` | 项目 ID | 同上 | 内部 |
| 运行时环境变量 | 数据库/第三方 key 等 | 项目 **Settings → Environment Variables**，分 Production / Preview / Development 三套分别配 | 按项分级 |

## 3. Netlify

| 参数 | 用途 | 在哪获取 | 敏感级别 |
|------|------|----------|----------|
| `NETLIFY_AUTH_TOKEN` | API 部署凭证 | app.netlify.com → **User settings → Applications → Personal access tokens** | 机密 |
| `NETLIFY_SITE_ID` | 指定站点 | 站点 **Site configuration → Site details → Site ID** | 内部 |

## 4. 云服务器自托管（全栈 / 纯后端）

| 参数 | 用途 | 在哪获取 / 生成 | 敏感级别 |
|------|------|-----------------|----------|
| 服务器 IP + SSH 端口 | 登录与部署目标 | 云控制台实例详情（阿里云 ECS / 腾讯云 CVM / AWS Lightsail） | 内部 |
| `SSH_PRIVATE_KEY` | CI 免密登录 | 本地执行 `ssh-keygen -t ed25519 -C "deploy"` 生成；**公钥**追加到服务器 `~/.ssh/authorized_keys`，**私钥**只进 GitHub secrets，绝不进仓库/聊天 | 机密 |
| SSH 登录用户 | — | 推荐新建低权限用户 `deploy`，不用 root | 内部 |
| 域名备案 | 国内服务器**必须 ICP 备案** | 云商备案系统提交，通常 1-3 周（提前提醒用户！影响上线时间） | 公开 |
| HTTPS 证书 | 加密访问 | Let's Encrypt 免费：服务器上 `sudo certbot --nginx -d <域名>`，自动续期 | — |
| 反向代理 | 80/443 → 应用端口 | Nginx / Caddy 配置（Caddy 自动 HTTPS，更省事） | — |

CI 部署常用：GitHub Actions 里用 `appleboy/ssh-action`（secrets 放 `SSH_PRIVATE_KEY`、`SERVER_HOST`、`SERVER_USER`）执行拉代码/重启脚本。

## 5. 常见后端依赖服务：参数与获取入口

### 数据库

| 服务 | 参数 | 在哪获取 |
|------|------|----------|
| 自建 PostgreSQL / MySQL | `DATABASE_URL` | 自己定连接串：`postgres://用户:密码@主机:5432/库名` |
| Supabase | `SUPABASE_URL`、`SUPABASE_ANON_KEY`（公开）、`SUPABASE_SERVICE_ROLE_KEY`（**机密**） | supabase.com 项目 → **Project Settings → API** |
| Neon / PlanetScale | `DATABASE_URL` | 控制台 **Connection string** 一键复制 |
| SQLite | `DATABASE_PATH` | 本地文件路径即可 |

### 对象存储（图片 / 文件上传）

| 服务 | 参数 | 在哪获取 |
|------|------|----------|
| 阿里云 OSS | `OSS_ACCESS_KEY_ID`、`OSS_ACCESS_KEY_SECRET`、`OSS_BUCKET`、`OSS_REGION` | OSS 控制台建 Bucket；RAM 控制台建**子账号 + 最小权限**策略后创建 AccessKey（不要用主账号 key） |
| 腾讯云 COS | `COS_SECRET_ID`、`COS_SECRET_KEY`、`COS_BUCKET`、`COS_REGION` | 同上思路：CAM 子账号 + COS Bucket |
| Cloudflare R2 | `R2_ACCOUNT_ID`、`R2_ACCESS_KEY_ID`、`R2_SECRET_ACCESS_KEY`、`R2_BUCKET` | Cloudflare Dashboard → R2 → **Manage R2 API Tokens** |
| AWS S3 | `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`S3_BUCKET`、`AWS_REGION` | IAM 建用户 + S3 最小权限策略 |

### 邮件发送

| 服务 | 参数 | 在哪获取 |
|------|------|----------|
| SMTP（QQ / 163 / 企业邮箱） | `SMTP_HOST`、`SMTP_PORT`、`SMTP_USER`、`SMTP_PASS` | 邮箱设置里开启 SMTP 服务，获得**授权码**（不是邮箱登录密码） |
| Resend | `RESEND_API_KEY` | resend.com → **API Keys** → Create |
| SendGrid | `SENDGRID_API_KEY` | app.sendgrid.com → **Settings → API Keys** |

### OAuth 登录

| 服务 | 参数 | 在哪获取 |
|------|------|----------|
| GitHub | `GITHUB_CLIENT_ID`、`GITHUB_CLIENT_SECRET` | github.com → Settings → **Developer settings → OAuth Apps → New OAuth App** |
| Google | `GOOGLE_CLIENT_ID`、`GOOGLE_CLIENT_SECRET` | console.cloud.google.com → **APIs & Services → Credentials → Create OAuth client**，回调 URI 填 `https://<域名>/api/auth/callback/google` |
| 微信开放平台 | `WECHAT_APP_ID`、`WECHAT_APP_SECRET` | open.weixin.qq.com 创建网站应用（**需企业资质**，个人做不了要提前说） |

### 支付

| 服务 | 参数 | 在哪获取 |
|------|------|----------|
| Stripe | `STRIPE_SECRET_KEY`、`STRIPE_WEBHOOK_SECRET` | dashboard.stripe.com → **Developers → API keys / Webhooks**（测试模式 key 以 `sk_test_` 开头） |
| 支付宝 / 微信支付 | `APP_ID`、商户私钥、平台证书 | 商户平台申请（**需营业执照**），流程长，提醒用户尽早启动 |

### 短信

| 服务 | 参数 | 在哪获取 |
|------|------|----------|
| 阿里云 SMS | `ALIYUN_SMS_ACCESS_KEY_ID`、`ALIYUN_SMS_ACCESS_KEY_SECRET`、`SMS_SIGN_NAME`、`SMS_TEMPLATE_CODE` | 控制台开通短信服务 → **签名与模板报备**（需审核）→ RAM AccessKey |

### AI API

| 服务 | 参数 | 在哪获取 |
|------|------|----------|
| OpenAI | `OPENAI_API_KEY` | platform.openai.com → **API keys** |
| Anthropic | `ANTHROPIC_API_KEY` | console.anthropic.com → **API Keys** |
| DeepSeek / Moonshot / 通义 / 智谱 | `<厂商>_API_KEY` | 各家开放平台控制台，流程类似 |

## 6. 落地规则（与 env-management.md 联动）

1. 每确定一个依赖服务 → 立即把其参数补进 `.env.example` 与 `docs/environment.md`，标注敏感级别，并在备注列写上「获取入口：见 deploy-params.md 第 X 节」
2. 机密参数：**引导用户自己去对应控制台创建**，粘贴进平台 secrets 或本地 `.env`；让用户把真实密钥贴进聊天是下策——如已贴出，提醒泄漏风险并建议用后轮换
3. `.env.example` 里的示例值用占位符或官方文档示例 key（如 `AKIAIOSFODNN7EXAMPLE`），绝不用真实 key
4. 上线前核对：代码引用的每个 env 参数，`.env.example` 里有行、secrets/`.env` 里有值、`docs/environment.md` 里有说明，三者缺一不可
