#!/usr/bin/env bash
# link-pi.sh — 把仓库 skills/ 注册为 pi 的 skill 源（零维护：新增 skill 自动被发现）
#   写入 $PI_AGENT_DIR/settings.json 的 skills 数组（默认 ~/.pi/agent/settings.json）
#   只改配置，不拷贝、不逐 skill 建链；改写前自动备份 settings.json.bak-<时间戳>
# 幂等；支持 --dry-run；重复执行不会重复添加。
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
AGENT_DIR="${PI_AGENT_DIR:-$HOME/.pi/agent}"
SETTINGS="$AGENT_DIR/settings.json"
DRY_RUN=0
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=1

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "[ERROR] 找不到 $SKILLS_DIR" >&2
  exit 1
fi

# 转成 Windows 绝对路径（Windows 下 pi 运行在原生环境，反斜杠路径最稳）
if command -v cygpath >/dev/null 2>&1; then
  SKILLS_ABS="$(cygpath -w "$SKILLS_DIR")"
else
  SKILLS_ABS="$SKILLS_DIR"
fi

python - "$SETTINGS" "$SKILLS_ABS" "$DRY_RUN" <<'PY'
import json, os, shutil, sys, time

settings_path, skill_src, dry = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
norm = lambda p: os.path.normcase(os.path.abspath(p))

data = {}
if os.path.exists(settings_path):
    with open(settings_path, encoding="utf-8") as f:
        data = json.load(f)

skills = data.get("skills")
if not isinstance(skills, list):
    skills = []
    data["skills"] = skills

# 忽略排除项（-path / !pattern）后再比对，避免把「已排除」误判成「已注册」
registered = [s for s in skills if isinstance(s, str) and not s.startswith(("-", "!", "+"))]
already = any(norm(s) == norm(skill_src) for s in registered)

if already:
    print(f"ok     settings.skills 已包含 {skill_src}")
    sys.exit(0)

if dry:
    print(f"[dry-run] 将在 settings.skills 添加：{skill_src}")
    sys.exit(0)

os.makedirs(os.path.dirname(settings_path) or ".", exist_ok=True)
if os.path.exists(settings_path):
    backup = f"{settings_path}.bak-{time.strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(settings_path, backup)
    print(f"backup {os.path.basename(backup)}")

skills.append(skill_src)
with open(settings_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write("\n")
print(f"add    settings.skills += {skill_src}")
PY
rc=$?

echo ""
echo "settings：$SETTINGS"
echo "pi 会递归扫描该目录下所有含 SKILL.md 的 skill；新增 skill 无需再跑本脚本。"
echo "pi 内执行 /reload 或新开会话后生效；用 /skill:<name> 可直接验证。"
exit $rc
