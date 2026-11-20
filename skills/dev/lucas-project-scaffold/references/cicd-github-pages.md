# GitHub Pages CI/CD

依据：GitHub 官方 Pages + Actions 部署文档、Vite 官方部署指南、`actions/starter-workflows` 官方模板。

## 适用判断

**可直接上 Pages**：纯静态站、文档站、无后端 SPA（含 Next/Astro 静态导出）。

**不可硬上 Pages**（给替代方案并主动提醒代价）：需要服务端运行时（用户登录、数据库、定时任务、私有 API 代理）→ 建议 Vercel / Netlify / 云服务器；提醒：Pages 免费但有 100GB/月带宽与 1GB 仓库软限，商业级流量另议。私有仓库的 Pages 需要付费计划，免费账户私有仓库不可用——先确认仓库可见性。

## 官方 action 链路（模板已内置，改动时保持此组合）

| Action | 作用 |
|--------|------|
| `actions/checkout@v4` | 拉取代码 |
| `actions/setup-node@v4` | Node 环境与依赖缓存（静态站无构建可省） |
| `actions/configure-pages@v5` | 启用/配置 Pages，收集部署元数据（base path 等） |
| `actions/upload-pages-artifact@v3` | 把构建产物打包上传为 Pages artifact |
| `actions/deploy-pages@v5` | 真正发布到 Pages |

## artifact 约束（upload-pages-artifact 的硬性要求）

- 产物是 **gzip 压缩的单个 tar**
- 解压后 **≤ 10GB**
- **不含符号链接 / 硬链接**（构建工具一般不会产生，但自写打包脚本要注意）
- **入口文件（index.html）位于 artifact 顶层**——上传的 `path` 目录必须直接就是站点根

## 搭建步骤

1. 复制 `assets/deploy-workflow.yml` 到 `.github/workflows/deploy.yml`
2. 按项目修改四处：触发分支、Node 版本与包管理器（npm ci → pnpm install --frozen-lockfile / yarn --frozen-lockfile）、构建命令、产物目录（`path: dist`）
3. 仓库 **Settings → Pages → Source 选「GitHub Actions」**——没选之前 workflow 会 403，这是最常见的「配置都对了却不部署」原因
4. README 写清访问地址 `https://<user>.github.io/<repo>/` 与部署触发条件（push 到 main）

## 子路径 base（最容易踩的坑）

项目页部署在 `https://<user>.github.io/<repo>/`，**不是根路径**：

- Vite：`vite.config.ts` 设 `base: '/<repo>/'`（推荐），或 `base: './'` 用相对路径；代码里动态拼资源/路由 URL 用 `import.meta.env.BASE_URL`
- 用户主页站（仓库名 = `<user>.github.io`）或绑定自定义域名 → `base: '/'`
- React Router / Vue Router：history 模式在子路径下刷新会 404；简单项目改用 HashRouter，或构建后把 `index.html` 复制一份为 `404.html` 作为 SPA fallback
- `configure-pages` 会把正确的 base path 注入构建环境，模板里已调用；自定义构建脚本时留意读取它

## 其他常见坑（配置时主动检查）

- **缓存策略**：`index.html` / `404.html` 不强缓存（要拿到最新版本）；带 hash 的 assets 可长缓存
- **构建密钥**：构建期需要的 token 走 Actions secrets（`secrets.XXX`），绝不写进仓库
- **并发部署**：`concurrency.group: pages` 防止两次 push 同时部署打架；生产部署不要 `cancel-in-progress: true`（会打断正在进行的发布）
- **权限**：workflow 顶层 `permissions` 必须含 `pages: write` 与 `id-token: write`，缺了 deploy 步骤会 403
- **首次开启**：也可以在 `configure-pages` 步骤加 `enablement: true` 让 action 自动开启 Pages，但需要触发者有仓库管理权限；失败仍需手动到 Settings 开启
