# Changelog — lusca-paper-polish

所有 notable 变更记于此。版本号规则：MAJOR（流程/输出规范 breaking）/ MINOR（新 reference、
新指导）/ PATCH（措辞、typo）。

## [1.5.0] — 2026-07-17

### Changed
- `assets/polish-paradigms.md` 从"仅摘要详写 + 其它节占位"**扩充为五节完整范式库**（来源：用户提供综述类五节写作范式 + 文献实例）：
  - 引言 / 相关工作 / 方法-框架 / 实验-评估 / 结论 五节，每节统一按"**元骨架 + 研究型变体 + 综述型变体 + 表达参考 + 自检**"组织；用户给的综述侧范式与实例（贡献声明、C1-Ck 对比矩阵、框架分层、场景汇总表、前瞻指引等）归入综述变体，并**补全研究型变体**（用户未给、但 SATCPP-UAR 等研究型论文所需）。
  - 每节补**常见毛病**（如引言现状≠缺口重复、相关工作树稻草人、方法只列参数清单、实验报喜不报忧、结论引入新内容）与**公允/去 AI 腔护栏**。
  - 摘要节沿用 v1.4.0；边界重申强化"模板借鉴非套用、论文类型不可混用"。
- SKILL.md Reference 索引 paradigms 描述更新（列全五节 + 研究型/综述型两变体）。

## [1.4.0] — 2026-07-17

### Changed
- `assets/polish-paradigms.md` 摘要范式**提炼升华为"元骨架 + 两类变体"**（来源：用户提供 IEEE 综述摘要范式）：
  - 抽出共通元骨架"定位 → 主体 → 发现 → 指向"，区分**研究型**（problem / setup / method / results，凸创新 + 实验）与**综述型**（定位 / 内容覆盖 / 发现空白 / 未来建议，凸广度 + 空白 + 方向）两种变体，表格对照；点明"用错变体"是常见硬伤。
  - 新增**表达参考库**（定位 / 内容 / 发现 / 建议的常用句式与高频词），标注"借鉴非套用——空套即 AI 腔"，与 `ai-tone-guardrails.md` 协同。
  - 自检清单加"是否按论文类型选对范式""综述覆盖是否体现广度、空白与建议是否具体"。

## [1.3.0] — 2026-07-17

### Added
- `assets/polish-paradigms.md`：**润色范式与深度指南（编写参考模板）**——给出摘要四要素骨架
  （现有问题 → 环境建模 → 方法 → 实验结论）与各节"凸什么 / 收什么"的深度取向（饱满充实、
  突出新颖算法与显著效果、用领域专有名词提升专业度、摘要聚焦亮点不展开 limitations）；
  明确"突出亮点 / 避免短板"**不凌驾于 faithfulness / 校准之上**——不注水、不隐瞒关键事实；
  附摘要润色自检清单与其它节占位骨架。**置于 assets/ 作编写参考模板**（非 references 方法论）。
  来源：用户反馈——需要模板库指导润色方向与深度。
- SKILL.md「分节惯例」补引用 paradigms（含诚信边界提醒）；Reference 索引新增 assets 条目。

## [1.2.0] — 2026-07-17

### Changed
- **落盘策略细化**（来源：用户反馈）：
  - **一篇论文一个润色文件、累积续写**——落盘到 `./outputs/lusca-paper-polish/{paper-slug}.md`
    （slug 取自论文、不带时间戳），同篇多次润色（先摘要、后引言…）追加到同一文件，**除非用户
    明确要求新开文件**；取代原先每次 `{YYYYMMDDHHmmss}_{slug}.md` 新建。
  - 落盘文档**保留原稿章节标题结构**（`## 摘要` 等，不自造"（润色后）"标题），每节按
    【原文】↔【润色后】对比 + 改动说明 + 待确认 before/after 组织——让作者不翻原文件即可对照。
  - 同步更新「处理文件 vs 粘贴文本」「输出与存放」「重要约定」；frontmatter 增 `polished_sections`
    / `created_at` / `last_updated`。

## [1.1.0] — 2026-07-17

### Changed
- **产出落盘规范修正**：润色稿一律 `Write` 到 `./outputs/lusca-paper-polish/{YYYYMMDDHHmmss}_{slug}.md`，
  **不就地改作者原稿**（原稿保持作者版本、polish 产出独立留存）；同步修订「处理文件 vs 粘贴文本」
  「输出与存放」「重要约定」「后续衔接」话术示例。来源：用户反馈——polish 产出应在
  `outputs/lusca-paper-polish/`，不应就地改原文件。

### Added
- 落盘文档结构约定：元信息 frontmatter（`source` / `source_version` / `scope` /
  `output_language` / `polished_at` / `generator`）+ 润色正文 + 改动说明 + 待确认 before/after
  + 文末出处块；整篇润色保留原 frontmatter、单节润色用 polish 元信息 frontmatter。

## [1.0.0] — 2026-07-17

首次纳入 lusca-skill 工作区并按统一规范整理。

### Changed
- **frontmatter 规范化**：`name` 由 `paper-polish` 改为 `lusca-paper-polish`（与目录一致）；
  补全 `version` / `author` / `user-invocable` / `argument-hint` / `allowed-tools`；
  `description` 改为中文并附触发话术；保留 `license`。
- **正文全面中文化**，重组为与 `lusca-paper-read` / `lusca-paper-search` 一致的节结构
  （分工表、触发条件、输入、主流程、核心准则、分节惯例、输出与存放、后续衔接、重要约定、
  质量底线、Reference 索引、版本管理）。
- **保留全部方法论内核**：忠实于本意、绝不臆造、默认保守、分节惯例、措辞校准、公允对待
  prior work、去 AI 腔、中译英改写、文件 vs 粘贴、长文、不可读内容、交付、问题更深、输出语言。

### Removed
- 删除对**本体系不存在的外部 skill** 的引用（`paper-writer` / `intro-drafter` /
  `tech-paper-template` / `pre-submission-reviewer` / `idea-evaluator`），改为诚实说明边界
  + 体系内现有 skill 的衔接。

### Added
- **输出与存放规范**：就地改文件优先、frontmatter 保留、出处块仅加在 polish 自身产出文档
  （严禁污染作者稿件）、交付不内联重复。
- **后续衔接**节：指向 `/lusca`（复盘润色）与 `/lusca-paper-search`（查证缺失引用）。
- **重要约定 / 质量底线 / 版本管理**节，对齐工作区其它 skill。
