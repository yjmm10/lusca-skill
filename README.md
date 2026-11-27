# lucas-skill — Claude Code 多 Skill 工作区

<div align="center">
  <img src="assets/logo.svg" width="120" alt="lucas-skill logo：中心实心块为 skills/ 唯一源，四条链路连接空心块为 symlink 发现层" />
  <p><a href="https://yjmm10.github.io/lusca-skill/">在线站点</a> · <a href="https://github.com/yjmm10/lusca-skill">GitHub</a></p>
</div>

本仓库用**单一源 + symlink 发现层**维护多个 cc skill，保证「改一处，处处最新」。skill 按类型分五类目录管理。

```
lucas-skill/
├── skills/            # 唯一源：只在这里改 SKILL.md 与资源（按类别分目录）
│   ├── paper/         # 论文科研线
│   ├── writing/       # 写作与发布线
│   ├── research/      # 调研线
│   ├── dev/           # 工程脚手架线
│   └── meta/          # 元技能
├── .claude/skills/    # 项目级发现层（仅 symlink）→ ../../skills/<category>/<name>
├── scripts/
│   ├── link-project.sh   # 重建项目级链接（递归扫描 skills/）
│   ├── link-global.sh    # 重建全局 ~/.claude/skills 链接
│   ├── link-pi.sh        # 注册到 pi（递归自动发现，新增 skill 免维护）
│   └── build-site-data.py # 生成官网数据 site/data/skills.json + 同步 logo
├── site/              # 官网（纯静态：落地页 / Skills / 关于三标签，GitHub Pages 自动部署）
├── assets/            # 品牌：logo.svg / logo-*.png（站点由构建脚本同步拷贝）
├── outputs/           # 各 skill 产出（gitignored：lucas reflex / 检索报告）
└── docs/superpowers/specs/ # 工作区设计规范
```

## 安装与使用

