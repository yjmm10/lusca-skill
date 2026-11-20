# 技术选型参考

使用方式：先问清约束（团队熟悉的技术、生态诉求、部署目标、性能要求），再从表里筛出 2-3 个合适方案，**以选项形式给用户**，每个附一句理由与代价。不替用户拍板。

版本基线（写进 README 前置要求与 agent 文件）：Node 20 LTS+、Python 3.11+、pnpm 9+（如用）。

## 典型场景默认推荐（先对号入座，再谈个性化）

| 场景 | 首选 | 备选 | 一句话理由 |
|------|------|------|-----------|
| 个人博客 / 作品集 / 文档站 | Astro | 原生 + Vite | 内容为主，零 JS 默认输出，Pages 完美支持 |
| 中后台管理系统 | Vue 3 + Vite + Element Plus | React + Vite + Ant Design | 表单表格密集，组件库覆盖 90% 需求 |
| C 端互动应用 / H5 | Vue 3 + Vite 或 React + Vite | — | 交互密集，需要组件化与状态管理 |
| 营销官网（重 SEO） | Astro / Next.js 静态导出 | Hugo | SEO 是硬需求，SPA 是下策 |
| 全栈小应用（1-2 人） | Next.js 全栈 或 Vue + FastAPI | — | 同语言/同仓开发，维护面最小 |
| 高并发 API / 网关 | Gin（Go） | FastAPI | 单二进制部署，并发模型简单可靠 |
| AI 应用后端 / 快速原型 | FastAPI（Python） | Express | 生态贴近 AI 库，pydantic 校验省心 |
| 简单工具页 / 落地页 | 原生 + Vite | — | 无框架心智负担，产物最小 |

## 前端

| 方案 | 适合 | 脚手架命令 | 代价 / 注意 |
|------|------|-----------|-------------|
| Vue 3 + Vite | 中后台、交互密集型应用、国内生态友好 | `npm create vite@latest <name> -- --template vue-ts` | 需遵守 tokens 统一约定，避免样式散落 |
| React + Vite | 组件生态最大、团队已有 React 经验 | `npm create vite@latest <name> -- --template react-ts` | JSX 心智负担、依赖选型自由度高需自律 |
| Next.js | 需要 SSR / SEO 的站点 | `npx create-next-app@latest <name> --ts --app` | 部署到 GitHub Pages 只能静态导出（`output: 'export'`），动态能力受限 |
| Astro | 内容型站点、博客、文档站 | `npm create astro@latest <name> -- --template minimal` | 交互组件按岛屿模式按需引入 |
| Svelte / SvelteKit | 追求体积小、语法简洁 | `npx sv create <name>` | 生态相对小、招人面窄 |
| 原生 + Vite（无框架） | 简单展示页、性能敏感小工具 | `npm create vite@latest <name> -- --template vanilla-ts` | 状态与路由需手写，复杂度上来后难维护 |

配套建议：路由用 Vue Router / React Router；状态管理 Pinia（Vue）/ Zustand（React），简单项目宁可用组件内状态也不 early-adopt 全局 store；CSS 用「tokens.css + 组件内 scoped/模块样式」，不默认引入 Tailwind（团队熟 Tailwind 或要快速堆 UI 时可用，但 tokens 必须仍是唯一色值来源，见 design-tokens.md 的映射方案）。

## 后端

| 方案 | 适合 | 最小启动 | 注意 |
|------|------|----------|------|
| FastAPI（Python） | API 服务、AI 应用、快速迭代 | `pip install fastapi "uvicorn[standard]" pydantic-settings` | 异步与依赖注入有学习曲线；配 pydantic-settings 管配置 |
| Express / Fastify（Node） | 轻量 API、与前端同语言 | `npm i express` / `npm i fastify` | 架构约定靠团队自律，建议分层（api/services） |
| NestJS（Node） | 大型 Node 服务、需要强结构 | `npx @nestjs/cli new <name>` | 模块化/装饰器较重，小项目过度设计 |
| Spring Boot（Java） | 企业级、复杂领域模型 | start.spring.io 生成 | 启动慢、内存开销大，小项目不划算 |
| Gin（Go） | 高并发、单二进制部署简单 | `go get github.com/gin-gonic/gin` | 生态库需要自己拼装 |
| Django（Python） | 全功能、自带 admin 与 ORM | `django-admin startproject <name>` | 默认单体，高度定制需要经验 |

配套建议：数据校验 pydantic（FastAPI 自带）/ zod（Node）；ORM 层小项目直接 SQLAlchemy 2.0 / Prisma / GORM；鉴权先用成熟库（如 fastapi-users、Passport.js），不手写密码哈希与会话。

## 决策提醒（主动反馈用）

- 只做一个展示页 → 不必上前端框架，原生 + Vite 足够
- SEO 是硬需求（官网/文档）→ 静态生成优先，SPA 是下策
- 团队只有一种语言的经验 → 优先该语言的主流方案，不追新
- 需要用户登录 / 数据库 / 定时任务 → 必须有后端，GitHub Pages 只能托管前端静态部分
- 前后端都要且团队小 → 优先同语言栈（如 Next.js 全栈 或 Vue + Express），降低维护面
- 用户给了明确偏好 → 尊重偏好，只提醒风险，不强行改推荐
