# lusca-skill 多 Skill 工作区设计

日期：2026-07-14  
状态：已批准（方案 A；§1–§3）  
范围：Claude Code 优先；Cursor 后补

## 目标

在仓库根 `/code/project/paper/skills/lusca-skill` 维护**多个 skill**，并保证：

1. 在本仓库内启动 Claude Code（cc）时加载到**项目级**最新 skill  
2. 可选同步到个人全局目录，使任意目录启动 cc 也能用到同一份源  
3. **单一源、禁止拷贝**，避免「改了一处、cc 仍读旧副本」

## 决策摘要

| 项 | 选择 |
|----|------|
| 结构方案 | **A**：`skills/` 为唯一源 + 双层 symlink |
| 可见范围 | 项目级 + 可选全局（个人 `~/.claude/skills`） |
| 编辑器 | 先保证 cc；Cursor 暂不实现 |
| 仓库根 | `lusca-skill` |

---

## §1 目录与所有权

### 目标布局

```
lusca-skill/
├── skills/                      # 唯一源（只在这里编辑 SKILL.md / 资源）
│   └── <skill-name>/
│       ├── SKILL.md             # 必需
│       ├── scripts/             # 可选
│       ├── references/          # 可选
│       └── assets/              # 可选
├── .claude/
│   └── skills/                  # 仅 symlink，不存实体内容
│       └── <skill-name> → ../../skills/<skill-name>
├── scripts/
│   ├── link-project.sh          # 重建 .claude/skills/* → skills/*
│   └── link-global.sh           # 重建 ~/.claude/skills/<name> → 仓库 skills/<name>
├── CLAUDE.md                    # cc 工作约定
├── README.md                    # 人读的安装/调试说明
└── docs/superpowers/specs/      # 本设计文档等
```

### 所有权规则

1. **唯一可写源**：`skills/<name>/`  
2. **只读发现层**：`.claude/skills/` 与 `~/.claude/skills/<name>` 必须是指向源的 symlink  
3. **命名**：`<skill-name>` 只用小写字母、数字、连字符；与 `SKILL.md` frontmatter 的 `name` 一致  
4. **新增 skill**：在 `skills/` 建目录 → 跑 `link-project.sh` → 需要全局时再跑 `link-global.sh`  
5. **本阶段不做**：Cursor 路径、eval 框架（可后补空目录，不实现）

### 现状与迁移备注（落盘时仓库快照）

当前 `lusca-skill` 下已存在（尚未按目标布局收拢）：

- `patent-skills/`：根目录含 `SKILL.md`（且含独立 `.git`）  
- `ResearchStudio/`：上游仓库形态，内含多套 `.../skills/`（且含独立 `.git`）

**约定**：实现阶段将可调试的 skill **迁入或链接进** `skills/<name>/`，再由 `link-*.sh` 挂到 `.claude/skills` / 全局；嵌套 `.git` 子仓是否保留为 submodule、或改为普通目录，实施前再定（本设计不锁定）。

---

## §2 `link-project.sh` / `link-global.sh` 行为

两脚本均**幂等**；默认直接执行；支持 `--dry-run` 只打印将要做的事。

### 共同约定

- 扫描 `skills/*/`，只处理内含 `SKILL.md` 的目录  
- 目标已是**正确指向源的 symlink** → 跳过  
- 目标是**错误 symlink** → 删链并重建  
- 目标是**实体目录/文件** → **报错并跳过该 skill**（绝不覆盖），退出码非 0  
- 源被删但链接仍在：  
  - `link-project.sh`：删除悬空的 `.claude/skills/<name>`  
  - `link-global.sh`：仅警告（避免误删用户其他全局 skill）

### `scripts/link-project.sh`

- 作用域：仓库内 `.claude/skills/`  
- 动作：为每个有效 `skills/<name>` 确保  
  `.claude/skills/<name>` → `../../skills/<name>`（**相对路径**链接，便于仓库搬家）  
- 清理「源已不存在」的悬空链  

### `scripts/link-global.sh`

- 作用域：`~/.claude/skills/`  
- 动作：为每个有效 `skills/<name>` 确保  
  `~/.claude/skills/<name>` → `<repo 绝对路径>/skills/<name>`  
- 使用**绝对路径**，避免从家目录解析相对路径出错  
- **不**删除 `~/.claude/skills` 里与本仓库无关的其他 skill  

### 日常命令

| 场景 | 命令 |
|------|------|
| 新增/重命名 skill 后（本仓库调试） | `./scripts/link-project.sh` |
| 希望任意目录开 cc 都能用 | `./scripts/link-global.sh` |
| 只改了已有 `SKILL.md` 正文 | 无需重链；**新开 cc 会话**更稳妥（尤其改了 description） |

---

## §3 `CLAUDE.md` 约定与日常调试流程

### `CLAUDE.md` 必写要点

1. 本仓库是多 skill 工作区；源目录是 `skills/<name>/`；禁止在 `.claude/skills/` 或 `~/.claude/skills/` 里直接改内容。  
2. 改 skill 后：若增删/重命名目录，先跑 `scripts/link-project.sh`（需要全局再用 `link-global.sh`）；若只改已有文件，新开一轮 cc 会话再测触发。  
3. 调试时优先在本仓库根目录启动 cc，以便加载项目级 `.claude/skills/`。  
4. 新建 skill 清单：`skills/<name>/SKILL.md`（frontmatter：`name` + `description`）→ `link-project.sh` →（可选）`link-global.sh` → 新开 cc → 用触发话术验证。  
5. Cursor 暂不要求；以后加挂载时仍以 `skills/` 为唯一源。

### 日常调试流程

```
编辑 skills/foo/SKILL.md
        ↓
目录有增删/重命名？ ──是──→ ./scripts/link-project.sh
        │                      （全局需要再 ./scripts/link-global.sh）
        否
        ↓
新开 cc（本仓库根）
        ↓
用 description 里的触发场景试一轮
        ↓
根据行为继续改 skills/foo/（回到顶部）
```

### `README.md`（给人）

- 说明源在 `skills/`、链接脚本用法、为何建议新开 cc 会话  
- 与上图一致的文字版流程即可  

### 本阶段明确不做

- eval / 基准脚本、示例 fixture  
- 自动 git hook 链（手跑脚本）  
- Cursor / `.cursor/skills`  

---

## 「每次 cc 都用最新」保证机制

| 规则 | 做法 |
|------|------|
| 单一源 | 只改仓库 `skills/`；禁止手改发现层实体内容 |
| 禁止拷贝 | 项目级与全局一律 **symlink** |
| 新会话 | 改 description / 增删 skill 后新开 `cc` |
| 一键修复 | `link-*.sh` 幂等；实体目录冲突则报警不覆盖 |

---

## 实现就绪条件（后续 plan / execute）

在实现前，建议确认：

1. 现有 `patent-skills`、`ResearchStudio` 内 skill 迁入 `skills/<name>/` 的命名与 submodule 策略  
2. 是否在仓库根初始化独立 git（当前主要是子目录自带 `.git`）  

实现产物清单（不含本设计已否定项）：

1. `skills/` 目录约定 + 至少一个迁入或占位 skill（若实施时需要）  
2. `scripts/link-project.sh`、`scripts/link-global.sh`  
3. `CLAUDE.md`、`README.md`  
4. 运行脚本一次，确认 `.claude/skills` 链接正确  

---

## 审批记录

- 方案 A：用户确认  
- §1 目录与所有权：同意  
- §2 链接脚本行为：同意  
- §3 CLAUDE.md 与调试流程：同意  
- 用户请求：对以上内容落盘（本文件）