按场景四选一（详见[官网首页](https://yjmm10.github.io/lusca-skill/)）：

```bash
# ① 推荐一键安装（cc，实体拷贝，重跑即更新）
curl -fsSL https://raw.githubusercontent.com/yjmm10/lusca-skill/main/scripts/install.sh | bash
```

```text
# ② Plugin marketplace（cc 官方渠道，指令带前缀 /lucas-skills:<skill-name>）
/plugin marketplace add yjmm10/lusca-skill
/plugin install lucas-skills@lucas-skill
```

```bash
# ③ pi（一条命令；启动时自动对齐远端 main，更新无感）
pi install git:github.com/yjmm10/lusca-skill
#   本地开发试用：pi -e /path/to/lusca-skill
#   已用 link-pi.sh 注册过的机器不要再装，同名 skill 会双重加载
```

```bash
# ④ 维护者：克隆 + 软链（单一源开发，Windows 需开发者模式或 WSL）
git clone https://github.com/yjmm10/lusca-skill && cd lusca-skill
./scripts/link-project.sh   # 或 link-global.sh 全局可用
```

改 skill 后同步分发产物：`python scripts/build-site-data.py`（刷新官网数据 + `plugin/` 分发拷贝；CI 部署前校验 plugin 拷贝过期即失败）。

## 官网（GitHub Pages）

- **访问地址**：<https://yjmm10.github.io/lusca-skill/>，三个固定标签：落地页 / Skills / 关于（hash 切换，刷新不 404）
- **技术形态**：纯静态免构建（原生 HTML/CSS/JS + tokens 设计令牌，无 node 依赖）；CI 在部署前自动重跑 `scripts/build-site-data.py`，站点数据永远与 `skills/` 单一源同步
- **本地预览**：`python scripts/build-site-data.py && python -m http.server -d site 8080` → 打开 `http://localhost:8080`
- **部署触发**：push 到 `main` 即自动部署（`.github/workflows/deploy.yml`）；首次需在仓库 Settings → Pages 把 Source 设为 GitHub Actions

## 技能分类总览

### 📄 paper — 论文科研线

主依赖链：**`lucas-paper-search`（检索）→ `lucas-pdf-parse`（解析）→ `lucas-paper-read`（精读）**

| Skill | 用途 |
|-------|------|
| `lucas-paper-search` | 多源并行文献检索（arXiv / DBLP / OpenAlex / OpenReview / Semantic Scholar / Crossref / DeepXiv / Sciverse + 模型知识） |
| `lucas-pdf-parse` | PDF / 图片 / DOCX 版面还原为结构化 Markdown（MinerU API，图片自动抽取，支持本地与 URL） |
| `lucas-paper-read` | 论文精读与批判性评估（六维精读 + 五视角批判，落盘阅读笔记） |
| `lucas-paper-polish` | 润色学术初稿：语法流畅度、措辞校准、去 AI 腔、中译英改写 |
| `lucas-paper-latex` | 润色稿转可编译 LaTeX（中译英 + 排版，保护公式/引用/宏） |
| `lucas-paper-poster` | 基于精读笔记生成会议尺寸可编辑海报（60×36in，导出 pptx） |

### ✍️ writing — 写作与发布线

| Skill | 用途 |
|-------|------|
| `lucas-paper-blog` | 论文 → 面向开发者的通俗科普博客 |
| `lucas-report-blog` | 报告（事件/调研/行业分析）→ 通俗博文 |
| `lucas-tech-writing` | 技术主题 → 新手可读、带图带代码的完整技术博客 |
| `lucas-style-distill` | 提取写作风格 DNA（六维风格画像，供 agent 复用） |
| `lucas-kunpeng-publish` | 鲲鹏社区发布合规审计与改进（真实化而非伪装） |

### 🔍 research — 调研线

| Skill | 用途 |
|-------|------|
| `lucas-news-report` | 新闻/热点事件多平台深度调研，产出带时间线的完整报告 |
| `lucas-command-query` | 需求/想法立项前调研：竞品、开源、论文 + 可行性方案 |

### 🛠️ dev — 工程脚手架线

| Skill | 用途 |
|-------|------|
| `lucas-project-scaffold` | 新项目脚手架：命名、目录结构、README/agent 文件/logo、GitHub Pages CI/CD、前后端选型、环境参数管理、可选关于页 |

### 🧠 meta — 元技能

| Skill | 用途 |
|-------|------|
| `lucas` | 反省元技能：会话问题多维分析，按 session 归档到 `./outputs/lucas/` |

## 快速开始

```bash
# 1. 挂到本项目（.claude/skills/）
./scripts/link-project.sh

# 2.（可选）挂到全局，使任意目录开 cc 都能用
./scripts/link-global.sh

# 3.（可选）注册到 pi（之后新增 skill 自动发现）
./scripts/link-pi.sh

# 4. 预览将要做的事，不实际执行
./scripts/link-project.sh --dry-run
```

然后在本仓库根目录启动 `cc`，用各 skill description 里的触发话术验证。

## 日常流程

```
编辑 skills/<category>/<name>/SKILL.md
        │
目录有增删/重命名？ ──是──→ ./scripts/link-project.sh（全局再 ./scripts/link-global.sh）
        │ 否
        ↓
新开 cc 会话（改了 description 尤其要新开）
        ↓
用触发话术试一轮 → 据行为继续改（回到顶部）
```

## 为什么改完要「新开 cc」

cc 在会话启动时加载 skill 的 description 与路由。会话中途改了源文件，当前会话不会重读；**改了 description 或增删 skill 后，新开一轮 cc** 才能生效。link 脚本只管 symlink，不触发重载。

## 设计依据

`docs/superpowers/specs/2026-07-14-lucas-skill-workspace-design.md`（方案 A）

> 旧形态说明：`patent-skills/`、`ResearchStudio/`、`paper_search/`、`project-uav-skill/` 等是待按方案 A 收拢的历史目录（部分含独立 `.git`）。
