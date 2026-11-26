---
name: {{PRODUCT_NAME}}
description: {{PRODUCT_TAGLINE_ZH}}
---

# {{PRODUCT_NAME}}

{{PRODUCT_NAME}} 是{{PRODUCT_SUMMARY_ZH}}站点包含落地页、数据页与关于页，默认中文，`/en/` 为英文。

## 快速开始

```bash
npm install
npm run dev
npm run build
npm run preview
```

## 页面与数据流

- `/`：落地页，展示 Hero、产品预览、核心指标、最新动态、能力与 CTA。
- `/data/`：数据页，展示完整指标、更新时间、来源与口径。
- `/about/`：关于页，包含产品、作者与免责声明。
- `src/data/product.json`：产品事实的单一源。
- `src/data/highlights.json`：由 `product.json` 派生的落地页摘要，不手动编辑。

更新数据后运行：

```bash
python ../../scripts/normalize_data.py src/data/product.json --output src/data/highlights.json
```

具体路径按本仓库相对位置调整；如果脚本不在相对路径上，使用安装该 skill 的绝对路径。

## 设计与国际化

- 设计 token 集中在 `src/styles/tokens.css`，组件只引用语义 token。
- 主题支持浅色、深色与跟随系统；URL 参数 `?theme=light|dark` 用于截图固定主题。
- 中文为默认语言，英文页面在 `/en/`；所有新增文案需同时补 zh/en。

## SEO / GEO

站点包含 canonical、hreflang、Open Graph、Twitter Card、sitemap、robots、JSON-LD 与 `llms.txt`。GEO 相关内容是清晰实体定义、稳定事实句、可抓取文本、FAQ 和来源链接；更新产品事实时同步检查 `src/pages/llms.txt.ts` 与结构化数据。

## 性能与缓存

默认静态输出，交互按需加载；图片保持明确尺寸并懒加载非首屏资源。部署缓存规则见 `public/_headers`、`vercel.json`、`netlify.toml` 中与平台匹配的文件；未使用的平台文件可删除。

## 文档

- `docs/product-overview.md`：定位、受众、数据来源与部署信息。
- `docs/ui-decisions.md`：组件调研与选型依据。
- `docs/screenshots.md`：页面截图预览索引。
- `docs/seo-geo.md`：索引与生成式引擎可见性说明。

## 部署

按 `--deploy` 参数生成的 workflow 或平台配置部署。GitHub Pages 部署时注意 `astro.config.mjs` 的 `base` 与仓库子路径一致。
