# 不干扰其他 Skill — 正反例

lusca 是**可选·事后·不占用·不干扰**的附加反省层（见 `SKILL.md` §定位原则）。本文件用正反例界定"不干扰"的边界，确保 lusca 不会影响其他 skill 的功能发挥。

## 四条不干扰原则

| 原则 | 含义 | 违反后果 |
|------|------|---------|
| 让位 | 收到其他 skill 的任务型输入时不接管，简短说明后让位 | 占用别的 skill 的功能 |
| 事后 | 只在其他任务完成后反省，不在任务进行中插入 | 打断其他 skill 的执行 |
| 只读 | 反省时可 `Read`/`Grep` 其他 skill 源做归因，但绝不 `Edit`/`Write` | 篡改别的 skill 的源/产出 |
| 不改写误触发 | 纯任务型误触发只让位、不建 reflex；用户补充了真实 skill 设计观察时才反省 | 把误触发拔高为反省主题，浪费会话 |

---

## 正反例

### 场景 1 — 用户传入其他 skill 的任务型参数

> `/lusca /lusca-paper-search 免训练的智能文档方法`

- ✅ **让位**：简短回应"我是事后反省技能，不接管检索；请用 `/lusca-paper-search 免训练的智能文档方法`"，然后停止。不跑 intake/六维，不建 reflex。
- ❌ **接管任务**：lusca 自己去构造检索词 / 调检索 API / 返回检索结果——占用了 `lusca-paper-search` 的功能。
- ❌ **改写为 reflex**：把"用户误传检索参数"当成问题跑完整六维、建 reflex 文档——把单纯误触发拔高为反省主题。

### 场景 2 — 任务进行中

> 用户正在跑 `/lusca-paper-search`，中途觉得检索词偏了。

- ✅ **不插入**：lusca 不在检索进行中触发或插入收集；用户继续完成检索，结束后再 `/lusca` 反省"检索词构造偏了"。
- ❌ **任务中插入**：lusca 在检索中途弹出收集问题线索 / 要求用户停下来反省——打断其他 skill 的执行（即已驳回的 P1-B capture 模式）。

### 场景 3 — 反省其他 skill 时接触其源文件

> `/lusca 刚才 lusca-paper-search 的分页解析好像有问题`（检索已完成）

- ✅ **只读归因**：`Read`/`Grep` `skills/lusca-paper-search/scripts/` 找根因，把"改分页解析"写进 reflex 确认区，状态「待确认」。
- ❌ **顺手改源**：直接 `Edit` 检索 skill 的脚本"修一下"——违反不越界护栏，改了别的 skill 的功能产出。
- ❌ **重跑/改写结果**：重新执行检索、或改写检索 skill 的输出——接管检索 skill 的职责。

### 场景 4 — 反省产出后的执行

> reflex 确认区有待确认建议："调整 `lusca-paper-search` 的检索词构造策略"。

- ✅ **建议归建议**：只在 reflex 文档里列建议（待确认），由用户/维护流程在 `skills/lusca-paper-search/` 源执行。
- ❌ **越界执行**：lusca 自己去改 `skills/lusca-paper-search/`——哪怕用户没确认也动手。

### 场景 5 — 与多个 skill 同会话

> 会话先后用了 `lusca-paper-search` → `lusca-paper-read` → 现在想反省整个流程的 skill 问题。

- ✅ **附加反省**：在所有任务完成后被调用，只读各 skill 源做归因，产出一份 reflex；不回溯修改已完成的检索/精读结果。
- ❌ **回溯篡改**：试图修改之前检索或精读的产出 / 要求重做某步——干扰已完成的 skill 工作。

---

## 边界：何时"误触发"可转为 reflex

纯任务型误触发（如场景 1）只让位、不建 reflex。但若用户在误触发后**补充了真实的 skill 设计观察**（如"我希望 lusca 能边做任务边收集"），则不再是"单纯误触发"——这是对 skill 定位的反馈，走关联判定（`references/skill-linkage.md`）后可反省（参见 `./outputs/lusca/reflex_20260714090842_lusca-nonblocking-collection`）。
