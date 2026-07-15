# Changelog

本文件记录 `lusca` 每次改动的版本号与摘要。
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)：`MAJOR.MINOR.PATCH`

- **MAJOR**：不兼容的流程/护栏删除或重命名
- **MINOR**：新增维度、prompt、reference 或显著能力扩展
- **PATCH**：措辞修正、检查项微调、typo

---

## [1.2.0] — 2026-07-14

### Added
- `references/non-interference.md`：不干扰其他 skill 的正反例（让位 / 事后 / 只读 / 不改写误触发），确保 lusca 不影响其他 skill 的功能发挥。

### Changed
- `SKILL.md` §定位原则 补指向 `references/non-interference.md`；`Reference 文件索引` 增该文件行。

## [1.1.0] — 2026-07-14

### Changed
- 明确 lusca 定位为**可选·事后触发**的附加反省层：不占用其他 skill 功能、不接管任务型输入、与其他 skill 同会话使用时不干扰其执行。
- `SKILL.md` 新增「定位原则」段；`定位与分工` 补"可选附加层"说明；`触发条件` 增"任务型输入不触发"条目；frontmatter `description` 同步标注"可选·事后触发、不占用其他 skill 功能"。

### 来源
- `docs/reflex/reflex_20260714090842_lusca-nonblocking-collection.md`（P1-A 已应用；P1-B 已驳回——不引入任务中 capture 模式，避免干扰其他 skill）

## [1.0.1] — 2026-07-14

### Changed
- 分工表补 `lusca-paper-read`（精读论文）交叉引用，明确体系内"找→读"衔接。

## [1.0.0] — 2026-07-14

### Added
- 初始发布：反省元技能，按会话归档 skill 相关问题与改进建议到仓库根 `docs/reflex/`
- `SKILL.md`：主流程（intake → 关联判定 → analyze → record）、关联判定护栏、不越界护栏、六维分析摘要；遵循工作区方案 A（源在 `skills/lusca/`）
- `references/skill-linkage.md`：问题与 skill 的关联判定三步法（可定位 / 在职责内 / 可归因）及检索 skill（`lusca-paper-search`）正反例
- `references/dimensions.md`：六维分析框架（场景 / 根因 / 影响 / 归属 / 改进 / 验证）
- `references/template-guide.md`：reflex 文档逐节填写规范与质量标准
- `assets/reflex-template.md`：空白归档模板（复制即用）
- `prompts/`：intake、analyze、record

### 遵循规范
- 位置与单一源：`docs/superpowers/specs/2026-07-14-lusca-skill-workspace-design.md`（方案 A）；本阶段不建 eval 框架（规范 §3.5）
