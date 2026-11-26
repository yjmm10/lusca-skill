# SEO 与 GEO

SEO 负责被传统搜索引擎理解，GEO 指生成式引擎可见性：让 AI 回答时能准确引用本站事实。二者共同基础是可抓取、可核验、实体清晰的静态 HTML。

## 必须配置

- `canonical`：每个语言页面指向自身绝对 URL。
- `hreflang`：zh 与 en 互指，带 `x-default`。
- `title` / `description`：每页独立，中文自然、英文不生硬直译。
- Open Graph / Twitter Card：`og:title`、`og:description`、`og:image`、宽高与 `twitter:card`。
- `sitemap.xml`：包含两个语言的三页，使用真实 `site` 域名。
- `robots.txt`：允许抓取，指向 sitemap。
- JSON-LD：产品/软件实体 + Organization + FAQPage（仅在 FAQ 有真实内容时）。
- `llms.txt`：给出产品名、一句话定义、关键事实、页面链接和来源说明。

## JSON-LD 原则

结构化数据只写页面中真实存在的信息；`name`、`description`、`url`、`applicationCategory`、`author`、`dateModified` 要从 `product.json` 生成。不要在结构化数据里堆用户没提供的评分、价格、评价。

## llms.txt 结构

```markdown
# Product Name

> 一句话定义，必须与页面首屏一致。

- 面向谁：...
- 核心能力：...
- 数据更新时间：...
- 来源说明：...

## Pages
- [Landing](https://example.com/)
- [Data](https://example.com/data/)
- [About](https://example.com/about/)
- [English](https://example.com/en/)
```

## GEO 做法

- 用明确主谓宾句子定义产品，不写空泛形容词。
- 每个关键事实附近保留时间、单位与来源链接。
- FAQ 用用户真会问的问题，答案能在数据页找到依据。
- 保持标题层级与正文文本可抓取；不要把核心信息只画进图片。
- 更新事实时同步更新 `dateModified`、sitemap 与 `llms.txt`。

## 验证

构建后检查：页面源码能看到正文与元数据；sitemap URL 可访问；JSON-LD 可被解析；hreflang 成对；外链状态正常。线上索引结果属于外部因素，不承诺排名。
