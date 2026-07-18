#!/usr/bin/env python3
"""图片完整性校验：检查阅读笔记目录里 imgs/ 的图是否都被正文引用。

用法:
    python3 scripts/check_imgs.py <note_dir>

<note_dir> 形如 outputs/lusca-paper-read/{slug}/，内含笔记 *.md 与 imgs/ 子目录。

退出码:
    0 — imgs/ 所有图都在笔记正文中被引用（无孤儿）；或本篇未用本地图
    1 — 存在"孤儿图"（已下载到 imgs/ 但正文未引用，需补嵌或说明后弃用）
    2 — 目录/用法异常（无笔记、目录不存在等）

背景：lusca-paper-read 要求原文图转存到 {slug}/imgs/ 并用 ![](imgs/..) 嵌入正文。
模型常"下载了却漏嵌"（尤其子结构图/示例图/消融图），本脚本在落盘后做硬校验，
把"图要嵌"从定性要求变成可执行的差集检查。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"}


def find_note(notedir: Path) -> Path | None:
    notes = [p for p in notedir.glob("*.md") if not p.name.startswith("reading-note-template")]
    return notes[0] if notes else None


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("用法: python3 scripts/check_imgs.py <note_dir>", file=sys.stderr)
        return 2
    notedir = Path(argv[1])
    if not notedir.is_dir():
        print(f"错误：目录不存在：{notedir}", file=sys.stderr)
        return 2

    note = find_note(notedir)
    if note is None:
        print(f"错误：{notedir} 下未找到笔记 *.md", file=sys.stderr)
        return 2

    imgsdir = notedir / "imgs"
    if not imgsdir.is_dir():
        print(f"提示：{notedir} 无 imgs/（本篇未用本地图，如全用在线 URL），跳过校验")
        return 0

    imgs = sorted(p for p in imgsdir.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXTS)
    if not imgs:
        print("提示：imgs/ 为空，跳过校验")
        return 0

    text = note.read_text(encoding="utf-8", errors="replace")
    # 兼容 ![](imgs/x.jpg) 与 <img src="imgs/x.jpg">；只要正文出现 imgs/<name> 即算引用
    referenced = set(re.findall(r"imgs/([^\s)\"'\]]+)", text))

    orphans = [p for p in imgs if p.name not in referenced]

    print(f"笔记：{note.name}")
    print(f"imgs/ 图片：{len(imgs)} 张；正文引用：{len(imgs) - len(orphans)} 张")
    if not orphans:
        print("✓ 无孤儿图，所有下载的图都被正文引用")
        return 0

    print(f"✗ {len(orphans)} 张孤儿图（已下载但正文未引用，需补嵌到对应节或说明弃用理由）：", file=sys.stderr)
    for p in orphans:
        print(f"    - imgs/{p.name}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
