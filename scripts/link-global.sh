#!/usr/bin/env bash
# link-global.sh — 同步到全局发现层
#   ~/.claude/skills/<name> → <repo>/skills/<name>   （绝对路径）
# 幂等；支持 --dry-run；实体冲突与非本仓库链接报错不覆盖；
# 不删除 ~/.claude/skills 里与本仓库无关的其他 skill。
# 退出码：0 正常；1 存在未处理的冲突。
# 设计依据：docs/superpowers/specs/2026-07-14-lusca-skill-workspace-design.md §2
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
GLOBAL_DIR="${HOME}/.claude/skills"
DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

say() { printf '%s\n' "$*"; }
err() { printf '[ERROR] %s\n' "$*" >&2; }

# 收集有效 skill
valid=()
shopt -s nullglob
for d in "$SKILLS_DIR"/*/; do
  [[ -f "${d}SKILL.md" ]] && valid+=("$(basename "$d")")
done

mkdir -p "$GLOBAL_DIR"

# 仅处理本仓库 valid 的 skill；不触碰与本仓库无关的全局 skill
rc=0
for name in "${valid[@]+"${valid[@]}"}"; do
  target="$GLOBAL_DIR/$name"
  want="$SKILLS_DIR/$name"            # 绝对路径
  if [[ -L "$target" && "$(readlink "$target")" == "$want" ]]; then
    say "ok     $name"
    continue
  fi
  if [[ -L "$target" ]]; then
    cur="$(readlink "$target")"
    if [[ "$cur" == "$REPO_ROOT"/skills/* ]]; then
      # 指向本仓库但路径有误（如仓库搬家后）→ 重建
      if (( DRY_RUN )); then say "[dry-run] fix    $name（本仓库错误链 → $want）"
      else rm -f "$target"; ln -s "$want" "$target"; say "fix    $name（本仓库错误链 → 重建）"; fi
    else
      err "skip   $name：全局已存在指向 $cur 的 symlink，疑似非本仓库；不覆盖"
      rc=1
    fi
    continue
  fi
  if [[ -e "$target" ]]; then
    err "skip   $name：$target 是实体（非 symlink），不覆盖；请手动处理"
    rc=1
    continue
  fi
  if (( DRY_RUN )); then say "[dry-run] link   $name → $want"
  else ln -s "$want" "$target"; say "link   $name → $want"; fi
done

# 指向本仓库但源已删的悬空链 → 仅警告（不自动删，避免误伤用户其他全局 skill）
for link in "$GLOBAL_DIR"/*; do
  [[ -L "$link" ]] || continue
  cur="$(readlink "$link")"
  [[ "$cur" == "$REPO_ROOT"/skills/* ]] || continue
  [[ -e "$link" ]] && continue
  err "warn   $(basename "$link")：指向本仓库的链接已悬空（源被删）；未自动删除，请手动处理"
done

shopt -u nullglob
exit $rc
