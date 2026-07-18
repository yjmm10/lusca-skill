# CLAUDE.md — lusca-skill 多 Skill 工作区

本仓库维护多个 Claude Code（cc）skill。**单一源、禁止拷贝**：所有 skill 源只在仓库根 `skills/<name>/`，发现层（`.claude/skills/`、`~/.claude/skills/`）一律 symlink。

## 所有权

- **可写源**：`skills/<name>/`（`SKILL.md` 必需；`prompts`/`references`/`scripts`/`assets` 可选）
- **只读发现层**：`.claude/skills/<name>` → `../../skills/<name>`；`~/.claude/skills/<name>` → 仓库绝对路径
- ❌ 禁止在 `.claude/skills/` 或 `~/.claude/skills/` 里直接编辑实体内容

## SKILL.md 精简：长内容拆文件（所有 skill 适用）

SKILL.md 是 skill 触发时**必载**的入口，保持骨架精简；较长的模板、要求、清单、范例拆到独立文件，AI 按需 Read，避免每次触发都全量加载。

- **拆去哪**：
  - `references/` — 指导性说明、查表资料（章节惯例、措辞阶梯、词表、API 用法）
  - `assets/` — 模板、范例、范式（笔记模板、润色范式、报告骨架）
  - `prompts/` — 可复用的提示片段
- **SKILL.md 里怎么留**：核心准则 + 主流程 + 一张「Reference 文件索引」表（文件 → **何时 Read**），让 AI 一眼判断当前要不要读某个文件——索引表而非全文
- **何时该拆**：某节展开明显拖重 SKILL.md（十几行以上的并列清单、多套并列范式、独立长模板）就拆；三五条的简短约定就地放，不必拆
- **范式**：见 `skills/lusca-paper-polish/`——主体只讲准则与流程，`references/`（section-conventions / academic-phrasebank / ai-tone-guardrails）与 `assets/paradigms/` 装细节，SKILL.md 末尾索引表逐文件注明何时读

## 改 skill 后怎么生效

| 改动 | 操作 |
|------|------|
| 只改已有 SKILL.md 正文 / prompts / references | 新开一轮 cc 会话再测（改了 description 尤其要新开） |
| 新增 / 重命名 / 删除 skill 目录 | 先跑 `./scripts/link-project.sh`，再新开 cc |
| 希望任意目录开 cc 都能用 | 再跑 `./scripts/link-global.sh` |

link 脚本幂等；实体目录冲突会**报错不覆盖**；`--dry-run` 可预览。

## 新建 skill 清单

1. `skills/<name>/SKILL.md`（frontmatter 至少 `name` + `description`；name 用小写字母/数字/连字符，与目录名一致）
2. `./scripts/link-project.sh`（挂到项目级 `.claude/skills/`）
3. 需要全局：`./scripts/link-global.sh`
4. 新开 cc，用 description 里的触发话术验证一轮

## 文档输出规范（所有 skill 适用）

skill 产出的 markdown 文档（阅读笔记、检索导览、反省记录等落盘文件，以及正文里粘贴的 md 片段）统一遵守：

- **文末出处块**：正文结尾附一行，三要素齐全，取自当前 skill 的 `SKILL.md` frontmatter：
  - **作者** — `author`（项目默认 `lusca`，主页 https://github.com/yjmm10 ）
  - **版本** — `version`
  - **出处（含链接）** — `https://github.com/yjmm10/lusca-skill/tree/main/skills/<name>`
  - 形如：`> 作者：lusca ｜ 版本：lusca-paper-read v1.9.0 ｜ 出处：https://github.com/yjmm10/lusca-skill/tree/main/skills/lusca-paper-read`
- **frontmatter 保留**：处理带 frontmatter 的 md（读入、基于模板生成、引用片段）时**保留其 frontmatter**，不剥离；仅按需在原 frontmatter 上补字段，不重写已有字段。

## 后续衔接提示（所有 skill 适用）

skill 落盘交付时，除路径 + 要点外，**附一句"后续可衔接操作"**：点明本 skill 的产出可喂给体系内哪个 skill、为什么值得接（用 `/skill-name` 形式，让用户一眼知道下一步能做什么）。

论文线的主依赖链：**`lusca-paper-search`（检索）→ `lusca-pdf-parse`（解析）→ `lusca-paper-read`（精读）**；各 skill 的后续衔接**优先指向主链下一环节**，旁支（回溯扩找、复盘等）列其后、不与主链平级。

- **具体、可执行**：写清"用什么产出 → 喂给哪个 skill → 收益"，如「如需精读批判可接着用 `/lusca-paper-read` 基于这份 Markdown 做（比直接读 PDF 更准、图不丢）」
- **按相关性排序，不堆砌**：只列真正顺手的 1–3 条，最常见的放第一
- **与「执行过程精简」不矛盾**：交付是该说话的时候，后续衔接属交付内容；简短一两行，不复述产出、不展开论证
- 各 skill 的具体衔接清单见各自 SKILL.md 的「后续衔接」节

## 执行过程精简（所有 skill 适用）

skill 执行过程**少生成中间信息、省 token**；产出文档本身该详尽处不受此限。

- **工具间直接切换**：上一步结果到下一步工具调用之间**不写分析性过渡**（“接下来我打算……因为……”），直接发起下一个调用
- **只在必要时开口**：仅当需要**用户确认 / 二选一 / 追问输入**时才输出说明文字；落盘交付只给路径 + 一两句要点
- **能简则简**：过程 narration、复述工具结果、自我检查独白一概省略

> 产出要饱满，过程要安静。

## 调试习惯

- 优先在**仓库根**启动 cc，以加载项目级 `.claude/skills/`
- 反省产出归 `./outputs/lusca/`（gitignored，见 `skills/lusca`）
- 工作区设计规范见 `docs/superpowers/specs/`

## 本阶段不做

- Cursor / `.cursor/skills` 挂载（以后加仍以 `skills/` 为唯一源）
- eval / 基准脚本框架（可后补空目录）
