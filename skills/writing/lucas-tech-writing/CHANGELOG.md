# Changelog

## 1.1.0 — 2026-09-14

- **Changed**: 新增「干货密度」与「有拓展」两条核心准则（SKILL.md），反冗余、反课程腔：禁
  教学套话 / 大纲复述 / 空过渡，空评价换具体事实；基础讲清后必给进阶拓展（调优 / 生态 /
  边界 / 组合），不让文章停在入门
- **Changed**: `assets/blog-template.md` 新增 §五「干货密度与拓展」：反冗余清单、干货化改写
  对照、拓展维度清单；骨架表导语压缩（150–250 → 100–180）、新增「进阶与拓展」节（推荐，
  300–600 字）
- **Changed**: `references/research-workflow.md` 检索角度新增「进阶拓展」（best practices /
  advanced tips / tuning / 生态），知识块清单同步新增「进阶与拓展」块——拓展素材在调研期
  就开始收集，不留到写作期硬凑

## 1.0.0 — 2026-09-14

- **Added**: 初版 `lucas-tech-writing`。
  - 多源检索与逐篇消化流程（`references/research-workflow.md`）：多角度检索、来源分级、
    知识地图（覆盖 / 缺口 / 时效 / 代码缺口），核心参考 ≥3 篇硬底线
  - 代码补全与快速上手规范（`references/code-and-quickstart.md`）：缺代码必补、API 查证、
    可运行底线、模块化主题逐模块 quick start
  - 图片工作流（`references/image-workflow.md`）：候选清单 → 脚本下载 → 逐张目检 → 水印分级
    （无水印直接用 + 署名 / 能换就换 / 稀缺必要保留原样 + 显著标注；绝不裁剪涂抹）
  - 反拼凑准则（`references/anti-patchwork.md`）：主题逻辑组织章节、来源差异写作期解决、
    正文零来源噪音、正反例与自检清单
  - 成文骨架（`assets/blog-template.md`）：新手向叙事线、frontmatter、图注与参考来源格式
  - 图片下载脚本（`scripts/fetch_images.py`）：格式嗅探、大小校验、hash 去重、文件名防撞
  - 跨 skill 复用：封面 `lucas-paper-blog/scripts/fetch_cover.py`、自检
    `lucas-paper-read/scripts/check_imgs.py`
