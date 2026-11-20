# Logo 绘制指南

用**内联 SVG** 生成，不依赖外部图片服务。目标是「简洁、单色可反白、小尺寸可识别」，不是复杂插画。

## 步骤

1. **取意象**：从项目名取首字母，或取一个核心图形隐喻（如 Radar→同心圆、Notes→书签、Dash→色块网格）
2. **定颜色**：主色从项目 design tokens 取；tokens 尚未建立时先定一个主题色，并同步写进 tokens
3. **选方向**：给用户 2-3 个方向选择——字母标（monogram）/ 图形标（abstract mark）/ 组合标（图形+名称）
4. **落盘**：存 `assets/logo.svg`，README 顶部引用；建议 `viewBox="0 0 512 512"`
5. **配套**：同色系生成一个 32×32 的 favicon（`public/favicon.svg`）

## 示例骨架（首字母标）

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="96" fill="#4F46E5"/>
  <text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle"
        font-family="Arial, sans-serif" font-size="280" font-weight="bold"
        fill="#FFFFFF">L</text>
</svg>
```

## 注意

- `<text>` 依赖系统字体，跨环境渲染有差异；正式用途把字母转成 `<path>` 或改用纯图形
- 圆角、底色、前景色全部应来自项目 tokens 的色值，保持品牌一致
- 深浅两种背景都要可用：必要时出 `logo-dark.svg` / `logo-light.svg` 两版
