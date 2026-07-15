#!/usr/bin/env bash
# link-project.sh — 重建项目级发现层
#   .claude/skills/<name> → ../../skills/<name>   （相对路径，便于仓库搬家）
# 幂等；支持 --dry-run；实体冲突报错不覆盖。
# 退出码：0 正常；1 存在未处理的实体冲突。
# 设计依据：docs/superpowers/specs/2026-07-14-lusca-skill-workspace-design.md §2
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
DISCOVER_DIR="$REPO_ROOT/.claude/skills"
DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

say() { printf '%s\n' "$*"; }
err() { printf '[ERROR] %s\n' "$*" >&2; }

# 收集有效 skill（skills/*/ 下含 SKILL.md 的目录）
valid=()
shopt -s nullglob
for d in "$SKILLS_DIR"/*/; do
  [[ -f "${d}SKILL.md" ]] && valid+=("$(basename "$d")")
done

mkdir -p "$DISCOVER_DIR"

# 1) 清理悬空链：发现层里指向已不存在源的 symlink
for link in "$DISCOVER_DIR"/*; do
  [[ -L "$link" ]] || continue
  if [[ ! -e "$link" ]]; then
    name="$(basename "$link")"
    if (( DRY_RUN )); then say "[dry-run] prune  .claude/skills/$name（源已不存在）"
    else rm -f "$link"; say "prune  $name（源已不存在）"; fi
  fi
done

# 2) 为每个有效 skill 确保正确 symlink
rc=0
for name in "${valid[@]+"${valid[@]}"}"; do
  target="$DISCOVER_DIR/$name"
  want="../../skills/$name"
  if [[ -L "$target" && "$(readlink "$target")" == "$want" ]]; then
    say "ok     $name"
    continue
  fi
  if [[ -L "$target" ]]; then
    if (( DRY_RUN )); then say "[dry-run] fix    .claude/skills/$name（错误链 → $want）"
    else rm -f "$target"; ln -s "$want" "$target"; say "fix    $name（错误链 → 重建）"; fi
    continue
  fi
  if [[ -e "$target" ]]; then
    err "skip   $name：$target 是实体（非 symlink），不覆盖；请手动处理"
    rc=1
    continue
  fi
  if (( DRY_RUN )); then say "[dry-run] link   .claude/skills/$name → $want"
  else ln -s "$want" "$target"; say "link   $name → $want"; fi
done

shopt -u nullglob
(( rc != 0 )) && err "存在实体冲突未处理。"
exit $rc
