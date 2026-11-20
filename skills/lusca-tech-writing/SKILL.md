---
name: lusca-tech-writing
description: >-
  输入一个技术主题，检索多篇 Web 技术文档（官方文档/技术博客/教程，核心参考 ≥3 篇）做调研素材，
  把散落各处的碎片知识消化成一篇新手可读、完整自洽、带图带代码的技术博客——读者不需要再点开
  任何源文档。模块化主题给出逐模块快速上手；源文档缺代码时主动查官方文档/GitHub 补齐并查证
  API 真实存在；图片取自源文档，AI 逐张检查水印（无水印直接用+署名，能换就换，稀缺必要的
  保留原样+显著标注，绝不裁剪涂抹）。反拼凑：一条叙事线消化所有来源，来源只出现在文末参考。
  产出干货向：反冗余、反课程腔，每段都要有信息量，基础讲清后必给进阶拓展（调优/生态/边界）。
  用户提到写篇 XX 的博客、调研这个技术写成文章、把零散资料整理成完整教程、XX 入门文章帮我
  写一篇、这个主题写成博文、写篇 XX 的干货文、tech writing、topic to blog、write a
  tutorial/blog about X 时使用本技能。
version: "1.1.0"
author: lusca
user-invocable: true
argument-hint: "[技术主题，可带版本/语言/平台等范围限定]"
allowed-tools: Read, Write, Bash, WebSearch, WebFetch
---

# lusca-tech-writing — 技术主题多文档调研成文

**核心理念：把散落在多篇文档里的碎片知识，消化成一篇新手读得懂、读完能动手、带图带代码的完整博客——读者不需要点开任何一篇源文档。不是把文档拼起来，而是像一位懂行的作者自己研究后独立写出来的。**

输入一个技术主题，检索多篇 Web 技术文档（官方文档 / 权威技术博客 / 教程，**核心参考 ≥3 篇**）作为调研素材。每篇往往只讲清主题的一个碎片：有的讲概念不讲实操、有的有步骤但缺原理、有的代码缺失或版本过时。本技能逐篇消化形成**知识地图**（哪些块已覆盖、哪些是缺口），补齐缺口，再按**主题自身逻辑**重写成一条叙事线的博文。

## 路径约定

- **`${SKILL_DIR}`**：本技能根目录（含本 `SKILL.md` 的文件夹）。经 symlink 发现层加载时即为
  `skills/lusca-tech-writing/`。
- 下文用 `$IMGFETCH` 指代 `${SKILL_DIR}/scripts/fetch_images.py`。**始终用绝对路径调用**。
- 封面图与孤儿图自检**复用兄弟 skill 的脚本**（跨 skill 复用是既有惯例）：
  - 封面：`python3 skills/lusca-paper-blog/scripts/fetch_cover.py <slug> <YYYYMMDDHHmmss> outputs/lusca-tech-writing/<slug>/`（仓库根相对路径；禁止手选）
  - 自检：`python3 skills/lusca-paper-read/scripts/check_imgs.py outputs/lusca-tech-writing/<slug>/`
- 产出默认落盘到 `./outputs/lusca-tech-writing/{slug}/`（用户指定路径时从其指定）。

## 与体系内其它 skill 的分工

| 场景 | 使用技能 |
|------|----------|
| **技术主题 → 多文档调研 → 完整入门博客** | **本技能（lusca-tech-writing）** |
| 单篇论文 → 通俗科普博客 | `lusca-paper-blog` |
| 已有报告 / 事件报告 → 通俗博文 | `lusca-report-blog` |
| 学术文献检索（论文线） | `lusca-paper-search` |
| 新闻 / 热点事件调研报告 | `lusca-news-report` |
| 复盘本会话中 skill 暴露的问题 | `lusca` |

**与 `lusca-paper-blog` 的边界**：同属博客体裁、语气规范一致；输入不同——paper-blog 输入是**单篇论文**（parse 结果 / 精读笔记 / 论文地址），本技能输入是**主题**，需自行多源检索并消化整合。

---

## 触发条件

- 明确提及：写篇 XX 的博客 / 教程 / 入门文章、调研 XX 写成文章、把零散资料整理成完整教程、
  帮我写一篇 XX 怎么上手、这个主题写成博文、整理成一篇完整的
