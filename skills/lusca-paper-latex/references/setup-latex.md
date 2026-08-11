# LaTeX 环境安装（Windows / Linux / macOS）

本 skill 的产出是**要能编译**的 `.tex`——编译验证是必做环节，不是可选项。本文件给三平台的 LaTeX 工具链安装指引。先检测，缺什么装什么。

## 0. 先检测现有环境

```bash
which latexmk pdflatex xelatex bibtex 2>/dev/null
latexmk --version 2>/dev/null && echo "✓ latexmk 就绪"
pdflatex --version 2>/dev/null | head -1
xelatex --version 2>/dev/null | head -1
```

- `latexmk` 命中 → 工具链就绪，可直接 `latexmk -pdf main.tex`（英文）/ `latexmk -xelatex main.tex`（中文）。
- 只有 `pdflatex`/`xelatex`、无 `latexmk` → 补装 `latexmk`（见各平台）。
- 全无 → 按下方对应平台装一套发行版。

> Windows 用户注意：Claude Code 的 `Bash` 工具在 Windows 上通常走 Git Bash 或 WSL。下面 Windows 节给了两条路径（MiKTeX + Git Bash / WSL + TeX Live），**WSL 兼容性最好**（与 Linux 一致）。

## 1. Linux

### Debian / Ubuntu（最常见）

```bash
# 精简够用（本 skill 的 article 模板所需 + 常见期刊宏包）
sudo apt update
sudo apt install \
  texlive-latex-base texlive-latex-recommended texlive-latex-extra \
  texlive-fonts-recommended texlive-fonts-extra \
  texlive-science texlive-bibtex-extra \
  latexmk

# 或一步到位（约 5 GB，省心，几乎不会再缺包）
sudo apt install texlive-full latexmk
```

### Fedora / RHEL

```bash
sudo dnf install texlive-scheme-full latexmk
```

### Arch / Manjaro

```bash
# 包名随版本可能调整，以 Arch Wiki 为准
sudo pacman -S texlive-meta biber latexmk
```

### 通用 installer（任意发行版，装到 /usr/local/texlive）

当系统源里的 TeX Live 太旧时用官方 installer：

```bash
cd /tmp
wget https://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz
tar -xzf install-tl-unx.tar.gz && cd install-tl-2*
sudo ./install-tl            # 交互式；或加 --no-interaction 默认全装
# 装后把 /usr/local/texlive/2024/bin/x86_64-linux 加进 PATH
```

验证：
```bash
latexmk --version
pdflatex --version
```

## 2. macOS

需先有 Homebrew（无则见 https://brew.sh）。

### MacTeX（完整，推荐，约 4 GB，含 latexmk 与几乎所有宏包）

```bash
brew install --cask mactex
```

安装后 MacTeX 在 `/Library/TeX/texbin`，brew cask 会通过 `/etc/paths.d/` 自动加 PATH；**新开一个终端**或 `eval "$(/usr/libexec/path_helper)"` 生效。

### BasicTeX（精简，约 100 MB，按需补包）

```bash
brew install --cask basictex
eval "$(/usr/libexec/path_helper)"
sudo tlmgr update --self
# 补本 skill 所需 + 常见宏包
sudo tlmgr install latexmk \
  collection-latexextra collection-fontsrecommended \
  collection-mathscience collection-langchinese
```

验证：
```bash
latexmk --version
```

## 3. Windows

### 方案 A：WSL + TeX Live（推荐，与 Linux 一致、兼容性最好）

在 WSL（Ubuntu）里按上面 Linux 节装。Claude Code 的 `Bash` 工具若走 WSL，能直接用 `latexmk`。

```powershell
# PowerShell 里装 WSL（若未装）
wsl --install -d Ubuntu
```
然后进入 WSL，按「Debian / Ubuntu」节执行 `apt install ...`。

### 方案 B：MiKTeX（原生 Windows，轻量、自动按需装包）

```powershell
# winget（Windows 10+ 自带）
winget install MiKTeX.MiKTeX
# 或 chocolatey
choco install miktex
```

安装后：
1. 打开 **MiKTeX Console** → Settings → "Install missing packages on-the-fly" 设为 **Yes**（编译时自动下载缺包，省去手动补包）。
2. 装 `latexmk`：MiKTeX Console → Packages，搜 `latexmk` 并安装；或命令行 `mpm --install=latexmk`。
3. 确认 PATH 含 MiKTeX bin（默认 `%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64`）——安装时勾选加 PATH 通常已就绪。

### 方案 C：TeX Live（原生 Windows，完整、与 Linux/macOS 一致）

```powershell
winget install TeXLive.TeXLive
# 或从 https://tug.org/texlive/acquire.html 下完整 installer / ISO
```
PATH 默认 `C:\texlive\2024\bin\windows`。含 `latexmk`。

### Windows 下验证（PowerShell 或 Git Bash）

```powershell
latexmk --version
pdflatex --version
xelatex --version
```

> Git Bash 用户：MiKTeX / TeX Live 的 bin 加进系统 PATH 后，Git Bash 里 `latexmk` 可直接用。

## 4. 缺宏包处理

编译时报 `! LaTeX Error: File 'xxx.sty' not found`：

| 发行版 | 补包命令 |
|--------|----------|
| TeX Live（Linux 通用 installer）/ MacTeX / BasicTeX | `sudo tlmgr install <包名>`（包名通常是 `.sty` 去后缀，如 `tlmgr install booktabs`） |
| MiKTeX | 开启 on-the-fly 自动装；或 `mpm --install=<包名>`；或 MiKTeX Console → Packages 搜并安装 |
| Debian/Ubuntu 的 texlive-* | 装对应的 collection：`sudo apt install texlive-latex-extra texlive-science texlive-fonts-extra` |
| Fedora | `sudo dnf install 'tex(<包名>.sty)'` 或装 `texlive-scheme-full` |

## 5. 本 skill 常用宏包

`article.tex` 默认骨架用到的宏包，装好下列即覆盖绝大多数英文稿：

```
amsmath  amssymb  amsthm  mathtools     # 数学
graphicx  booktabs  caption  subcaption  float   # 图表
listings                                  # 代码
natbib                                    # 文献（authoryear 样式）
xurl  hyperref                            # 链接（hyperref 最后加载）
```

**中文稿**另需 `xeCJK`：在 TeX Live / MacTeX 里属 `collection-langchinese`（`sudo tlmgr install collection-langchinese`）或 `texlive-lang-chinese`（apt）；MiKTeX 开 on-the-fly 会自动取。编译用 `xelatex`，并需系统装有中文字体（`Noto Serif/Sans CJK SC` 等，用 `fc-list :lang=zh` 查可用字体）。

## 6. 验证安装：跑通模板

```bash
cd outputs/lusca-paper-latex/<slug>/
latexmk -pdf main.tex        # 英文稿；能生成 main.pdf 即就绪
latexmk -xelatex main.tex    # 中文稿（需 xeCJK + 中文字体）
latexmk -c main.tex          # 清辅助文件（.aux .log .fls ...）
```

若生成 `main.pdf` 且 `.log` 末尾无 `! ` 级错误，工具链就绪。常见 warning（如 `Overfull \hbox`）不阻塞编译，按需调。
