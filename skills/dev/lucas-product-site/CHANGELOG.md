# CHANGELOG

## 0.2.0

### Changed
- **反模板化重构**：删除 `scripts/init_project.py`（1505 行模板式初始化器）——站点代码改由 AI 按 `references/architecture-pages.md` 的信息架构、职责边界与差异化理论从零搭建，验收只锁结构契约，不再锁模板实现；新增红线「脚本只做工具不做生成器」「反模板化」。
- **验收改为结构契约**：`validate_site.py` 不再检查模板专属文件名（BaseLayout/ProductPreview 等）与写法字符串，改查不变量——三页双语路由、robots/sitemap/llms（端点或静态均可）、i18n 字典与 tokens（glob 任意路径）、layout SEO 标记（任意 layout 文件）、落地页引用 highlights、关于页含作者与免责；组件调研检查升级为「无待补充占位 + ≥3 可核验来源」。
- **截图流程改「探测→询问→跳过」**：`capture_screenshots.py` 新增 `--check`（exit 0 可用 / 3 未装附安装提示，`--no-install` 探测不隐式下载）；`validate_site.py` 新增 `--skip-screenshots`（用户不装 Playwright 时截图项记 SKIP 不阻塞 --strict），交付说明需标注用户选择。
- **新增审核模式**：对已有站点按本技能验收标准体检（机械审核 + 人工审核），产出符合/缺失/风险报告，缺失项逐项交用户确认（补/跳过/以后再说），修补后复验给出前后对比。

### Fixed
- 版本号与 CHANGELOG 同步（此前 SKILL.md 停在 0.1.0）。

## 0.1.2

- 重构落地页：渐变 Hero（网格背景 + 渐变标题）+ 数据徽章、浏览器窗口式产品预览（内置重绘的仪表盘插画）、带图标与悬停态的指标卡（顶部渐变条 + delta pill）、日期 pill + 标签芯片的动态卡片、图标化能力卡、渐变 CTA 横幅、三栏页脚（含更新日期与 llms.txt 链接）；tokens 新增 --brand-2 辅助色。
- 真实构建验证（Astro 5 + Tailwind 4）发现并修复：en 页面组件导入路径少一级（index/data/about 均受影响）；滚动渐显动画在 IntersectionObserver 外增加 1.2s 兜底显示，避免无滚动场景内容不可见。
- 重设计默认 logo：渐变徽章 + 轨道环 + 星芒 + 节点 + 核心点的分层图标（SVG/渐变内发光），替换单一几何三角形；favicon 同步简化版，OG 图改为徽章 + 内容剪影。
- 修复 OG 圆形徽章对角渐变越界导致的偏色；修复 logo.png 行缓冲少写 alpha 通道的错位。
- `naming-brand.md`/`logo-brief-template.md` 明确「分层图标」要求（主符号 + 至少 2 层辅助元素）；`validate_site.py` 新增 logo 丰富度检查；截图脚本等待时间加长到 1.8s 避免截到动画中间态。

## 0.1.1

- 修复 `init_project.py` README 模板占位符不匹配（`{{KEY}}` → `__KEY__`）并增加未解析占位符警告。
- 脚手架切换到 Tailwind v4 官方路径（`@tailwindcss/vite`），弃用 `@astrojs/tailwind`（官方已标记 deprecated）。
- 主流程调整：先生成骨架（第 4 步）再调研 UI 组件（第 5 步），并限制调研调用次数，避免阻塞骨架产出。
- 版本说明：npm registry 最新 astro 为 7.x（验证于 2026-11），脚手架仍锁定 `^5.0.0`（未经本环境构建验证新版，保守稳定）；生成项目可自行升级。

## 0.1.0

- 初版：Astro + TypeScript + Tailwind 静态产品站技能。
- 建立数据单一源、落地页派生摘要、三页结构、SEO/GEO、i18n/主题、性能缓存、品牌 logo、文档截图与验证脚本。
