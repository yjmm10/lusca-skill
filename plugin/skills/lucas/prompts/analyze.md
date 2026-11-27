# Step 3: Analyze — 六维分析

**Read** `references/dimensions.md` 后执行。

## 前置

已完成 intake 并通过关联判定（`skill-linkage.md`）；仅对**留存的问题**分析。

## 目标

把每个问题拆解到可执行的程度：定位到 skill 的具体组件，给出最小改动建议与验证方式。

## 对每个留存问题执行

依序回答六维（判据与示例见 `references/dimensions.md`）：

| 维度 | 必须给出 |
|------|---------|
| 场景 Scenario | 复现的输入/触发条件；预估频率（偶发/常见/必现） |
| 根因 Root Cause | 归到一层：路由(frontmatter) / 流程(prompts) / 规范(references) / 脚本(scripts) / 边界(护栏) / 协作(跨skill) |
| 影响 Impact | 后果类型（阻塞/降质/误导/体验）+ 范围 |
| 归属 Ownership | 目标 skill + 文件 + 小节（如 `prompts/intake.md §模式判定`） |
| 改进 Fix | 具体改法（补充/修正/重构/新增）；最小改动；不擅自执行 |
| 验证 Verify | 如何确认：手测用例、触发词/路由回归、补 eval（eval 框架待建） |

## 质量门槛（直击要点）

每个问题的六维必须**全部可落地**；任一维度空泛（如根因写"设计不够好"、改进写"优化一下"）→ 重写，或降级为「观察项」不进改进建议。

## 输出

六维表（每问题一份），供 Step 4 填入 reflex 文档。**不**在此步写文件。
