# GitHub Pages CI/CD

依据：GitHub 官方 Pages + Actions 部署文档、Vite 官方部署指南、`actions/starter-workflows` 官方模板。

> 部署需要准备哪些参数（域名、平台凭证、secrets）、去哪申请，见 `references/deploy-params.md`；本文件管「workflow 怎么写、坑怎么避」。

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
2. 按项目修改四处：

| 改动点 | npm | pnpm | yarn |
|--------|-----|------|------|
| 安装 | `npm ci` | `pnpm install --frozen-lockfile` | `yarn --frozen-lockfile` |
| setup-node cache | `cache: npm` | `cache: pnpm` | `cache: yarn` |
| （pnpm 另需） | — | 加一步 `pnpm/action-setup@v4`（在 setup-node 之前） | — |

   以及：触发分支（默认 `main`）、构建命令（`npm run build`）、产物目录（`path: dist`；CRA=build，Next export=out，Astro=dist）
3. 仓库 **Settings → Pages → Source 选「GitHub Actions」**——没选之前 workflow 会 403，这是最常见的「配置都对了却不部署」原因
4. README 写清访问地址 `https://<user>.github.io/<repo>/` 与部署触发条件（push 到 main）

## 子路径 base（最容易踩的坑）

项目页部署在 `https://<user>.github.io/<repo>/`，**不是根路径**：

```ts
// vite.config.ts —— 仓库名 pages-demo 时：
export default defineConfig({
  base: "/pages-demo/",          // 用户主页站（仓库名=<user>.github.io）或自定义域名用 "/"
});
```

- 代码里动态拼资源/路由 URL 用 `import.meta.env.BASE_URL`，不要手写 `/assets/...`
- 用户主页站（`<user>.github.io` 仓库）或绑定自定义域名 → `base: "/"`

**SPA 刷新 404 修复**（history 路由必做；简单项目直接改用 HashRouter 更省事）：

```yaml
      - name: Build
        run: npm run build
      - name: SPA fallback (404.html)
        run: cp dist/index.html dist/404.html   # 路径按产物目录改
```

- `configure-pages` 会把正确的 base path 注入构建环境，模板里已调用；自定义构建脚本时留意读取它

## 部署后验证（写完 workflow 当次就做，或提醒用户做）

1. push 后打开仓库 **Actions** 页，确认最新一次 run 全绿（build + deploy 两个 job）
2. 打开 `https://<user>.github.io/<repo>/`，确认页面能看（不是 404 / 白屏 / GitHub 404 页）
3. **强刷**（Ctrl+Shift+R）确认拿到的不是旧缓存
4. F12 看 Network：js/css/图片有没有 404（有 → 大概率 base path 问题）
5. SPA 项目：从首页点路由跳转后，**直接刷新该路由 URL**，确认不 404
6. 手机尺寸（DevTools 切换）打开确认布局不破

## 故障速查表（symptom → 原因 → 修复）

| 症状 | 原因 | 修复 |
|------|------|------|
| deploy job 403 | Pages Source 未设为 GitHub Actions，或私有仓库无付费计划 | Settings→Pages 改 Source；确认仓库可见性 |
| 页面白屏，Console 大量 404（js/css） | base path 没配，资源请求打到根路径 | Vite 设 `base: '/<repo>/'`，动态 URL 用 `import.meta.env.BASE_URL` |
| 首页正常，刷新子路由 404 | 无 SPA fallback | 复制 index.html 为 404.html，或改 HashRouter |
| 部署成功但内容是旧版 | index.html 被浏览器/CDN 强缓存 | 确认 index.html 未带强缓存头；强刷验证 |
| build 成功，deploy 卡住不动 | 并发部署被 cancel-in-progress 打断 | `cancel-in-progress: false`（官方建议） |
| artifact 上传失败 | 产物里有 symlink，或 path 指错目录 | 检查构建配置；确认 `path` 指向构建产物根 |

## 其他常见坑（配置时主动检查）

- **缓存策略**：`index.html` / `404.html` 不强缓存（要拿到最新版本）；带 hash 的 assets 可长缓存
- **构建密钥**：构建期需要的 token 走 Actions secrets（`secrets.XXX`），绝不写进仓库
- **`.nojekyll`**：用 upload-pages-artifact 时无需关心 Jekyll 处理；若是「直接 push 静态文件到 gh-pages 分支」的老式方案才需要在产物根放 `.nojekyll`（避免 `_` 开头文件被 Jekyll 吞掉）
- **首次开启**：也可以在 `configure-pages` 步骤加 `enablement: true` 让 action 自动开启 Pages，但需要触发者有仓库管理权限；失败仍需手动到 Settings 开启
- **自定义域名**：把 CNAME 文件放进产物根，并在 DNS 加 CNAME 记录；启用「Enforce HTTPS」
