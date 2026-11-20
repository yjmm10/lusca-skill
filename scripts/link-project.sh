#!/usr/bin/env bash
# link-project.sh — 重建项目级发现层
#   .claude/skills/<name> → ../../skills/<category>/<name>   （相对路径，便于仓库搬家）
# 递归扫描 skills/ 下所有含 SKILL.md 的目录（支持 paper/writing/research/meta 分类子目录）。
# 幂等；支持 --dry-run；实体冲突报错不覆盖。
# 退出码：0 正常；1 存在未处理的实体冲突。
# 设计依据：docs/superpowers/specs/2026-07-14-lucas-skill-workspace-design.md §2
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
DISCOVER_DIR="$REPO_ROOT/.claude/skills"
DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

say() { printf '%s\n' "$*"; }
err() { printf '[ERROR] %s\n' "$*" >&2; }

# 收集有效 skill（递归扫描，凡含 SKILL.md 的目录），记为 "name<TAB>相对路径"
valid=()
while IFS= read -r skillmd; do
  dir="$(dirname "$skillmd")"
  valid+=("$(basename "$dir")"$'\t'"${dir#"$REPO_ROOT"/}")
done < <(find "$SKILLS_DIR" -type f -name SKILL.md | sort)

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
for entry in "${valid[@]+"${valid[@]}"}"; do
  name="${entry%%$'\t'*}"
  rel="${entry#*$'\t'}"
  target="$DISCOVER_DIR/$name"
  want="../../$rel"
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
