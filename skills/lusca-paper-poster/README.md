# lusca-paper-poster

从 `lusca-paper-read` 笔记生成 **60×36 in** 可编辑海报（`poster.pptx`）。

## 依赖

```bash
pip install python-pptx qrcode pillow playwright
# slack / html2pptx 复用已链接的 paper2poster
```

## 示例

```text
> /lusca-paper-poster outputs/lusca-paper-read/ocean-ocr/
```

脚本干跑（已有 `poster_copy.json` 时）：

```bash
OUT=outputs/lusca-paper-poster/ocean-ocr
NOTE=outputs/lusca-paper-read/ocean-ocr
python3 skills/lusca-paper-poster/scripts/validate_copy.py $OUT/poster_copy.json --note-dir $NOTE
python3 skills/lusca-paper-poster/scripts/copy_figures.py --copy $OUT/poster_copy.json --note-dir $NOTE --outdir $OUT
python3 skills/lusca-paper-poster/scripts/make_qr.py --copy $OUT/poster_copy.json --outdir $OUT
python3 skills/lusca-paper-poster/scripts/fill_html.py --copy $OUT/poster_copy.json --outdir $OUT
python3 skills/lusca-paper-poster/scripts/run_slack_gate.py $OUT/poster.html
python3 skills/lusca-paper-poster/scripts/export_pptx.py --html $OUT/poster.html --out $OUT/poster.pptx
```
