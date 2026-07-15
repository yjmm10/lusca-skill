---
name: lusca
description: >-
  反省元技能（可选·事后触发）：在其他任务完成后，对本会话中出现的、与所涉 skill 强相关的问题做多维度分析，输出"问题 + 改进建议"清单，按会话归档到 ./outputs/lusca/，一个 session 一份文档。不占用其他 skill 的功能、不接管任务型输入；只记录与分析，绝不自动改动任何 skill；改进建议需用户确认后由对应维护流程执行。用户提到"反省本 session""复盘刚才 skill 用得不对的地方""记录这次的问题与改法""lusca""reflex"时使用本技能。
version: "1.4.0"
user-invocable: true
argument-hint: "[可选：session 主题 / 涉及的 skill 名 / 问题简述]"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# Lusca — Skill 反省与会话归档

**核心理念：问题是 skill 演化的燃料，但只有被准确归因、记录并确认的问题才有价值。**

本技能是**元技能**：不生产论文/专利/代码，只**复盘本会话中与 skill 相关的问题**，做多维度归因，产出可执行的改进建议并归档。**只读、只建议、不擅改**——所有对 skill 文件的改动必须经用户确认。

**定位原则**：lusca 是**可选**的附加反省层——**事后**触发（在其他任务完成后才反省）、**不占用**其他 skill 的功能、**不接管**任务型输入、与其他 skill 同会话使用时**不干扰**它们的执行。当传入的参数是其他 skill 的任务型输入（如检索主题、待润色文本、待读论文）时，lusca 不接管该任务，简短说明自身作用域后让位给对应 skill（正反例见 `references/non-interference.md`）。**无感执行**：触发后静默完成读取/判定/分析/归档，不在对话中输出中间步骤；仅最终一次交付。

## 定位与分工

| 场景 | 使用技能 |
|------|----------|
| 文献检索 | `lusca-paper-search` |
| 精读一篇论文 / 批判性评估 | `lusca-paper-read` |
| UAV 实验与存档 | `project-uav-skill` |
| 论文润色 | `paper-polish-skill` |
| 专利全流程 | `patent-skills` |
| **复盘本次会话中 skill 暴露的问题、记录改法** | **本技能（lusca）** |
| 真正去改某个 skill 的文件 | 对应 skill 维护流程（经 lusca 确认后） |

lusca 的产出是 `./outputs/lusca/` 下的归档文档；它**不**触碰 `skills/` 下任何 skill 源。lusca 是**可选**附加层：不替代、不抢占上表任何 skill；仅在所有任务完成后按用户要求做一次额外反省，与其他 skill 同会话使用时不干扰它们的执行。

---

## 触发条件

lusca 仅在用户**明确请求反省**时触发，不因随口提及问题而自动打断任务：

- 斜杠指令：`/lusca`、`/反省`
- 明确提及：反省、复盘、反思本会话、记录刚才的问题、lusca、reflex
- 英文：reflect on this session, post-mortem the skill issue, log the skill problem
- 隐式（仅当用户**明确要求记录/沉淀**时）：如"帮我记一下刚才 XX skill 的这个问题"——仅随口抱怨/提及问题、未要求记录时**不触发**

**不触发 / 拒绝记录**（见 §关联判定护栏）：
- 问题与任何 skill 无关（纯业务问题、外部工具故障、用户操作失误）→ 告知超出范围，不归档
- 用户只是抱怨、未提供可分析的问题线索 → 先引导补全，再决定是否反省
- 传入的是其他 skill 的任务型输入（如检索主题、待润色文本、待读论文）而非反省请求 → 简短告知 lusca 是事后反省技能、不接管任务，引导用对应 skill；不把单纯误触发改写为 reflex 主题

---

## 主流程

```
intake → (skill-linkage 判定) → analyze → record → 一次交付
```

**无感执行**：Step 1–5 静默完成——依次 `Read` 各 prompt/reference，做 intake → 关联判定 → 六维分析 → 写入归档。**中间不单独输出** intake 确认、关联判定过程；六维分析直接写进 reflex 文档，随 reflex 内联展示（不作为独立中间产物）。不铺垫"现在执行 X"、不复述正在做什么。

1. **`Read`** `prompts/intake.md` → 界定**会话范围**与**候选问题**；识别涉及的 skill（内部完成，不输出确认）
2. **`Read`** `references/skill-linkage.md` → 对每个候选问题做**关联判定**：剔除与 skill 无关者
3. **`Read`** `prompts/analyze.md` + `references/dimensions.md` → 对留存问题做**六维分析**
4. **`Read`** `prompts/record.md` + `references/template-guide.md` → 按模板填写并写入归档
5. **`Read`** `assets/reflex-template.md` → 复制为本次会话的 reflex 文档
6. **一次交付**：落盘 reflex 到 `./outputs/lusca/` + 完整内联展示 + 声明（见 §交付格式）

---

## 关联判定护栏（核心）

**只有与 skill 强相关的问题才进入 reflex 文档。** 判定三步（详见 `references/skill-linkage.md`）：

1. **可定位**：问题能指到一个具体 skill（如 `lusca-paper-search`、`paper-polish-skill`）
2. **在职责内**：问题落在该 skill 的功能/触发/流程/输出/规范范围内
   - 例：检索 skill（`lusca-paper-search`）的问题必须是关于检索触发、检索词构造、数据源选择、结果解析、检索范围内 skill 内容——**与检索无关的下游需求（如"检索完帮我写周报""结果翻译成日语"）不记**
