# 目录结构模板

按项目形态选模板并**裁剪**：用不到的目录不建，宁可少而准确。每个目录都要能说出职责，说不出职责的目录不创建。

## 静态站 / 文档站（可直接上 GitHub Pages）

```
<project>/
├── index.html              # 入口页
├── assets/                 # 图片、字体、静态资源
│   └── logo.svg
├── styles/
│   └── tokens.css          # 设计 token 唯一来源（颜色/字体/间距/圆角/阴影）
├── docs/                   # 多页站的其他页面（单页站可省）
├── .github/
│   └── workflows/deploy.yml
├── README.md
├── CLAUDE.md               # agent 约定（或 AGENTS.md）
└── .gitignore
```

## 前端 SPA（Vite 类构建）

```
<project>/
├── public/                 # 原样拷贝的静态资源（favicon 等）
├── src/
│   ├── assets/             # 构建期处理的图片等
│   ├── components/         # 通用组件（跨页面复用）
│   ├── pages/              # 路由页面（Vue 也可叫 views/）
│   ├── router/             # 路由定义
│   ├── stores/             # 状态管理（按需，简单项目可省）
│   ├── api/                # 后端接口封装（无后端可省）
│   ├── styles/
│   │   └── tokens.css      # 设计 token 唯一来源
│   ├── App.vue / App.tsx
│   └── main.ts
├── index.html
├── vite.config.ts
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
│   │   ├── api/            # 路由 / 控制器
│   │   ├── models/         # 数据模型 / ORM
│   │   ├── services/       # 业务逻辑（不含 HTTP 细节）
│   │   ├── core/           # 配置加载、鉴权、依赖注入
│   │   └── tests/
│   ├── .env.example        # 环境参数全集（不含真实密钥）
│   └── requirements.txt / package.json / go.mod
├── docs/
│   └── environment.md      # 环境参数总说明表
├── README.md
└── CLAUDE.md
```

## 纯 API 服务（无前端）

同全栈的 `backend/` 部分，另加：

```
├── docs/
│   ├── environment.md
│   └── api.md              # 接口约定（或指向 OpenAPI 文档）
```

## CLI / 脚本库

```
<project>/
├── src/<pkg>/              # 源码包
├── tests/
├── examples/               # 用法示例
├── pyproject.toml / package.json
├── README.md
└── CLAUDE.md
```

## 落地要点

- 先在回复里给目录树让用户确认，再创建目录（空目录放 `.gitkeep`）
- 模板是起点不是终点：用户需求里明确没有的东西（如无后端）直接裁掉对应分支
- 每个目录的职责一句话写进 README 的「目录结构」节，后续维护者一看就懂
