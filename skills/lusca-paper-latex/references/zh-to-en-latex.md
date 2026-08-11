# 中文稿 → 英文 LaTeX 翻译

中文稿转 LaTeX 时查本文件。翻译是"学术翻译"——把作者用中文写下的科学内容，用地道的学术英文重新表达，再排进 LaTeX。**不是逐句直译，也不是再次润色**（润色是 `lusca-paper-polish` 的事；本技能把中文译到位即止，英文稿不润色）。

## 1. 先保护，再翻译

翻译前先把 LaTeX 敏感片段抽成占位符（主流程第 3 步），译完还原：

- `$...$` `$$...$$` `\[...\]` `equation` `align` → `[[M0]]` `[[M1]]`（公式内容**不译**）
- `\cite{key}` `\ref{sec:x}` `\label{...}` `\url{...}` `\href{...}` → `[[C0]]`（命令与 key**不译**）
- 代码块、`` `inline code` `` → `[[V0]]`（代码**不译**）
- 已有的 `\textbf{}` `\usepackage{}` 自定义宏 → `[[C1]]`（保留原样）

只对占位之外的中文叙述翻译。还原后 `grep '\[\['` 确认零残留。

## 2. 学术翻译五原则

### ① 先取义，再造句

不要跟着中文语序逐字走。把每句的核心命题用自己的话朴素复述，再写成地道的学术英文。

- ❌ "本方法的优势是显而易见的" → "The advantage of this method is obvious"（中式直译、还多了"是"）
- ✅ → "The advantage of this method is evident" / "This method offers a clear advantage"

### ② 补回被中文语序藏起来的逻辑

中文学术写作常把转折、因果、让步、递进藏在语序里，英文要把它们用连接词说出来：

- 中文："该方法精度高，计算量大" （并列？转折？因果？中文不说）
- 英文要选一种关系："The method achieves high accuracy **but** incurs substantial computational cost."（转折）/ "The method **trades** computational cost **for** high accuracy."（取舍）

拿不准原文是哪种关系时，**不要替作者定**——选最保守的那个，或保留原文的并列结构，加一句译注让作者定。

### ③ 术语全文稳定一个译法

专业术语、基因 / 蛋白名、模型名、数据集名、统计术语：选一个译法，**贯穿全文**，绝不意译成模糊描述。

- 建一张术语表（term → translation），全文对照一致
- 缩写首次出现给全称 + 缩写：`Gradient Descent (GD)`，之后用 GD
- 中英混合稿里的英文术语（Transformer、BERT、ResNet）**保留英文原名**，不译成"变形金刚"之类

### ④ 修常见中式英语

中译英的高频病灶，翻译时一并修正：

| 病灶 | 修正 |
|------|------|
| 冠词缺失（"深度学习是流行技术"） | 补 a / the："Deep learning is **a** popular technology" |
| 复数漏（"多个模型"） | 复数 -s："multiple **models**" |
| 时态错（Methods 该用过去时） | Methods / Results 用过去时；普遍事实用现在时；引用他人已发表工作用现在时或过去时（按领域惯例） |
| 话题优先开头（"这个方法，它的优势…"） | 改主谓句："**The advantage of** this method…" |
| 弱动词堆砌（make / do / get / use） | 换精确动词：construct / perform / obtain / employ |
| 冗余范畴词（"进行研究" "实现改善"） | 删冗余："research"（非 "conduct research" 在紧凑句里）、"improve"（非 "achieve improvement"） |
| 名词化堆叠（"特征提取模块的实现与优化"） | 还原成动词："implementing and optimizing the feature extraction module" |
| 绝对化（"显然" "证明" "完全"） | 学术对冲：appears to / suggests / substantially（详见 §6 不注水） |

### ⑤ 标点、数字、单位

