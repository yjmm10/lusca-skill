# 设计令牌（Design Tokens）统一规范

目标：让「改一个值 = 全局生效」且**不出现魔法数字**。颜色、字体、间距、圆角、阴影全部收敛到唯一 tokens 文件；组件只消费语义层 token，不写死值。依据：MDN CSS 自定义属性（CSS Custom Properties）标准用法。

## 唯一来源文件

- 纯静态 / 无构建项目：`styles/tokens.css`
- Vite / 框架项目：`src/styles/tokens.css`
- **直接复制 `assets/tokens-starter.css` 作为起点**（已含基础色板→语义色两层、字体、间距阶梯、圆角/阴影/层级/动效、暗色主题覆盖、最小重置），按品牌改基础色板即可
- 所有组件样式通过 `@import` / 构建配置引入该文件，**任何组件文件里不得出现新的颜色、字号、间距字面量**

## 两层结构（为什么这样分）

- **基础色板层**（`--indigo-600` 等）：唯一允许出现十六进制值的区域，换品牌只改这里
- **语义层**（`--color-primary`、`--color-bg`、`--color-text-muted`…）：组件只引用这一层；名字描述**用途**而不是颜色（用 `--color-danger` 不用 `--color-red`），换品牌色时组件零改动
- 暗色主题只覆盖语义层变量（`[data-theme="dark"]`），组件不用感知——这是分层最直接的收益

## 组件中的用法

```css
.card {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-6);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-fast);
}

.card:hover { box-shadow: var(--shadow-md); }
```

可带兜底值（较少用，主要用于第三方容器内防裸奔）：`var(--color-bg, #fff)`。

## 与 Tailwind 共存（团队坚持用 Tailwind 时）

不搞两套色值：CSS 变量仍是唯一来源，Tailwind 只做引用。

```ts
// Tailwind v3：tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: "var(--color-primary)",
        bg: "var(--color-bg)",
        surface: "var(--color-surface)",
      },
      borderRadius: { md: "var(--radius-md)" },
    },
  },
};
```

```css
/* Tailwind v4：入口 css 里用 @theme 映射 */
@theme {
  --color-primary: var(--color-primary);
  --color-surface: var(--color-surface);
}
```

这样 `class="bg-primary"` 最终仍解析到 tokens，暗色切换依旧只改语义层。

## 硬编码审计（改完样式、提交前跑）

```bash
# 组件里出现十六进制色值（排除 tokens 文件本身）
grep -rnE "#[0-9a-fA-F]{3,8}\b" src --include="*.vue" --include="*.tsx" --include="*.ts" --include="*.jsx" | grep -v tokens.css

# 组件里出现 px 字号（字体大小应走 --text-*）
grep -rnE "font-size:\s*[0-9]+px" src --include="*.vue" --include="*.tsx" | grep -v tokens.css

# 间距魔法数字（padding/margin 用了非 var 的 px，4px 网格外都算）
grep -rnE "(padding|margin)[^:]*:\s*[0-9]+px" src --include="*.vue" --include="*.tsx" | grep -v tokens.css
```

有输出 → 当场改成对应 token 或提醒用户；把这几条 grep 放进 agent 文件的变更检查清单。

## 命名约定

- `--color-<语义>`：`--color-primary`、`--color-bg`、`--color-text-muted`
- `--text-<字号>`、`--font-<族>`、`--space-<数字>`、`--radius-<尺寸>`、`--shadow-<层级>`、`--z-<层级>`、`--transition-<速度>`
- 新增 token 先查是否已有语义相近的（如想要「次要文字色」时已有 `--color-text-muted`），避免同义 token 膨胀

## 变更规则（写入 agent 文件）

1. 改视觉 → 先查 tokens 是否已有对应变量；没有 → 在 tokens 文件里新增，再在组件引用
2. 改一个 token 的值 → 全局 grep 该变量名的引用面，评估影响后一起过目（改 `--color-primary` 会影响所有按钮/链接/高亮）
3. 禁止在组件里写 `#hex`、`px 字号`、魔法间距；发现即提醒并修正
4. 提交前跑上面的硬编码审计命令，输出应为空
