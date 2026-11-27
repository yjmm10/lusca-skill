#!/usr/bin/env bash
# install.sh — lucas-skill 一键安装：从 GitHub 下载 skill（实体拷贝）到 Claude Code 个人技能目录
#
# 用法：
#   curl -fsSL https://raw.githubusercontent.com/yjmm10/lusca-skill/main/scripts/install.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/yjmm10/lusca-skill/main/scripts/install.sh | bash -s -- lucas-paper-read lucas-paper-blog
#   bash install.sh <skill-name>...    # 本地运行
#
# 行为：浅克隆仓库到临时目录 → 把 skills/<category>/<name>/ 实体拷贝到 ~/.claude/skills/<name>/
#   * 不用软链，无需开发者模式 / 管理员权限（Windows 在 Git Bash 里直接跑）
#   * 重复运行 = 更新（整目录替换；已存在的软链会被安全替换为实体拷贝）
#   * 自定义目标：CLAUDE_SKILLS_DIR=/path bash install.sh
set -euo pipefail

REPO="yjmm10/lusca-skill"
BRANCH="main"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

say() { printf '%s\n' "$*"; }
die() { printf '[ERROR] %s\n' "$*" >&2; exit 1; }

command -v git >/dev/null 2>&1 || die "需要 git（Windows 请在 Git Bash / WSL 里运行）"
command -v curl >/dev/null 2>&1 || command -v wget >/dev/null 2>&1 || true

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

say "▸ 克隆 $REPO（浅克隆）..."
git clone --quiet --depth 1 -b "$BRANCH" "https://github.com/$REPO" "$TMP/repo" || die "克隆失败：检查网络或仓库名"

# 收集可用 skill 名（skills/<category>/<name>/ 含 SKILL.md）
AVAILABLE="$(find "$TMP/repo/skills" -type f -name SKILL.md -exec dirname {} \; | while IFS= read -r d; do basename "$d"; done | sort)"
[ -n "$AVAILABLE" ] || die "仓库中未发现任何 SKILL.md"

if (($#)); then
  WANT=("$@")
  for name in "${WANT[@]}"; do
    grep -qx "$name" <<<"$AVAILABLE" || die "未知 skill：$name（可用：$(echo "$AVAILABLE" | tr '\n' ' ')）"
  done
else
  # shellcheck disable=SC2207
  WANT=($(echo "$AVAILABLE"))
fi

mkdir -p "$DEST"
installed=0
for name in "${WANT[@]}"; do
  src="$(find "$TMP/repo/skills" -type f -name SKILL.md -exec dirname {} \; | grep "/$name\$" | head -1)"
  rm -rf "$DEST/$name"
  cp -R "$src" "$DEST/$name"
  say "  install  $name"
  installed=$((installed + 1))
done

say ""
say "✔ 完成：$installed 个 skill → $DEST"
say "  验证：新开 Claude Code 会话，输入 /${WANT[0]} 或用自然语言触发（如「帮我精读这篇论文」）"
say "  更新：重新运行本脚本即可整目录替换"
