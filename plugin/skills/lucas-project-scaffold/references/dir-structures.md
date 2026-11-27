# 目录结构模板

按项目形态选模板并**裁剪**：用不到的目录不建，宁可少而准确。每个目录都要能说出职责，说不出职责的目录不创建。

## 通用根文件（所有形态都要）

| 文件 | 内容要求 |
|------|----------|
| `README.md` | 用 `assets/README-template.md`，快速开始的命令必须实测可跑 |
| `CLAUDE.md` 或 `AGENTS.md` | 用 `assets/agent-file-template.md`，二选一保持全仓一致 |
| `.gitignore` | 见下方 starter 内容 |
| `LICENSE` | MIT / Apache-2.0，与 README 的 License 节一致（私有内部项目可省） |
| `CHANGELOG.md` | 从 `## 0.1.0 — <日期>` 起记 |

### .gitignore starter（按语言增删）

```gitignore
# 依赖与构建产物
node_modules/
dist/
build/
out/

# 环境参数（红线：.env 绝不进仓库）
.env
.env.local
.env.*.local

# 日志与系统文件
*.log
.DS_Store
Thumbs.db

# 编辑器
.idea/
.vscode/
```

Python 项目追加：`__pycache__/ *.pyc .venv/ venv/ .pytest_cache/ .mypy_cache/`
Go 项目追加：`*.exe *.test`（`go.sum` 进仓库，不 ignore）

## 静态站 / 文档站（可直接上 GitHub Pages）

```
<project>/
├── index.html              # 入口页
├── 404.html                # SPA fallback 或自定义 404（部署时若用 history 路由必加）
├── assets/                 # 图片、字体、静态资源
│   ├── logo.svg
│   └── favicon.svg
├── styles/
│   ├── tokens.css          # 设计 token 唯一来源（复制 assets/tokens-starter.css 改）
│   └── main.css            # 页面样式，只引用 tokens 变量
├── js/                     # 无构建项目的手写脚本（有构建则见 SPA 模板）
├── docs/                   # 多页站的其他页面（单页站可省）
├── .github/
│   └── workflows/deploy.yml
├── README.md
├── CLAUDE.md               # agent 约定（或 AGENTS.md）
└── .gitignore
```

首日最小可运行 `index.html`：

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title><项目名> — <一句话定位></title>
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg" />
  <link rel="stylesheet" href="styles/tokens.css" />
  <link rel="stylesheet" href="styles/main.css" />
</head>
<body>
  <main class="container">
    <h1><项目名></h1>
    <p><一句话定位></p>
  </main>
</body>
</html>
```

## 前端 SPA（Vite 类构建）

**落地命令（用户确认框架后执行）**：

```bash
# Vue 3 + TS（React 换 --template react-ts，原生换 --template vanilla-ts）
npm create vite@latest <project> -- --template vue-ts
cd <project> && npm install
```

脚手架生成后**必须做的三件事**：删掉默认示例组件与默认样式 → 建 `src/styles/tokens.css`（复制 `assets/tokens-starter.css`）并在 `main.ts` 引入 → 按下表补齐目录。

```
<project>/
├── public/                 # 原样拷贝的静态资源（favicon.svg 等）
├── src/
│   ├── assets/             # 构建期处理的图片等
│   ├── components/         # 通用组件（跨页面复用；单组件单文件）
│   ├── pages/              # 路由页面（Vue 也可叫 views/）
│   ├── router/             # 路由定义（只有一页时可省，用条件渲染）
│   ├── stores/             # 状态管理（Pinia/Zustand；简单项目可省）
│   ├── api/                # 后端接口封装（无后端可省）
│   ├── styles/
│   │   └── tokens.css      # 设计 token 唯一来源
│   ├── App.vue / App.tsx   # 根组件：只做布局与路由出口
│   └── main.ts             # 入口：createApp + tokens + router + pinia
├── index.html
├── vite.config.ts          # 部署到 Pages 时设 base（见 cicd 参考）
├── package.json
├── README.md
└── CLAUDE.md
```

## 全栈分离（frontend/ + backend/）

```
<project>/
├── frontend/               # 上面 SPA 结构整体放入
├── backend/
│   ├── src/                # 或 app/
│   │   ├── api/            # 路由 / 控制器：只做参数校验与调用 services
│   │   ├── models/         # 数据模型 / ORM
│   │   ├── services/       # 业务逻辑（不含 HTTP 细节，可单测）
│   │   ├── core/           # 配置加载、鉴权、依赖注入
│   │   └── tests/          # 与 src 同级或镜像目录
│   ├── .env.example        # 环境参数全集（不含真实密钥）
│   └── requirements.txt / package.json / go.mod
├── docs/
│   └── environment.md      # 环境参数总说明表
├── README.md
└── CLAUDE.md
```

后端落地命令示例：

```bash
# FastAPI
pip install fastapi "uvicorn[standard]" pydantic-settings
# NestJS
npx @nestjs/cli new backend
# Gin
go mod init github.com/<user>/<project> && go get github.com/gin-gonic/gin
```

## 纯 API 服务（无前端）

同全栈的 `backend/` 部分，另加：

```
├── docs/
│   ├── environment.md
│   └── api.md              # 接口约定：方法/路径/入参/出参/错误码（或指向 OpenAPI 文档）
```

## CLI / 脚本库

```
<project>/
├── src/<pkg>/              # 源码包（Python: src/<pkg>/；Node: src/ 或 lib/）
├── tests/                  # 与源码镜像命名：test_<模块>.py / <模块>.test.ts
├── examples/               # 至少 1 个可复制粘贴跑通的用法示例
├── pyproject.toml / package.json
├── README.md
└── CLAUDE.md
```

## 落地要点

- 先在回复里给目录树让用户确认，再创建目录（空目录放 `.gitkeep`）
- 模板是起点不是终点：用户需求里明确没有的东西（如无后端）直接裁掉对应分支
- 每个目录的职责一句话写进 README 的「目录结构」节，后续维护者一看就懂
- 首日目标：**clone 下来 → 装依赖 → 一条命令跑起来看到页面/接口通**，做不到就说明骨架缺文件
