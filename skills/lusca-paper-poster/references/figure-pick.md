# 选图（仅笔记 imgs/）

最多 **2** 张：`figures.method`、`figures.result`。路径相对于笔记所在目录（如 `imgs/fig2_architecture.png`）。

1. 列出笔记目录下 `imgs/*` 与正文 `![](imgs/...)` 引用。
2. **method**：文件名含 `arch` / `architecture` / `method` / `pipeline` / `overview`，或笔记 §2.1 所嵌图。
3. **result**：含 `result` / `ablation` / `compare` / `benchmark`，或 §3.1 主结果图。
4. 仍模糊：按正文引用顺序，method 取首张结构图，result 取首张实验图；不够则对应字段 `null`。
5. **禁止** 调用 PDF 抽图或 paper2assets。
