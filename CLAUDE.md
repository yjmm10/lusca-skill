# CLAUDE.md — lusca-skill 多 Skill 工作区

本仓库维护多个 Claude Code（cc）skill。**单一源、禁止拷贝**：所有 skill 源只在仓库根 `skills/<name>/`，发现层（`.claude/skills/`、`~/.claude/skills/`）一律 symlink。

## 所有权

- **可写源**：`skills/<name>/`（`SKILL.md` 必需；`prompts`/`references`/`scripts`/`assets` 可选）
- **只读发现层**：`.claude/skills/<name>` → `../../skills/<name>`；`~/.claude/skills/<name>` → 仓库绝对路径
- ❌ 禁止在 `.claude/skills/` 或 `~/.claude/skills/` 里直接编辑实体内容

## 改 skill 后怎么生效

| 改动 | 操作 |
|------|------|
| 只改已有 SKILL.md 正文 / prompts / references | 新开一轮 cc 会话再测（改了 description 尤其要新开） |
| 新增 / 重命名 / 删除 skill 目录 | 先跑 `./scripts/link-project.sh`，再新开 cc |
| 希望任意目录开 cc 都能用 | 再跑 `./scripts/link-global.sh` |

link 脚本幂等；实体目录冲突会**报错不覆盖**；`--dry-run` 可预览。

## 新建 skill 清单

1. `skills/<name>/SKILL.md`（frontmatter 至少 `name` + `description`；name 用小写字母/数字/连字符，与目录名一致）
2. `./scripts/link-project.sh`（挂到项目级 `.claude/skills/`）
3. 需要全局：`./scripts/link-global.sh`
4. 新开 cc，用 description 里的触发话术验证一轮

## 调试习惯

- 优先在**仓库根**启动 cc，以加载项目级 `.claude/skills/`
- 反省产出归 `docs/reflex/`（见 `skills/lusca`）
- 工作区设计规范见 `docs/superpowers/specs/`

## 本阶段不做

- Cursor / `.cursor/skills` 挂载（以后加仍以 `skills/` 为唯一源）
- eval / 基准脚本框架（可后补空目录）
