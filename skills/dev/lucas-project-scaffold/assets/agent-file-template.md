# <项目名> — Agent 指南（CLAUDE.md / AGENTS.md 通用骨架）

> 放仓库根目录，命名 `CLAUDE.md` 或 `AGENTS.md`（团队二选一保持一致）。这是 agent 与新成员的第一入口：只写「约定与红线」，不写教程。

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

## 环境参数

- 位置：`.env.example`（全集+示例）与 `docs/environment.md`（说明表）
- **红线：新增 / 改名 / 删除任何环境参数，必须当次同步更新这两处**

## 设计规范

- 颜色、字体、间距、圆角、阴影**只从 `tokens.css` 引用**，组件内禁止写死值
- 样式改动先评估全局影响：改 token 影响所有引用组件；改公共组件先查引用面
- 新增页面复用现有组件与 token，不另起炉灶

## 变更检查清单

- [ ] 环境参数已同步 `.env.example` 与 `docs/environment.md`
- [ ] 样式改动只通过 tokens，未引入硬编码值
- [ ] 公共组件改动已确认引用面
- [ ] README / 文档与实际行为一致
- [ ] `build` 与 `test` 通过
