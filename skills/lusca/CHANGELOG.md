# Changelog

本文件记录 `lusca` 每次改动的版本号与摘要。
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)：`MAJOR.MINOR.PATCH`

- **MAJOR**：不兼容的流程/护栏删除或重命名
- **MINOR**：新增维度、prompt、reference 或显著能力扩展
- **PATCH**：措辞修正、检查项微调、typo

---

## [1.4.0] — 2026-07-14

### Changed
- **输出位置迁移**：reflex 归档从 `docs/reflex/` 改到 `./outputs/lusca/`（gitignored，与 `lusca-paper-search` 输出同级）；不再写入 `docs/`。
- **完整内联展示**：参考 `lusca-paper-search`，落盘后把完整 reflex（问题清单+汇总+确认区）内联返回，不折叠、不截断；用户无需开文件即可看到反省结果。
- 同步更新 `prompts/record.md`、`references/non-interference.md`、`CLAUDE.md`、`README.md` 路径引用；既有 reflex 文档迁到 `outputs/lusca/`，移除 `docs/reflex/`。

### 来源
- 用户反馈：reflex 输出参考 lusca-paper-search，不要输出到 docs

## [1.3.0] — 2026-07-14

### Changed
- **无感执行**：主流程改为静默处理——intake/关联判定/六维分析/归档全在后台，中间不在对话中输出；仅最终一次交付（路径+建议表+声明）。`prompts/intake.md` 去掉"输出确认/确认后进入下一步"的暂停。
- **触发收窄**：仅在用户**明确请求反省**时触发（斜杠指令/明确关键词/明确要求记录）；随口提及问题、未要求记录时不自动触发，避免打断任务。
- `SKILL.md` 定位原则补"无感执行"；`交付格式` 强调一次交付、简短。

### 来源
- `outputs/lusca/reflex_20260714090842_lusca-nonblocking-collection.md` P2（先响应后处理、不友好）

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
- `outputs/lusca/reflex_20260714090842_lusca-nonblocking-collection.md`（P1-A 已应用；P1-B 已驳回——不引入任务中 capture 模式，避免干扰其他 skill）

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
