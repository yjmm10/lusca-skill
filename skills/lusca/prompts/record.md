# Step 4: Record — 写入 reflex 归档

**Read** `references/template-guide.md` 与 `assets/reflex-template.md` 后执行。

## 目标

把 intake + analyze 的结果按模板写入仓库根 `docs/reflex/`，一个 session 一份文档。

## 步骤

1. **确定文件**：
   - 新 session → 复制 `assets/reflex-template.md` 为 `docs/reflex/reflex_{YYYYMMDDHHmmss}_{slug}.md`
   - 同 session 追加 → **编辑**既有 reflex 文档，在问题清单追加、更新汇总与确认区
2. **填充**：按 `template-guide.md` 逐节填写；全部改进建议状态置「待确认」
3. **质量自检**（对照 `template-guide.md` §质量标准）：
   - 每条问题是否都定位到 skill + 组件 + 改法？
   - 是否有与 skill 无关的问题混入？（有则删除）
   - 确认区是否完整列出所有待确认项？
4. **不越界复核**：确认本次仅写入仓库根 `docs/reflex/**`，**未**触碰 `skills/**`

## 命名与路径

- 目录：仓库根 `docs/reflex/`（与 `docs/superpowers/` 平级）
- 文件：`reflex_{YYYYMMDDHHmmss}_{主题slug}.md`
- slug：小写、连字符、取主问题关键词，≤6 词

## 交付

向用户输出：

1. reflex 文档路径
2. **待确认改进建议清单**（表格：ID / skill / 文件 / 建议 / 类型 / 状态=待确认）
3. 声明：「未改动任何 skill 源；以下建议需您确认后，由对应 skill 维护流程在 `skills/<name>/` 执行调整。」

## 禁止

- ❌ `Edit`/`Write` 到 `skills/**`
- ❌ 在 reflex 文档里替用户"预设已同意"——状态一律「待确认」
- ❌ 把与 skill 无关的问题写进归档
