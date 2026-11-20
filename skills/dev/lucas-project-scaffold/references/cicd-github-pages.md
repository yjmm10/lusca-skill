# GitHub Pages CI/CD

## 适用判断

**可直接上 Pages**：纯静态站、文档站、无后端 SPA（含 Next/Astro 静态导出）。

**不可硬上 Pages**（给替代方案并主动提醒代价）：需要服务端运行时（用户登录、数据库、定时任务、私有 API 代理）→ 建议 Vercel / Netlify / 云服务器；提醒：Pages 免费但有 100GB/月带宽与 1GB 仓库软限，商业级流量另议。

## 搭建步骤

1. 复制 `assets/deploy-workflow.yml` 到 `.github/workflows/deploy.yml`
2. 按项目修改三处：构建命令（`npm run build` 等）、产物目录（`dist` / `build` / `out`）、Node 版本与包管理器（npm/pnpm/yarn 对应改 setup 与 install 命令）
3. 仓库 Settings → Pages → Source 选 **GitHub Actions**
4. README 写清访问地址 `https://<user>.github.io/<repo>/` 与部署触发条件（push 到 main）

## 常见坑（配置时主动检查）

- **子路径问题**：项目部署在 `/<repo>/` 而非根路径 → Vite 需设 `base: '/<repo>/'`；资源引用用相对路径；路由用 HashRouter 或配置 fallback
- **SPA 刷新 404**：把 `index.html` 复制一份为 `404.html` 一并发布
- **缓存策略**：`index.html` 不强缓存；带 hash 的 assets 可长缓存
- **构建密钥**：构建期需要的 token 走 Actions secrets（`secrets.XXX`），绝不写进仓库
- **首次开启**：仓库 Settings 里 Pages 未开启时 workflow 会 403，首次需手动到 Settings 确认
- **私有仓库**：Pages 在免费版私有仓库不可用，需提醒用户
