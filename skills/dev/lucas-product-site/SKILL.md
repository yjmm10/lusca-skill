---
name: lucas-product-site
description: >-
  为产品/工具/项目搭建静态产品官网：落地页 + 数据页 + 关于页，数据页作为事实单一源，落地页最新区块从产品数据派生；含 Astro+TS+Tailwind 骨架、深浅主题与跟随系统、中英文、SEO/GEO、组件调研、性能与缓存、品牌命名与 SVG/PNG logo、说明文档和页面截图。用户提到做产品站、产品官网、静态展示站、落地页、数据展示页、关于页、项目主页、官网改版、给产品做个网站、product site、landing page、data page、about page、SEO/GEO、多语言官网、深浅主题官网、产品 logo 与截图时使用本技能——哪怕只说“帮我给这个项目做个官网”也走本技能。
version: "0.1.0"
author: lucas
user-invocable: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch
---

# lucas-product-site — 静态产品站搭建

输入产品资料/数据 + 约束 → 产出可直接运行、可部署、可索引的静态产品站：落地页、数据页、关于页，以及品牌、文档、截图和验证结果。默认技术路线是 **Astro + TypeScript + Tailwind CSS**；动态交互以岛屿方式按需加载，保持静态优先。

## 输入与产出

- **输入**：产品一句话定位、目标用户、产品数据（JSON/MDX/CSV/API 链接/文本表格均可）、可选参考站、已有 logo、部署平台、语言与品牌偏好。
- **产出**：Astro 项目骨架、统一设计 token、三页内容、中英文与主题切换、SEO/GEO 文件、组件调研记录、logo SVG/PNG、README/文档、页面截图、验证报告。
- **数据边界**：数据页是事实单一源；落地页的“最新动态”“核心指标”“精选能力”必须从同一份产品数据派生，不另写一套可能冲突的文案。

## 红线

- **不臆造事实**：指标、客户、奖项、日期、链接、引用必须来自用户提供的数据或可核验来源；缺数据时用明确标注为“示例”的结构化占位，并在 README 列出替换点。
- **组件要查证**：选型前查官方文档/GitHub 的维护状态、版本、许可证、无障碍、主题与国际化支持；把依据写进 `docs/ui-decisions.md`，不要凭印象点名组件。
- **命名要确认**：先发散再收敛，短名优先（单词或神话/东西方文化意象），做 GitHub/npm/域名基础可用性检查；商标与实际可用性只提示人工核验，不宣称已清权。
- **参考页只借结构**：参考站只提炼信息层级和布局，不复制代码、文案、图片或品牌资产。
- **文档按专业标准交付**：保留原 frontmatter；正文段落一项一行、不硬换行；结尾不写“AI 生成/仅供参考/欢迎指正”这类免责尾巴。关于页里的“免责声明”是产品内容，按事实写清边界即可。

## 主流程

### 1. 确认约束

问清并在 `docs/product-overview.md` 记录：产品是什么、给谁看、数据从哪里来、默认语言（zh/en）、部署平台、是否需要展示真实截图、是否已有品牌名与 logo。用户未指定时给出 2-4 个选项，不替用户拍板。

数据“最新内容”的规则：无论原始来源是本地文件、API 还是表格，都先归一到 `src/data/product.json`，再从 `updates`、`metrics`、`features` 派生落地页摘要；落地页不直接维护另一份“最新消息”。

### 2. 命名与品牌

按 `references/naming-brand.md` 发散 5-10 个短名 → 筛 2-3 个 → 基础撞名检查 → 用户确认。优先一个词、好读、能讲出意象（如神话/天文/器物/东方意象），避免多个英文单词用连字符硬拼。logo 的图形语义必须能说回名字含义，产出 `public/logo.svg` 与 `public/logo.png`（至少 512×512），并派生 favicon/OG 图。

### 3. 归一产品数据

按 `references/data-contract.md` 把来源数据映射成统一 schema；运行 `scripts/normalize_data.py` 校验并生成 `src/data/highlights.json`。每条指标保留 `label/value/unit/period/source`，每条动态保留 `date/title/summary/source`，允许追溯来源。字段缺失时留空或标示例，不补造。

### 4. 调研 UI 组件

按 `references/ui-research.md` 检索官方组件库文档与技术博客，至少 3 个核心来源；用“可维护性 / 无障碍 / 包体 / 主题与 i18n / 许可证 / 与 Astro 集成”六维比较。结论落到 `docs/ui-decisions.md`。默认优先 Tailwind 样式层 + 原生 Astro 组件；只在图表、表格、轮播等确有收益时引入 React 岛屿或轻量组件。

### 5. 生成骨架

运行 `scripts/init_project.py` 创建项目。脚本负责稳定结构，不替代设计判断；随后按产品数据替换示例文案、图片和颜色，并把组件调研结论落到代码。

### 6. 页面与视觉

- **落地页**：一屏一个主张，顺序为 Hero → 产品渲染图/界面预览 → 核心指标（最多 3-6 个，按重要性）→ 最新动态（来自 `highlights.json`）→ 能力/场景 → 证据/FAQ → CTA。动效只服务于理解：进场渐显、指标轻动、预览切换；避免自动轮播打断阅读。
- **数据页**：展示完整条目、筛选/排序、更新时间、来源链接、口径说明。表格在移动端转卡片，关键列固定或优先显示；空状态、加载状态和异常状态都要可解释。
- **关于页**：产品为何存在、作者/团队、可核验链接、联系方式、免责声明；免责声明写清数据时效、非建议声明、商标归属等具体边界，不写模板腔。
- **视觉**：单一 token 文件控制颜色/字体/间距/圆角/阴影；主色从品牌色派生，语义色跟随深浅主题；标题层级和留白体现专业权威感，不用密集卡片墙。数据条目先回答“这是什么、为什么重要、数据何时、来自哪里”。

