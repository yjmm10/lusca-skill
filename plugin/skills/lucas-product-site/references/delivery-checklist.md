# 交付验收清单

按顺序检查，失败项写进交付说明，不要静默跳过。

## 品牌与数据

- [ ] 产品名由用户确认，短且可解释；基础撞名检查已记录。
- [ ] `docs/brand.md` 说明名字含义、候选与 logo 解释。
- [ ] `public/logo.svg`、`public/logo.png`、`public/favicon.svg` 存在。
- [ ] `src/data/product.json` 通过校验，`src/data/highlights.json` 由它派生。
- [ ] 示例数据明确标注，README 列出替换点。

## 页面与体验

- [ ] `/`、`/data/`、`/about/`、`/en/`、`/en/data/`、`/en/about/` 可访问。
- [ ] 关于页含产品、作者/团队、免责声明。
- [ ] 落地页最新区块来自 `highlights.latest`，指标来自 `highlights.metrics`。
- [ ] 数据条目有单位、周期、来源；移动端表格可读。
- [ ] 主题支持系统/浅色/深色，切换无闪烁；中英文互链。

## SEO / GEO / 性能

- [ ] canonical、hreflang、OG、sitemap、robots、JSON-LD、`llms.txt` 存在且内容一致。
- [ ] 首屏正文在静态 HTML 中可抓取。
- [ ] 图片有尺寸与 alt，非首屏资源懒加载。
- [ ] 缓存文件与部署平台匹配；构建成功。
- [ ] 实测性能数据记录到文档，未达标项如实说明。

## 文档与截图

- [ ] README、`docs/product-overview.md`、`docs/data-sources.md`、`docs/ui-decisions.md`、`docs/seo-geo.md`、`docs/screenshots.md` 齐全。
- [ ] 至少三张真实截图在 `docs/images/` 并被索引。
- [ ] 没有免责式尾巴、没有硬折行、没有占位图冒充真实截图。

## 验证命令

```bash
python <skill>/scripts/normalize_data.py <target>/src/data/product.json --output <target>/src/data/highlights.json
python <skill>/scripts/validate_site.py <target> --strict
npm --prefix <target> run build
```
