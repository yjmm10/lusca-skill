---
name: lucas-project-scaffold
description: >-
  从零搭建新项目脚手架：根据需求选合适的项目名、定项目目录结构、写说明文档（README）、
  配置 agent 文件（CLAUDE.md / AGENTS.md）、绘制项目 logo；能用 github.io 部署的项目直接搭好
  GitHub Pages CI/CD；前端项目挑选合适框架并建立统一设计规范（改动需整体评估）；
  后端项目挑选框架，开发中暴露的环境参数用专门文件说明并随改动及时更新，设计不合理处主动反馈；
  前端页面可选配「关于页」（支持用户给参考页面做引用，注意与原有样式适配，也可以不做）。
  关键决策点以提供选项的方式交由用户选择，执行中发现问题随时提醒。
  用户提到新建项目、搭脚手架、项目初始化、init 一个项目、新仓库起步、项目起名、
  目录结构设计、搭 CI/CD、github pages 部署、项目模板、scaffold、bootstrap a project、
  project starter、init project 时使用本技能。
version: "0.1.0"
author: lucas
user-invocable: true
argument-hint: "[可选：项目想法 / 需求描述 / 已定项目名]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, WebSearch, WebFetch
---

# lucas-project-scaffold — 项目脚手架搭建

输入一个项目想法 / 需求 → 七步搭出可直接开发的骨架：命名、目录、文档与 agent 文件、logo、CI/CD、前端与后端选型落地、可选关于页。每步落到文件，关键分叉给选项。

## 核心原则

- **决策点选项化**：项目名、项目形态、前端/后端框架、部署方式、是否做关于页——一律给 2-4 个带理由与代价的选项，由用户选，不替用户拍板
- **主动提醒**：发现需求矛盾、选型坑、部署限制、环境参数遗漏、设计不合理，当场指出，不憋到最后
- **不臆造需求**：信息不足先问清（受众、形态、要不要后端、部署到哪），再动手
- **每步有产出**：每一步结束都落盘文件或给出确认项，不做纯口头规划
- **设计统一**：前端设计 token 集中在单一文件，组件只引用 token 不写死值；任何样式改动做全局影响评估

## 处理流程（七步）

### 第 1 步：需求澄清与项目命名

提炼项目定位、受众、形态（静态站 / 文档站 / 前端 SPA / 全栈 / 纯 API / CLI 工具库）。给 2-3 个候选项目名，每个附理由（含义、长度、仓库/域名可用性、区分度），选项确认。

**产出**：项目名 + 一句话定位 + 形态结论。

### 第 2 步：目录结构

按形态取 `references/dir-structures.md` 模板裁剪，给出目录树并逐目录说明职责；先文档后落地（创建目录与占位文件）。

**产出**：目录规划 + 落地空骨架。

### 第 3 步：说明文档 + agent 文件 + logo

- `README.md`：用 `assets/README-template.md`，写定位、特性、快速开始、目录说明、部署方式
- agent 文件：用 `assets/agent-file-template.md` 生成 `CLAUDE.md`（或 `AGENTS.md`），写清技术栈约定、目录规则、环境参数位置、设计规范入口、变更检查清单
- logo：按 `assets/logo-guide.md` 生成简洁 SVG（2-3 个方向给用户选），落 `assets/logo.svg`，README 顶部引用

**产出**：README.md、CLAUDE.md（或 AGENTS.md）、logo.svg。

### 第 4 步：CI/CD（github.io / GitHub Pages）

静态站、文档站、无后端 SPA（含静态导出）→ 直接搭 GitHub Pages 工作流：复制 `assets/deploy-workflow.yml` 到 `.github/workflows/deploy.yml`，按项目改构建命令与产物目录；排障与子路径 base、SPA 404 等坑见 `references/cicd-github-pages.md`。需要服务端运行时的项目**不硬上 Pages**，给替代方案（Vercel / Netlify / 自托管）并说明代价。

**产出**：.github/workflows/deploy.yml + README 部署说明。

### 第 5 步：前端选型与设计统一

查 `references/framework-selection.md` 前端对比表，结合用户偏好给选项确认。建立统一设计：颜色、字体、间距、圆角、阴影集中到单一 tokens 文件（如 `src/styles/tokens.css`），组件只引用 token；「改 token 即全局生效、改组件先查引用面」写入 agent 文件。

**产出**：框架落地（脚手架命令 / package.json）、tokens 文件、设计约定写入 agent 文件。

### 第 6 步：后端选型与环境参数管理

查 `references/framework-selection.md` 后端对比表给选项确认。环境参数按 `references/env-management.md` 管理：`.env.example`（参数全集 + 注释 + 示例值，不含真实密钥）+ `docs/environment.md`（参数/用途/默认值/示例/敏感级别表）。**代码中新暴露任何环境参数，必须当次同步更新这两处**——该规则写入 agent 文件检查清单。对接口、数据模型、鉴权、部署拓扑给设计意见；发现明文密钥、参数硬编码、缺健康检查、单点依赖等问题主动反馈。

**产出**：后端骨架、.env.example、docs/environment.md、设计备忘。

### 第 7 步：关于页（可选）

询问用户：不做 / 简版自述 / 参考某个页面定制（选项确认）。用户给参考页面（链接或截图）时，按 `references/about-page.md` 提炼其布局骨架与信息层级，**映射到本项目 tokens 与组件风格**，不照抄样式代码与素材，适配性有疑问先确认。

**产出**：about 页面，或明确记录不做。

## 与用户的交互方式

- 关键分叉一律给选项：名称 / 形态 / 框架 / 部署 / 关于页，每项带一句理由与代价
- 每步结束简报：做了什么 + 下一步是什么
- 发现问题立即提醒（需求矛盾、选型风险、部署限制、参数遗漏、设计缺陷），并给修正选项

## Reference 文件索引

| 文件 | 何时 Read |
|------|-----------|
| `references/dir-structures.md` | 第 2 步设计目录结构时，按项目形态取模板 |
| `references/framework-selection.md` | 第 5 / 6 步前端、后端技术选型时查对比表与决策提醒 |
| `references/cicd-github-pages.md` | 第 4 步配置 GitHub Pages 工作流、排查部署问题时 |
| `references/env-management.md` | 第 6 步建环境参数文件、定参数管理规则时 |
| `references/about-page.md` | 第 7 步做关于页、处理参考页引用时 |
| `assets/README-template.md` | 第 3 步写 README 时取骨架 |
| `assets/agent-file-template.md` | 第 3 步写 CLAUDE.md / AGENTS.md 时取骨架 |
| `assets/logo-guide.md` | 第 3 步绘制项目 logo 时 |
| `assets/deploy-workflow.yml` | 第 4 步直接复制改造的 GitHub Actions 模板 |

## 后续衔接

- 需求还没摸透就来到本技能时，可先用 `/lucas-command-query` 做竞品与可行性调研，再回来搭骨架
- 文档站 / 技术博客型项目搭好后，可用 `/lucas-tech-writing` 产出首批内容填充
