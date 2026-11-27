# CHANGELOG

## 0.1.2

- 重设计默认 logo：渐变徽章 + 轨道环 + 星芒 + 节点 + 核心点的分层图标（SVG/渐变内发光），替换单一几何三角形；favicon 同步简化版，OG 图改为徽章 + 内容剪影。
- 修复 OG 圆形徽章对角渐变越界导致的偏色；修复 logo.png 行缓冲少写 alpha 通道的错位。
- `naming-brand.md`/`logo-brief-template.md` 明确「分层图标」要求（主符号 + 至少 2 层辅助元素）；`validate_site.py` 新增 logo 丰富度检查。

## 0.1.1

- 修复 `init_project.py` README 模板占位符不匹配（`{{KEY}}` → `__KEY__`）并增加未解析占位符警告。
- 脚手架切换到 Tailwind v4 官方路径（`@tailwindcss/vite`），弃用 `@astrojs/tailwind`（官方已标记 deprecated）。
- 主流程调整：先生成骨架（第 4 步）再调研 UI 组件（第 5 步），并限制调研调用次数，避免阻塞骨架产出。
- 版本说明：npm registry 最新 astro 为 7.x（验证于 2026-11），脚手架仍锁定 `^5.0.0`（未经本环境构建验证新版，保守稳定）；生成项目可自行升级。

## 0.1.0

- 初版：Astro + TypeScript + Tailwind 静态产品站技能。
- 建立数据单一源、落地页派生摘要、三页结构、SEO/GEO、i18n/主题、性能缓存、品牌 logo、文档截图与验证脚本。
