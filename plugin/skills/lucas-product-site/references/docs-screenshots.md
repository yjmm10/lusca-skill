# 文档与截图

## 文档规则

- 带 frontmatter 的模板先保留 frontmatter，再按产品信息补字段。
- 段落和列表项在源码里写一行，不按显示宽度硬折行。
- 文档结尾不写免责式尾巴；事实边界写在正文或关于页的免责声明里。
- 每个“示例”字段都要能一眼看出是示例，README 列出所有需替换项。

## 必须文件

- `README.md`：定位、快速开始、目录、页面、数据流、设计/主题/i18n、SEO/GEO、性能缓存、部署。
- `docs/product-overview.md`：定位、受众、数据来源、部署平台、未确认事项。
- `docs/data-sources.md`：原始来源、字段映射、更新时间、缺失字段、失败回退。
- `docs/ui-decisions.md`：组件候选、来源链接、决策矩阵、最终选择与代价。
- `docs/seo-geo.md`：索引文件、结构化数据、GEO 做法、实测结果。
- `docs/screenshots.md`：真实截图索引。

## 截图计划

至少截三张：中文浅色的落地页、数据页、关于页。推荐再补深色三张和英文落地页；每张图对应一个稳定 URL 与固定主题参数。

命名：`landing-zh-light.png`、`data-zh-light.png`、`about-zh-light.png`、`landing-zh-dark.png` 等。图片放 `docs/images/`，不要引用临时目录或本地绝对路径。

`docs/screenshots.md` 索引格式：

```markdown
# 页面预览

## 落地页（中文 / 浅色）

![落地页](./images/landing-zh-light.png)

要点：一句话主张、产品预览、核心指标与最新动态。

## 数据页（中文 / 浅色）

![数据页](./images/data-zh-light.png)

要点：完整指标、来源、口径与筛选。
```

截图必须来自真实运行的页面；无法启动时只写计划，不放占位图冒充预览。