### 7. SEO / GEO / 多语言 / 主题

按 `references/seo-geo.md` 配 canonical、hreflang、OG/Twitter、sitemap、robots、JSON-LD、`llms.txt`；GEO 指生成式引擎可见性，靠清晰实体定义、稳定事实句、可抓取文本、FAQ 与来源链接，不靠堆关键词。按 `references/i18n-theme.md` 实现 zh 默认、`/en/` 英文、主题跟随系统且可手动切换、无 FOUC；截图脚本通过 `?theme=light|dark` 固定主题。

### 8. 性能与缓存

按 `references/performance-cache.md` 保持静态输出、按需 hydration、图片 WebP/AVIF 与明确尺寸、字体子集化、关键 CSS、懒加载非首屏资源。为静态资产生成不可变缓存策略（按部署平台写入 `_headers` / `vercel.json` / `netlify.toml`），HTML 用短缓存或重新验证。目标：LCP ≤ 2.5s、CLS ≤ 0.1、INP ≤ 200ms、首屏 JS 尽量 < 150KB；达不到时报告实际值与取舍，不谎报达标。

### 9. 验证、截图与交付

运行 `scripts/validate_site.py <target> --strict`；启动 `npm run dev` 后用 `scripts/capture_screenshots.py` 截取至少落地页/数据页/关于页的中文浅色预览，推荐再补深色与英文。截图写入 `docs/images/`，`docs/screenshots.md` 建索引。交付时给出项目路径、关键文件、验证结果、未确认事项，以及 1-3 条后续衔接建议。

## 脚本用法

在仓库根执行，把 `<skill>` 替换为 `skills/dev/lucas-product-site`：

```bash
python <skill>/scripts/init_project.py <目标目录> --name "Aether" --domain "example.com" --description "一句话定位" --deploy github
python <skill>/scripts/normalize_data.py <目标目录>/src/data/product.json --output <目标目录>/src/data/highlights.json
python <skill>/scripts/validate_site.py <目标目录> --strict
python <skill>/scripts/capture_screenshots.py <目标目录> --url http://localhost:4321
```

`init_project.py` 默认不覆盖非空目录；需要合并时先备份再手动处理，避免误删用户文件。`capture_screenshots.py` 依赖本地可用的 Playwright，不可用时输出人工截图步骤而不伪造截图文件。

## Reference 文件索引

| 文件 | 何时 Read |
|------|-----------|
| `references/naming-brand.md` | 第 2 步起名、检查撞名、确定 logo 意象时 |
| `references/data-contract.md` | 第 3 步把任意来源映射为产品数据、派生落地页最新内容时 |
| `references/ui-research.md` | 第 4 步联网调研组件、写 `docs/ui-decisions.md` 时 |
| `references/architecture-pages.md` | 第 6 步设计三页信息层级、组件边界与交互动效时 |
| `references/seo-geo.md` | 第 7 步配置 SEO/GEO、结构化数据与索引文件时 |
| `references/i18n-theme.md` | 第 7 步做中英文与深浅主题、避免 FOUC 时 |
| `references/performance-cache.md` | 第 8 步做性能预算、图片字体、部署缓存时 |
| `references/docs-screenshots.md` | 第 9 步写 README/文档、生成截图索引时 |
| `references/delivery-checklist.md` | 交付前逐项验收时 |
| `assets/product.example.json` | 需要数据样例或字段解释时 |
| `assets/product.schema.json` | 校验数据字段、给外部数据源做映射时 |
| `assets/README-template.md` | 写项目 README 时 |
| `assets/logo-brief-template.md` | 生成 logo 设计说明与提示词时 |
| `assets/ui-decision-template.md` | 写组件调研结论时 |
| `assets/screenshot-plan.md` | 规划截图清单与预览文档时 |
| `assets/tokens.css` | 建立或检查设计 token 时 |

## 完成前检查

- [ ] 产品名短且已由用户确认；`public/logo.svg` 与 `public/logo.png` 存在且语义一致
- [ ] 三页齐全：落地页、数据页、关于页；关于页含作者/产品/免责声明
- [ ] 数据页是单一源；落地页最新区块来自 `highlights.json`，无手写冲突数据
- [ ] `docs/ui-decisions.md` 有至少 3 个可核验来源，选型理由与代价写清
- [ ] zh/en 文案与 hreflang 完整；主题支持系统/亮/暗且无闪烁
- [ ] canonical、sitemap、robots、OG、JSON-LD、`llms.txt` 均存在
- [ ] 首屏 JS、图片尺寸、懒加载、缓存头已检查；构建通过
- [ ] README、`docs/screenshots.md` 与至少 3 张真实截图存在
- [ ] `validate_site.py --strict` 通过；未解决项明确列出

## 后续衔接

- 产品站搭好后，需要首批功能介绍/教程内容，可用 `/lucas-tech-writing` 产出成稿再填入数据页。
- 若用户给了参考站点要统一文风，先用 `/lucas-style-distill` 提炼风格 DNA，再回到本技能落地页面文案。
- 交付后要做索引与 AI 可见性复查，可用 `/ai-seo` 针对线上结果继续优化。