3. **可归因**：问题能映射到 skill 的某个组件（frontmatter / prompts / references / scripts / 护栏 / 协作）

不满足任一条 → **剔除**，并在对话中告知用户"该问题超出 lusca 记录范围（理由）"。

---

## 不越界护栏（核心）

本工作区采用**单一源**（见 `docs/superpowers/specs/2026-07-14-lusca-skill-workspace-design.md` 方案 A）：skill 源只在 `skills/<name>/`。lusca **严禁**修改任何 skill 源：

- ❌ `Edit`/`Write` 到 `skills/**`（任何 skill 的 SKILL.md、prompts、references、scripts、assets）
- ❌ `Write` 到 `docs/**`（reflex 不入库）
- ✅ `Write`/`Edit` 仅限 `./outputs/lusca/**`（归档文档，gitignored）
- ✅ `Read`/`Grep`/`Glob` 可读 `skills/**` 用于归因分析

改进建议以**「待确认」**状态写入 reflex 文档的确认区；用户确认后，**由用户或对应 skill 维护流程**执行调整（直接编辑 `skills/<name>/` 源、或经 link 脚本同步），lusca 本身不执行。

---

## 输出与存放

- **目录**：`./outputs/lusca/`（gitignored，与 `lusca-paper-search` 输出同级）；用户指定其他路径时从其指定
- **粒度**：一个 session 一份文档；同一 session 内多个问题汇总到同一份
- **命名**：`reflex_{YYYYMMDDHHmmss}_{主题slug}.md`
  - 示例：`reflex_20260714143022_paper-polish-code-abstraction.md`
- **模板**：`assets/reflex-template.md`（复制即用）；逐节填写规范见 `references/template-guide.md`
- 同一 session 追加问题时：**编辑**既有 reflex 文档（不新建），在问题清单区追加并更新汇总

---

## 多维度分析（摘要）

详见 `references/dimensions.md`。

| 维度 | 回答的问题 | 作用 |
|------|-----------|------|
| 场景 Scenario | 什么输入/触发下复现？高频吗？ | 判优先级 |
| 根因 Root Cause | 出在 skill 哪一层（路由/流程/规范/脚本/边界/协作）？ | 定位改动点 |
| 影响 Impact | 对用户任务的后果（阻塞/降质/误导/体验）？ | 判严重度 |
| 归属 Ownership | 改哪个 skill、哪个文件、哪一节？ | 明确责任 |
| 改进 Fix | 具体怎么改（文件+改法+类型）？最小改动 | 可执行 |
| 验证 Verify | 怎么确认改对了（手测/触发词回归/补 eval）？ | 闭环 |

---

## 交付格式

**一次交付、完整内联**——参考 `lusca-paper-search`：静默完成分析后一次输出，不铺垫流程、不单独输出中间产物（intake 确认/关联判定过程不输出）。每次交付：

1. **落盘**：写 reflex 到 `./outputs/lusca/reflex_{ts}_{slug}.md`（gitignored，不入库）
2. **内联展示**：把完整 reflex（问题清单 + 汇总 + 确认区）内联返回，不折叠、不截断——用户无需开文件即可看到反省结果
3. **声明**：未改动任何 skill 源；改进建议需用户确认后由维护流程执行

---

## Reference 文件索引

| 文件 | 何时 Read |
|------|-----------|
| `references/skill-linkage.md` | intake 后，做关联判定时 |
| `references/non-interference.md` | 判断是否干扰其他 skill 时（让位/事后/只读/不改写误触发） |
| `references/dimensions.md` | analyze 时，六维分析判据与示例 |
| `references/template-guide.md` | record 时，reflex 文档逐节填写规范与质量标准 |
| `assets/reflex-template.md` | record 时，复制为本次归档文档 |

---

## Prompt 文件映射

| 步骤 | 文件 | 用途 |
|------|------|------|
| Step 1 | `prompts/intake.md` | 界定会话范围、收集候选问题、识别涉及 skill |
| Step 2 | `references/skill-linkage.md`（规范，非 prompt） | 关联判定，剔除无关问题 |
| Step 3 | `prompts/analyze.md` | 六维分析执行 |
| Step 4 | `prompts/record.md` | 按模板填写并写入 ./outputs/lusca |

---

## 质量底线

- **直击要点**：每个问题必须落到具体 skill + 具体组件 + 具体改法；泛泛而谈的不记录
- **只记有价值的**：能改善 skill 的问题才记；已确认是用户误用而非 skill 缺陷的，标注「非 skill 缺陷」后不进改进建议
- **不夸大**：不把一次性偶发问题拔高为系统性缺陷，除非有复现证据
- **不擅改**：见 §不越界护栏

---

## 版本管理

**当前版本**：见 frontmatter `version` 与 `CHANGELOG.md` 最新条目。

每次修改本 skill **必须**：
1. 递增 `SKILL.md` frontmatter `version`
2. 写入 `CHANGELOG.md`（Added / Changed / Fixed / Removed）
3. 向用户说明版本号与变更要点
4. 本 skill 源目录或 frontmatter 有增删/重命名时，按工作区规范跑 link 脚本同步发现层

版本号规则：MAJOR（流程/护栏 breaking）/ MINOR（新维度、新 prompt、新 reference）/ PATCH（措辞、typo）。