- 英文：tech writing, topic to blog, write a blog/tutorial about X, research and write an article on X
- 斜杠指令：`/lusca-tech-writing`、`/技术写作`
- 给了一个技术主题（框架 / 工具 / 协议 / 概念 / 方向），要的产出是**一篇文章**

**不触发**：
- 单篇论文解读 / 科普（→ `lusca-paper-blog`）
- 已有报告要转博文（→ `lusca-report-blog`）
- 新闻 / 事件来龙去脉（→ `lusca-news-report`）
- 只检索文献不成文（→ `lusca-paper-search`）

---

## 输入（自动推断——绝不追问确认）

从 `$ARGUMENTS` 自动推导，首轮即跑：

- **主题**：一个技术 / 框架 / 工具库 / 协议 / 概念 / 方向。用户给的范围限定（版本、语言、
  平台、场景）原样保留，检索与成文都限定在该范围内
- **深浅**：默认新手向（见核心准则）；用户明确说"进阶""面向资深"时才上调假设的读者水平
- **语言**：默认中文成文；检索中英并用（英文一手资料通常更全）

**唯一允许的停顿**：两轮多角度补搜后核心参考仍 <3 篇 → 停下如实报告（找到哪些、主题是否
太窄 / 太新 / 有歧义），与用户确认后再继续。**绝不硬凑不相关文档充数。**

---

## 主流程

```
parse-topic → search-docs → digest → fill-gaps → outline-and-write → images → save-and-check → deliver
```

1. **解析主题**：从 `$ARGUMENTS` 推断主题与范围限定
2. **多源检索**（→ `references/research-workflow.md`）：WebSearch 多角度（是什么 / 怎么上手 /
   原理 / 对比 / 踩坑 / 进阶调优，中英各查），筛出**核心参考 ≥3 篇**（官方文档优先）
3. **逐篇消化**（→ `references/research-workflow.md`）：逐篇读全文，填知识地图（概念 / 原理 /
   安装 / 最小示例 / 模块用法 / 对比 / 坑 / 进阶拓展 各块覆盖情况）+ 时效标注 + 代码缺口 +
   图片候选清单（知识地图在会话内完成，**不落盘中间文件**）
4. **缺口补查**（→ `references/code-and-quickstart.md`）：知识缺口查官方文档 / GitHub 仓库补齐；
   **缺代码必须补**，补的代码 API 经 fetch 查证真实存在、可运行
5. **大纲与写作**：`Read` `assets/blog-template.md`，按新手向叙事线出大纲再写；反拼凑准则见
   `references/anti-patchwork.md`——一条叙事线消化所有来源，正文无来源痕迹
6. **图片处理**（→ `references/image-workflow.md`）：候选图清单 → `python3 "$IMGFETCH" --manifest ... --output-dir ...`
   下载 → `Read` 逐张查看（内容匹配 + **水印分级**）→ 按叙事需要嵌入；封面跑 fetch_cover.py
7. **落盘自检**：写到 `./outputs/lusca-tech-writing/{slug}/{YYYYMMDDHHmmss}_{slug}.md`；
   跑 check_imgs.py 查孤儿图；frontmatter 自检（`cover` http 开头、`sources` 列全核心参考）
8. **交付**：路径 + 标题 + 一两句要点（消化了几篇、配图几张、水印处理情况）；**不内联重贴
   全文**；附后续衔接（见 §后续衔接）

---

## 核心准则

- **新手可读**：默认读者刚接触这个主题——术语首次出现配白话解释、先 why 后 how、机制配一个
  生活类比、循序渐进不堆术语；读完能建立完整认知并动手跑起来
- **干货密度**：每段都要有信息量——命令、参数、数字、版本、结论；砍掉课程腔（"本节我们将
  学习……"）、客套铺垫与重复解释；空评价换具体事实（"非常快"→"官方基准 X 场景比 Y 快 30%"）
- **有拓展**：基础讲清后必给进阶一层——调优参数、生态工具、组合用法、边界与局限，不让文章
  停在入门；拓展同样要具体可带走，不是罗列关键词（写法见 `assets/blog-template.md` §五）
