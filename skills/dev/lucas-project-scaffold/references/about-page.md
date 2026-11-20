# 关于页（About）

## 是否要：先给选项

- **A 不做**：单页工具、落地页本身已含信息 → 推荐，省维护
- **B 简版自述**：一个 section 或独立轻页面
- **C 参考页面定制**：用户提供参考页面（链接 / 截图）

## 简版信息结构（B 方案）

信息层级按此顺序，能少则少：

1. 一段定位：这是什么、给谁用（2-3 句，与 README 首屏一致）
2. 特性列表：3-5 条，每条一个动词开头
3. 作者/团队：名字 + 一句话
4. 联系方式 / 仓库链接
5. 版本与最近更新时间

页面骨架（放在 `about.html` 或路由 `/about`，样式全部走 tokens）：

```html
<section class="about">
  <h1>关于 <项目名></h1>
  <p class="about-intro">这是一款<给谁用>的<是什么>，帮助<用户><解决什么问题>。</p>

  <h2>它能做什么</h2>
  <ul class="about-features">
    <li><动词开头的特性 1></li>
    <li><动词开头的特性 2></li>
  </ul>

  <h2>作者</h2>
  <p><名字> — <一句话介绍></p>

  <p class="about-links">
    <a href="<repo>">源码仓库</a> · <a href="mailto:<email>>联系我们</a>
  </p>
  <p class="about-version">v0.1.0 · 更新于 <日期></p>
</section>
```

```css
/* 样式示例：全部引用语义 token，不出现色值/魔法数 */
.about { max-width: 40rem; margin: 0 auto; padding: var(--space-8) var(--space-4); }
.about h1 { font-size: var(--text-xl); line-height: var(--leading-tight); }
.about h2 { font-size: var(--text-lg); margin-top: var(--space-8); }
.about-intro { color: var(--color-text-muted); }
.about-links a { color: var(--color-primary); }
```

## 参考页引用方法（C 方案）

1. 从参考页**提取**四样东西填入下表——**不抄**配色代码、图片素材、文案：

| 提取项 | 参考页的做法 | 映射到本项目 |
|--------|--------------|--------------|
| 布局骨架 | 顶部横幅 + 双栏（左正文右侧栏） | 单栏居中（本项目页面少，双栏过重） |
| 信息层级 | 先讲团队故事，再讲功能 | 调整为先功能后团队（工具类项目功能优先） |
| 交互模式 | 团队卡片 hover 翻转 | 简化为 hover 变阴影（`--shadow-sm → --shadow-md`） |
| 区块顺序 | 头像墙 → 使命 → 联系表单 | 头像省略 → 使命 → 邮箱链接（无表单） |

2. 把提取结果**映射到本项目 tokens 与已有组件**：颜色、圆角、字体、间距全部用本项目 token；组件复用 `components/` 里已有的
3. 参考页与本项目风格差异过大（如参考页是暗色玻璃拟态、本项目是亮色简洁风）→ 先提醒用户确认再动手
4. 版权注意：只借鉴结构与模式，不搬运受版权保护的素材与成段文案

## 验收清单

- [ ] 关于页信息与 README 定位一致，无矛盾表述
- [ ] 全部颜色/间距/字体来自 tokens，无写死值（跑 design-tokens 的硬编码审计命令确认）
- [ ] 移动端可读（单栏可折叠）
- [ ] 链接可点（仓库 / 联系方式真实有效）
- [ ] 版本号与 CHANGELOG 当前版本一致
