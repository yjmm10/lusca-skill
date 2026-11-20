# Logo 绘制指南

用**内联 SVG** 生成，不依赖外部图片服务。目标是「简洁、单色可反白、小尺寸可识别」，不是复杂插画。

## 步骤

1. **取意象**：从项目名取首字母，或取一个核心图形隐喻（如 Radar→同心圆、Notes→书签、Dash→色块网格、Flow→折线）
2. **定颜色**：主色从项目 design tokens 取（如 `--color-primary` 对应的值）；tokens 尚未建立时先定一个主题色，并同步写进 tokens
3. **选方向**：给用户 2-3 个方向选择（选项格式：「方向名 + 一句视觉效果描述 + 一句代价」）：
   - 字母标（monogram）：最快、最稳，小尺寸清晰
   - 图形标（abstract mark）：品牌感强，但抽象图形要用户认可
   - 组合标（图形 + 名称）：信息最全，但页头占宽
4. **落盘**：存 `assets/logo.svg`，README 顶部引用；建议 `viewBox="0 0 512 512"`
5. **配套**：同色系生成 32×32 的 favicon（`public/favicon.svg` 或静态站 `assets/favicon.svg`），并在入口 HTML `<head>` 加：
   `<link rel="icon" type="image/svg+xml" href="assets/favicon.svg" />`

## 成品示例 A：字母标（首字母）

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="96" fill="#4F46E5"/>
  <text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle"
        font-family="Arial, sans-serif" font-size="280" font-weight="bold"
        fill="#FFFFFF">L</text>
</svg>
```

## 成品示例 B：图形标（同心圆 = Radar/监测类项目）

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="96" fill="#4F46E5"/>
  <circle cx="256" cy="256" r="150" fill="none" stroke="#FFFFFF" stroke-opacity="0.35" stroke-width="24"/>
  <circle cx="256" cy="256" r="90"  fill="none" stroke="#FFFFFF" stroke-opacity="0.6" stroke-width="24"/>
  <circle cx="256" cy="256" r="30"  fill="#FFFFFF"/>
</svg>
```

## 成品示例 C：图形标（书签 = 笔记/收藏类项目）

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="96" fill="#4F46E5"/>
  <path d="M176 112h160a16 16 0 0 1 16 16v272l-96-64-96 64V128a16 16 0 0 1 16-16z"
        fill="#FFFFFF"/>
</svg>
```

## 给用户的选项消息模板

> logo 给三个方向，选一个（也可以描述你的想法我重新画）：
> 1. **字母标**：圆角方块 + 首字母「M」，最简洁，缩小到 favicon 也清晰
> 2. **图形标-同心圆**：呼应「监测/雷达」含义，品牌感强，但含义需要解释
> 3. **图形标-书签**：呼应「笔记/收藏」含义，具象好懂，图形感略普通

## 注意

- `<text>` 依赖系统字体，跨环境渲染有差异；正式用途把字母转成 `<path>` 或改用纯图形
- 圆角、底色、前景色全部应来自项目 tokens 的色值，保持品牌一致
- 深浅两种背景都要可用：必要时出 `logo-dark.svg` / `logo-light.svg` 两版
- 改完 logo 同步更新：README 顶部引用、favicon、（如有）PWA manifest 的 icon 项
