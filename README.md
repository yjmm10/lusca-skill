# lusca-skill — Claude Code 多 Skill 工作区

本仓库用**单一源 + symlink 发现层**维护多个 cc skill，保证「改一处，处处最新」。

```
lusca-skill/
├── skills/            # 唯一源：只在这里改 SKILL.md 与资源
│   └── <name>/
├── .claude/skills/    # 项目级发现层（仅 symlink）→ ../../skills/<name>
├── scripts/
│   ├── link-project.sh   # 重建项目级链接
│   └── link-global.sh    # 重建全局 ~/.claude/skills 链接
├── docs/reflex/            # 反省归档（lusca 产出）
└── docs/superpowers/specs/ # 工作区设计规范
```

## 快速开始

```bash
# 1. 挂到本项目（.claude/skills/）
./scripts/link-project.sh

# 2.（可选）挂到全局，使任意目录开 cc 都能用
./scripts/link-global.sh

# 3. 预览将要做的事，不实际执行
./scripts/link-project.sh --dry-run
```

然后在本仓库根目录启动 `cc`，用各 skill description 里的触发话术验证。

## 日常流程

```
编辑 skills/<name>/SKILL.md
        │
目录有增删/重命名？ ──是──→ ./scripts/link-project.sh（全局再 ./scripts/link-global.sh）
        │ 否
        ↓
新开 cc 会话（改了 description 尤其要新开）
        ↓
用触发话术试一轮 → 据行为继续改（回到顶部）
```

## 为什么改完要「新开 cc」

cc 在会话启动时加载 skill 的 description 与路由。会话中途改了源文件，当前会话不会重读；**改了 description 或增删 skill 后，新开一轮 cc** 才能生效。link 脚本只管 symlink，不触发重载。

## 设计依据

`docs/superpowers/specs/2026-07-14-lusca-skill-workspace-design.md`（方案 A）

## 现有 skill

- `skills/lusca` — 反省元技能（会话问题归档到 `docs/reflex/`）

> `patent-skills/`、`ResearchStudio/`、`paper_search/`、`project-uav-skill/` 等是待按方案 A 收拢的旧形态（部分含独立 `.git`）。
