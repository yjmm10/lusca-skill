# Changelog

## 0.3.0 — 2026-11-20

全链路具体化：每步给出可直接执行/复制的命令、代码、清单与消息模板。

- 新增 `references/deploy-params.md`：按部署目标（Pages / Vercel / Netlify / 云服务器）与依赖服务（数据库 / 对象存储 / 邮件 / OAuth / 支付 / 短信 / AI API）列出参数清单、**控制台获取入口、生成命令（ssh-keygen、certbot）与敏感级别/放置位置**
- 新增 `assets/tokens-starter.css`：可直接复制的完整 tokens 起步文件（色板/语义层/字体/间距/圆角阴影层级/暗色主题/最小重置）
- SKILL.md：第 1 步给出 6 项澄清问题清单；选项呈现格式模板；第 4/6 步接入 deploy-params；完成前检查增加部署参数三项核对
- naming-guide：起名技巧、撞名检查具体指令（gh/npm/pip/搜索）、各生态命名格式表
- dir-structures：通用根文件清单、.gitignore starter、静态站首日可运行 index.html、Vite 脚手架命令与生成后三件事、后端落地命令
- framework-selection：典型场景默认推荐表、每个框架的脚手架命令、路由/状态/UI 库配套建议、版本基线
- design-tokens：指向 tokens-starter.css、Tailwind v3/v4 映射、硬编码审计 grep 命令
- cicd-github-pages：vite.config base 片段、pnpm/yarn 变体、SPA fallback workflow 步骤、部署后 6 步验证、故障速查表、.nojekyll 与自定义域名
- env-management：.env.example 完整示例、zod/pydantic-settings 配置模块模板、GitHub Actions secrets 具体用法
- about-page：简版关于页 HTML/CSS 骨架、参考页提取映射表模板
- logo-guide：3 个完整 SVG 成品示例、favicon 引用代码、选项消息模板
- README/agent-file 模板：徽章与在线地址、技术栈表、提交信息 type 列表与分支命名、好/坏规则写法示例

## 0.2.0 — 2026-11-20

依据外部权威资料修订（anthropics/skills 技能编写规范、agents.md 开放标准、GitHub Pages 官方文档与 starter-workflows、Vite 部署指南、The Twelve-Factor App、MDN CSS 自定义属性、README 写作实践）：

- 新增 `references/naming-guide.md`：命名标准、流程与撞名检查表（支撑第 1 步）
- 新增 `references/design-tokens.md`：tokens 分层（基础色板/语义层）、CSS 变量骨架、暗色主题、命名约定与变更规则（支撑第 5 步）
- `assets/deploy-workflow.yml` 对齐官方：补 `actions/configure-pages@v5`，升级 `deploy-pages@v5`，`cancel-in-progress` 改为官方建议的 `false`，注明 artifact 约束与 Settings→Pages 前置条件
- `references/cicd-github-pages.md` 补官方 action 链路表、artifact 硬性约束（gzip tar、≤10GB、无符号链接、入口在顶层）、子路径 base 的 Vite 具体配置
- `references/env-management.md` 补 12-factor 判据（什么算配置、开源检验法）与机密处理现代补充（env var 泄露路径、secrets 管理）
- `assets/README-template.md` 按 GitHub/Google/18F 实践补：前置要求、开发与测试、参与贡献、获取帮助、目录/截图建议、篇幅控制检查
- `assets/agent-file-template.md` 对齐 AGENTS.md 标准：补测试与提交约定、安全注意节，规则改为具体可验证，标注文件名选择建议与嵌套用法
- SKILL.md：参考索引纳入两个新文件；新增「完成前检查」清单；description 触发词扩充；版本升 0.2.0
- 新增 `evals/evals.json`：3 个测试用例（静态博客、全栈待办应用、起名+骨架）

## 0.1.0 — 2026-11-20

- 初版：七步脚手架流程（需求澄清与命名 → 目录结构 → README/agent 文件/logo → GitHub Pages CI/CD → 前端选型与设计统一 → 后端选型与环境参数管理 → 可选关于页）
- 关键决策点选项化（名称/形态/框架/部署/关于页），执行中问题主动提醒
- references：目录结构模板、技术选型对比、Pages CI/CD 指南、环境参数管理、关于页与参考页适配
- assets：README 模板、agent 文件模板、logo 绘制指南、GitHub Actions 部署模板
