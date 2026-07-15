# Step 4: Record — 写入 reflex 归档

**Read** `references/template-guide.md` 与 `assets/reflex-template.md` 后执行。

## 目标

把 intake + analyze 的结果按模板写入 `./outputs/lusca/`，一个 session 一份文档。

## 步骤

1. **确定文件**：
   - 新 session → 复制 `assets/reflex-template.md` 为 `./outputs/lusca/reflex_{YYYYMMDDHHmmss}_{slug}.md`
   - 同 session 追加 → **编辑**既有 reflex 文档，在问题清单追加、更新汇总与确认区
2. **填充**：按 `template-guide.md` 逐节填写；全部改进建议状态置「待确认」
3. **质量自检**（对照 `template-guide.md` §质量标准）：
   - 每条问题是否都定位到 skill + 组件 + 改法？
   - 是否有与 skill 无关的问题混入？（有则删除）
   - 确认区是否完整列出所有待确认项？
4. **不越界复核**：确认本次仅写入 `./outputs/lusca/**`，**未**触碰 `skills/**`、`docs/**`

## 命名与路径

- 目录：`./outputs/lusca/`（gitignored，与 `lusca-paper-search` 输出同级）
- 文件：`reflex_{YYYYMMDDHHmmss}_{主题slug}.md`
- slug：小写、连字符、取主问题关键词，≤6 词

## 交付

参考 `lusca-paper-search`：落盘 + 内联展示，一次完成。

1. **落盘**：写 reflex 到 `./outputs/lusca/reflex_{ts}_{slug}.md`
2. **内联展示**：把完整 reflex（问题清单 + 汇总 + 确认区）内联返回，不折叠、不截断
3. **声明**：「未改动任何 skill 源；以下建议需您确认后，由对应 skill 维护流程在 `skills/<name>/` 源执行调整。」

## 禁止

- ❌ `Edit`/`Write` 到 `skills/**`
- ❌ 写入 `docs/**`（reflex 不入库；落 `./outputs/lusca/`）
- ❌ 在 reflex 文档里替用户"预设已同意"——状态一律「待确认」
- ❌ 把与 skill 无关的问题写进归档
