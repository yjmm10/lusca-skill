# <项目名> — Agent 指南

> 放仓库根目录。文件名二选一：`AGENTS.md`（跨工具开放标准，Codex / Cursor / Gemini CLI / Aider 等均识别，Claude Code 也读）或 `CLAUDE.md`（Claude Code 专用入口）；团队统一即可，内容通用。
> 只写「约定与红线」：agent 无法从代码里自行推断的规则、命令和禁令。目标 < 200 行；规则要具体可验证：
>
> ❌ 「保持代码整洁」 → ✅ 「缩进用 2 空格；组件 Props 用 interface 显式声明类型」
> ❌ 「注意性能」 → ✅ 「列表渲染必须加 key；单组件超过 300 行需拆分」
> ❌ 「环境参数要规范」 → ✅ 「新增参数当次同步 .env.example 与 docs/environment.md，缺一不许提交」

## 项目定位

<一句话：这是什么、给谁用、当前阶段（MVP / 迭代 / 维护）>

## 技术栈

- 前端：<框架 + 版本 + 关键库（路由/状态/UI 库）>
- 后端：<框架 + 版本 + 数据库>
- 部署：<Pages / Vercel / 服务器>

## 目录约定

| 目录 | 职责 | 改动注意 |
|------|------|----------|
| `src/components/` | 通用组件 | 改动前全局查引用面 |
| `src/pages/` | 路由页面 | 页面级逻辑不下沉到 components |
| `src/styles/tokens.css` | 设计 token 唯一来源 | 改这里 = 全局生效，需整体评估 |
| `backend/src/api/` | 路由/控制器 | 只做参数校验与调用 services |
| `backend/src/services/` | 业务逻辑 | 不含 HTTP 细节 |

## 常用命令

```bash
npm run dev      # 本地开发
npm run build    # 构建
npm run test     # 测试
npm run lint     # 静态检查
```

## 测试与提交约定

- 提交前必须跑通 `npm run test` 与 `npm run lint`，红了不许提交
- 修复 bug 先补一条能复现该 bug 的测试，再修
- 提交信息格式：`<type>(<scope>): <subject>`，type 取：`feat` / `fix` / `docs` / `style`(不影响代码含义的格式) / `refactor` / `perf` / `test` / `chore`
- 示例：`feat(auth): add login rate limit`、`fix(api): handle empty page param`
- 分支命名：功能 `feat/<短名>`，修复 `fix/<短名>`；main 上不直接 push
- 大改动先开 Issue / 和维护者确认，再动手

## 环境参数

- 位置：`.env.example`（全集+示例）与 `docs/environment.md`（说明表）
- **红线：新增 / 改名 / 删除任何环境参数，必须当次同步更新这两处**
- 真实密钥只存部署平台 secrets，绝不进仓库、README、代码常量

## 设计规范

- 颜色、字体、间距、圆角、阴影**只从 `tokens.css` 引用**，组件内禁止写死值（禁止新出现 `#hex`、魔法 px 间距）
- 样式改动先评估全局影响：改 token 影响所有引用组件；改公共组件先查引用面
- 新增页面复用现有组件与 token，不另起炉灶

## 安全注意

- 依赖升级前查已知漏洞（`npm audit` / `pip-audit`）
- 用户输入一律校验后再用；错误信息不暴露内部细节与堆栈
- 日志不打印密码、token、完整身份证/手机号等敏感值

## 变更检查清单

- [ ] 环境参数已同步 `.env.example` 与 `docs/environment.md`
- [ ] 样式改动只通过 tokens，未引入硬编码值
- [ ] 公共组件改动已确认引用面
- [ ] 新增/修改行为有对应测试
- [ ] README / 文档与实际行为一致
- [ ] `build` 与 `test` 通过

<!-- 大型 monorepo：在各子包放嵌套 AGENTS.md，agent 读取离改动文件最近的那个 -->