- 中文全角标点 → 英文半角：`，` `,`；`。` `.`；`：` `:`；`；` `;`；`（ ）` `( )`
- 中文引号 `" "` → LaTeX ``` ``...'' ```（左两个反引号、右两个单引号）；单引号 `' '` → `` `...` ``
- 省略号 `……` → `\dots`（数学里）或 `...`（正文）
- 破折号 `——` → `---`（em dash）
- 数字与单位间留空格：`20 ms`、`90\%`（百分号在 LaTeX 正文要转义为 `\%`）、`32\,000` 或 `32{,}000`（千分位）
- 数字范围：`10--20`（en dash），不是 `10-20`
- 角度 / 摄氏度：`$20^{\circ}\mathrm{C}$`

## 3. 中英混合稿的处理

常见情形：中文叙述夹英文术语、公式、引用。处理：

- **英文术语保留原英文**：Transformer、softmax、cross-entropy、ImageNet——不译
- **中文叙述译成英文**：连接词、动词、描述性内容
- **公式与引用原样保护**：走占位符，不译

混合稿按中文稿处理（走翻译支路），但翻译量小于全中文稿——只译中文部分。

## 4. 数字、百分号、单位的 LaTeX 处理

翻译时顺手处理 LaTeX 语法：

- 正文百分号：`90%` → `90\%`（`%` 是注释符，必转义）
- 数学里的百分号：`$90\%$` 也可，或写 `0.90` 比例
- 温度 / 角度：`20$^{\circ}$C` 或 `$20^{\circ}\mathrm{C}$`
- 乘号：`3×10^8` → `$3 \times 10^{8}$`（Unicode `×` 转 `\times`）
- 范围：`3-5` → `3--5`（en dash 表范围）

## 5. 分节语气（翻译时参考）

不同章节英文语体不同，与 `lusca-paper-polish` 的分节惯例一致：

- **Abstract**：现在时陈述普遍事实 + 过去时陈述本文所做；紧凑、150–250 词
- **Introduction**：现在时陈述已知、现在完成时陈述近期进展、本文贡献用 we propose / we present
- **Methods / Methodology**：过去时（"We trained..."）
- **Results**：过去时陈述发现（"The model achieved..."），现在时引用图表（"Table 1 shows..."）
- **Discussion**：现在时陈述解读、过去时引用自己的结果
- **Conclusion**：现在时总结贡献、概括意义

## 6. 不注水（继承 polish 的校准）

翻译不改论证强度。谨慎的中文不等于可以改成更强的英文：

- `可能` `提示` `在某种程度上` → may / suggest / partly，不译成 prove / demonstrate / conclusively
- `首次` `最优` `碾压` `颠覆性` → 没证据时不译成 first / optimal / outperform everything / groundbreaking；软化或标注待作者确认
- 拿不准中文的论断强度时，**就低不就高**——译成较保守的英文，让作者决定是否加强

完整动词阶梯与注水词表参见 `lusca-paper-polish` 的 `references/academic-phrasebank.md` 与 `references/ai-tone-guardrails.md`——本技能翻译时参照同一套尺度，但不负责对英文稿做二次润色。

## 7. 不臆造

翻译同样守 polish 的底线：

- 原文没有的数据、引用、实验结果、机理性解释——一律不加
- 原文模糊处（"某方法" 未指明）——保留模糊或加译注 `[which method?]`，不替作者补具体
- 读不清的中文（OCR 噪声、笔误）——加 `% TODO: 原文此处不清，译法待确认` 注释，不猜

## 8. 自检：翻译完成后

逐句对照中文源稿与英文 `.tex`：

- 这句英文的科学内容，和中文写下的，是同一回事吗？（每一处"不太一样"都要回退或标注）
- 术语是不是全文统一？（grep 关键术语，确认译法一致）
- 公式 / 引用 / 命令是不是零误伤？（占位符还原、`grep '\[\['` 清零）
- 有没有把中文的谨慎译成了英文的强论断？（就低不就高）
