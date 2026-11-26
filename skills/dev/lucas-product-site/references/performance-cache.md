# 性能与缓存

目标是“静态优先、按需交互、缓存明确”。性能数字必须来自真实构建/测量；达不到目标时报告差距，不写虚假达标。

## 构建与加载

- Astro `output: 'static'`，默认不整站 hydration；交互组件用 `client:visible` 或 `client:idle`。
- 首屏 CSS 优先，非关键样式与脚本延后；避免阻塞渲染的第三方脚本。
- 预览图与截图放 `public/images/`，生成 WebP/AVIF 版本；`<img>` 写明确宽高、loading 与 decoding。
- 字体自托管、子集化并预加载关键字重；系统字体可作为无网络降级。
- 数据页筛选只在必要时加载客户端脚本；无 JS 时仍可读完整表格。
- 动效用 transform/opacity，避免触发布局抖动；预留图片与卡片空间控制 CLS。

## 预算

| 指标 | 目标 |
|------|------|
| LCP | ≤ 2.5s |
| CLS | ≤ 0.1 |
| INP | ≤ 200ms |
| 首屏 JS | 尽量 < 150KB |
| 单张预览图 | 尽量 < 200KB（视实际清晰度调整） |

这些是工程目标，不是承诺；用 Lighthouse、WebPageTest 或浏览器面板实测后记录结果。

## 缓存策略

- HTML：短缓存或 `no-cache` + 重新验证，保证内容更新及时。
- 带 hash 的 JS/CSS/图片：`public, max-age=31536000, immutable`。
- `sitemap.xml`、`robots.txt`、`llms.txt`：短缓存，便于更新后被抓取。
- 根据部署平台保留匹配文件：Netlify/Cloudflare `_headers`、Vercel `vercel.json`、GitHub Pages 依赖 CDN 默认策略并在文档中说明限制。
- 数据源更新后重新构建站点；不要在静态页里承诺实时性。

## 验证清单

- `npm run build` 成功。
- 检查构建产物里没有超大的未压缩图片或意外整站 bundle。
- 检查首屏正文是否在 HTML 源码中可抓取。
- 在桌面与移动视口检查 CLS、图片加载和主题切换。
- 记录实测数据与仍未优化项到 `docs/seo-geo.md`。