- **完整自洽**：读者不点开任何源文档也能完整搞懂主题；源文档的缺口（没讲的机制、缺的代码、
  过时的步骤）必须补齐，而不是跟着缺
- **反拼凑**：章节按主题自身逻辑组织，不按来源组织；所有事实消化进统一口径，正文不出现
  "根据官方文档""某博客说"式痕迹；来源只出现在文末参考来源与图注署名
- **模块化主题给快速上手**：主题是多模块框架 / 工具库时，必有「5 分钟跑通最小示例 + 每个核心
  模块一个 quick start（干什么 + 最小代码 + 怎么验证跑通）」
- **代码真实**：可运行、API 查证过、依赖与版本标明；禁止编造 API、禁止伪代码糊弄；验证不了的
  不写
- **水印分级**：无明显水印 → 直接用 + 图注署名；有水印且有替代 → 弃用换图；有水印但稀缺必要
  → 保留原样 + 显著来源标注；**绝不裁剪、涂抹、遮挡水印**；图库大水印一律不用
- **绝不编造**：事实忠于来源，冲突按版本 / 场景澄清，裁不断标 uncertain；错误如实上报
- **体裁规范**：TL;DR、资源块、自问自答、段落 ≤4-5 行、一段一行（不硬换行）——与
  `lusca-paper-blog` 同语气，细节见 `assets/blog-template.md`

---

## 输出与存放

```
outputs/lusca-tech-writing/{slug}/
  ├── {YYYYMMDDHHmmss}_{slug}.md   # 博客文章
  └── imgs/                         # 取自源文档的图 + 封面备份
```

- **slug**：主题 kebab-case（如 `mcp-quickstart`、`vector-db-intro`）
- **frontmatter**：`title` / `topic` / `slug` / `category` / `tags` / `abstract` / `read_minutes` /
  `blog_date` / `cover` / `cover_backup` / `cover_source` / `sources` / `generator` / `generated_at`
  ——完整字段与成文骨架见 `assets/blog-template.md`
- **不带文末出处块**（仓库已废除）；参考来源节属于文章内容，保留

---

## 后续衔接

博客落盘后附一句最相关的下一步：

- **`/lusca`**：复盘本次成文（检索质量、知识地图完整性、反拼凑与新手向是否到位、水印处理）
- **`/lusca-paper-search`**：若主题有学术侧值得深挖（原理 / 论文线），转论文检索继续
- 若这篇博客基于的某个事实需要核对原文，参考来源节已列全部文档 URL，可直接回查

> 话术示例：路径 + 要点后补一句「想复盘这次成文质量可用 `/lusca`；想深挖学术侧可用 `/lusca-paper-search`」。

---

## Reference 文件索引

| 文件 | 何时 Read |
|------|-----------|
| `references/research-workflow.md` | 开始检索前：多角度检索、来源分级、逐篇消化与知识地图填法 |
| `references/code-and-quickstart.md` | 进入写作前：代码缺口补查渠道、API 查证、可运行底线、快速上手模块写法 |
| `references/image-workflow.md` | 处理图片时：候选图清单、下载、逐张查看、水印分级、署名格式 |
| `references/anti-patchwork.md` | 动笔前与通读自检时：叙事线组织、来源消化、冲突澄清的正反例与清单 |
| `assets/blog-template.md` | 大纲与落盘时：标题范式、章节骨架、frontmatter、干货与拓展写法、图注与参考来源格式 |
| `scripts/fetch_images.py` | 下载源文档图片时**必跑**：格式校验、大小校验、hash 去重 |

---

## 版本管理

**当前版本**：见 frontmatter `version` 与 `CHANGELOG.md` 最新条目。

每次修改本技能**必须**：
1. 递增 `SKILL.md` frontmatter `version`
2. 写入 `CHANGELOG.md`（Added / Changed / Fixed / Removed）
3. 向用户说明版本号与变更要点
4. 本 skill 源目录有增删 / 重命名时，跑 `./scripts/link-project.sh` 同步发现层

版本号规则：MAJOR（流程 / 输出规范 breaking）/ MINOR（新 reference、新脚本能力、新准则）/ PATCH（措辞、typo）。
