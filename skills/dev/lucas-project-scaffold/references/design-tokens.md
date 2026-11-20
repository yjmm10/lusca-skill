# 设计令牌（Design Tokens）统一规范

目标：让「改一个值 = 全局生效」且**不出现魔法数字**。颜色、字体、间距、圆角、阴影全部收敛到唯一 tokens 文件；组件只消费 token，不写死值。依据：MDN CSS 自定义属性（CSS Custom Properties）标准用法。

## 唯一来源文件

- 纯静态 / 无构建项目：`styles/tokens.css`
- Vite / 框架项目：`src/styles/tokens.css`
- 所有组件样式通过 `@import` / 构建配置引入该文件，**任何组件文件里不得出现新的颜色、字号、间距字面量**

## tokens.css 基本骨架

```css
:root {
  /* ---- 颜色：先定基础色板（primitive），再定语义色（semantic） ---- */
  /* 基础色板：只在这里出现十六进制值 */
  --indigo-600: #4f46e5;
  --indigo-700: #4338ca;
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-900: #111827;

  /* 语义色：组件只用这一层 */
  --color-primary: var(--indigo-600);
  --color-primary-hover: var(--indigo-700);
  --color-bg: var(--gray-50);
  --color-surface: #ffffff;
  --color-text: var(--gray-900);
  --color-text-muted: var(--gray-100);
  --color-danger: #dc2626;

  /* ---- 字体 ---- */
  --font-sans: "Inter", "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", Consolas, monospace;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.5rem;

  /* ---- 间距（4 的倍数阶梯）---- */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;

  /* ---- 圆角 / 阴影 / 过渡 ---- */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-full: 9999px;
  --shadow-sm: 0 1px 2px rgb(0 0 0 / 0.06);
  --shadow-md: 0 4px 12px rgb(0 0 0 / 0.1);
  --transition-fast: 150ms ease;
}
```

## 组件中的用法

```css
.card {
  background: var(--color-surface);
  color: var(--color-text);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-fast);
}
```

可带兜底值（较少用，主要用于第三方容器内防裸奔）：`var(--color-bg, #fff)`。

## 暗色主题（可选，一次说清）

用 `[data-theme="dark"]` 或 `@media (prefers-color-scheme: dark)` **只覆盖语义层变量**，基础色板不动：

```css
[data-theme="dark"] {
  --color-bg: #0b1020;
  --color-surface: #111827;
  --color-text: #f3f4f6;
}
```

因为组件只引用语义层，暗色适配不需要改任何组件代码——这正是分层的好处，向用户解释设计约定时用这个例子。

## 命名约定

- `--color-<语义>`：`--color-primary`、`--color-bg`、`--color-text-muted`
- `--text-<字号>`、`--font-<族>`、`--space-<数字>`、`--radius-<尺寸>`、`--shadow-<层级>`
- 语义层名字描述「用途」而不是「颜色」：用 `--color-danger` 不用 `--color-red`（换品牌色时语义不变）

## 变更规则（写入 agent 文件）

1. 改视觉 → 先查 tokens 是否已有对应变量；没有 → 在 tokens 文件里新增，再在组件引用
2. 改一个 token 的值 → 全局 grep 该变量名的引用面，评估影响后一起过目（改 `--color-primary` 会影响所有按钮/链接/高亮）
3. 禁止在组件里写 `#hex`、`px 字号`、`魔法间距`；发现即提醒并修正
4. 框架带样式方案（Tailwind / UI 库主题）时：把 tokens 作为其主题变量的数据源（如 Tailwind 的 `theme.extend.colors` 引用 CSS 变量），不搞两套值
