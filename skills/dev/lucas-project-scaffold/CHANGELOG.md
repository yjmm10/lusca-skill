# Changelog

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
