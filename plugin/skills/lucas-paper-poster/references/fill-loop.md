# Fill 门控（最多 3 轮）

在 `fill_html.py` 写出 `poster.html` 之后：

1. 运行 `scripts/run_slack_gate.py <outdir>/poster.html`（内部调用 paper2poster `check_poster.py slack --strict --with-polish --canvas 60x36in`）。
2. **exit 0**：全部 section `FULL`（fullRatio 0.90–1.00）且无 polish 硬失败 → 进入 `export_pptx.py`。
3. **非 0**：根据报告的 `EDIT TARGETS` / `needPx`，**Edit** `poster.html`（增删 bullet、微调字号/间距、调整 figure `max-height`），再跑 gate。
4. 累计 gate 调用 **≤ 3**。第 3 次仍失败 → **仍导出 pptx**，交付时注明未达 FULL，并附最后一轮 verdict 摘要。

不要重启超过 3 轮的长 staged-fill；不要为凑 FULL 编造数字。
