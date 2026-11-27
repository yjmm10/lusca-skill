#!/usr/bin/env python3
"""同步工作区分发产物：扫描 skills/*/*/SKILL.md →
  1) site/data/skills.json（官网数据）
  2) site/assets/（logo 同步拷贝，Pages artifact 不允许 symlink）
  3) plugin/skills/<name>/（Claude Code plugin marketplace 分发拷贝，实体目录）

用法：
    python scripts/build-site-data.py            # 同步全部产物
    python scripts/build-site-data.py --check    # 仅校验 plugin 拷贝是否与 skills/ 单一源一致（CI 门禁）

CI（.github/workflows/deploy.yml）部署前先 --check 再同步；本地改完 skill 后跑一次即可。
"""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
SITE = REPO / "site"
DATA_FILE = SITE / "data" / "skills.json"
PLUGIN_DIR = REPO / "plugin"

try:
    import yaml  # noqa: F401  有 pyyaml 用标准解析
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

# 分类元信息与 README「技能分类总览」保持一致
CATEGORIES = [
    {"id": "paper", "name": "论文科研线", "emoji": "📄", "desc": "检索 → 解析 → 精读 → 润色 → LaTeX → 海报的全流程论文生产力链"},
    {"id": "writing", "name": "写作与发布线", "emoji": "✍️", "desc": "论文博客化、报告博客化、技术教程、风格提炼与投稿合规审查"},
    {"id": "research", "name": "调研线", "emoji": "🔍", "desc": "需求/竞品/论文三线调研、新闻事件多平台深度报告"},
    {"id": "dev", "name": "工程脚手架线", "emoji": "🛠️", "desc": "新项目脚手架、产品官网搭建"},
    {"id": "meta", "name": "元技能", "emoji": "🪞", "desc": "对本工作区的 skill 使用做事后反省与改进建议"},
]

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    if HAVE_YAML:
        data = yaml.safe_load(m.group(1))
        return data if isinstance(data, dict) else {}
    raise SystemExit("缺少 pyyaml：pip install pyyaml 后重跑")


def clean_desc(desc) -> str:
    """frontmatter 的 description 可能是 >- 折叠块，压成单行供卡片展示。"""
    if desc is None:
        return ""
    return re.sub(r"\s+", " ", str(desc)).strip()


def collect() -> dict:
    categories = []
    total = 0
    for meta in CATEGORIES:
        cat_dir = SKILLS_DIR / meta["id"]
        skills = []
        if cat_dir.is_dir():
            for skill_dir in sorted(p for p in cat_dir.iterdir() if p.is_dir()):
                smd = skill_dir / "SKILL.md"
                if not smd.is_file():
                    continue
                fm = parse_frontmatter(smd.read_text(encoding="utf-8"))
                name = str(fm.get("name") or skill_dir.name)
                version = str(fm.get("version") or "").strip() or None
                skills.append({
                    "name": name,
                    "version": version,
                    "description": clean_desc(fm.get("description")),
                    "category": meta["id"],
                    "command": "/" + name,
                })
        total += len(skills)
        categories.append({**meta, "count": len(skills), "skills": skills})
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "stats": {"total": total, "categories": len(categories)},
        "categories": categories,
    }


def sync_logo() -> None:
    """仓库根 assets/ 的 logo 拷贝进 site/assets/（真实文件，非 symlink）。"""
    out = SITE / "assets"
    out.mkdir(parents=True, exist_ok=True)
    for fname in ("logo.svg", "logo-512.png", "logo-32.png"):
        src = REPO / "assets" / fname
        if src.is_file():
            shutil.copyfile(src, out / fname)


def skill_source_dirs():
    """产出 (name, Path)：全部含 SKILL.md 的 skill 目录。"""
    for meta in CATEGORIES:
        cat_dir = SKILLS_DIR / meta["id"]
        if not cat_dir.is_dir():
            continue
        for skill_dir in sorted(p for p in cat_dir.iterdir() if p.is_dir()):
            if (skill_dir / "SKILL.md").is_file():
                yield skill_dir.name, skill_dir


def sync_plugin() -> int:
    """把 skills/ 实体拷贝为 plugin/skills/<name>/（Claude Code plugin marketplace 分发拷贝），并清理残留。"""
    out = PLUGIN_DIR / "skills"
    out.mkdir(parents=True, exist_ok=True)
    valid = set()
    count = 0
    for name, src in skill_source_dirs():
        shutil.copytree(src, out / name, dirs_exist_ok=True)
        valid.add(name)
        count += 1
    for child in list(out.iterdir()):
        if child.name not in valid:
            shutil.rmtree(child) if child.is_dir() else child.unlink()
    return count


def plugin_is_fresh() -> tuple[bool, str]:
    """校验 plugin/skills/ 拷贝与 skills/ 单一源逐文件一致（内容级比较，不依赖 mtime）。"""
    names = {name for name, _ in skill_source_dirs()}
    out = PLUGIN_DIR / "skills"
    if not out.is_dir():
        return False, "plugin/skills/ 不存在，需先同步"
    stale = [n for n in names if not (out / n).is_dir()]
    extra = [p.name for p in out.iterdir() if p.name not in names]
    if stale or extra:
        return False, f"目录不一致（缺：{stale}；多：{extra}）"
    for name, src in skill_source_dirs():
        cmp = filecmp.dircmp(src, out / name)
        _, mismatch, errors = filecmp.cmpfiles(
            src, out / name,
            [f for f in cmp.left_list if (src / f).is_file()],
            shallow=False,
        )
        if mismatch or errors:
            return False, f"{name} 内容不一致（mismatch={mismatch}，errors={errors}）"
        # 递归子目录
        for sub in cmp.subdirs.values():
            if sub.left_only or sub.right_only or sub.funny_files:
                return False, f"{name}/{sub.name} 子目录不一致"
    return True, ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="仅校验生成结果与现有文件一致")
    args = ap.parse_args()

    if not SKILLS_DIR.is_dir():
        print(f"错误：找不到 {SKILLS_DIR}", file=sys.stderr)
        return 1

    data = collect()
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"

    if args.check:
        ok, reason = plugin_is_fresh()
        if ok:
            print("plugin 拷贝与 skills/ 单一源一致")
            return 0
        print(f"plugin 拷贝过期：{reason}", file=sys.stderr)
        print("本地运行 python scripts/build-site-data.py 后提交，再触发部署", file=sys.stderr)
        return 1

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(payload, encoding="utf-8")
    sync_logo()
    n_plugin = sync_plugin()
    print(f"已生成 {DATA_FILE.relative_to(REPO)}（{data['stats']['total']} 个 skill / {data['stats']['categories']} 类）")
    print(f"logo 已同步 → {SITE.relative_to(REPO)}/assets/")
    print(f"plugin 分发拷贝已同步 → plugin/skills/（{n_plugin} 个）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
