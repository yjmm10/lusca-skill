---
product: "{{PRODUCT_NAME}}"
meaning: "{{NAME_MEANING}}"
tone: "{{BRAND_TONE}}"
---

# Logo 设计说明

## 名字与语义

{{PRODUCT_NAME}} 的含义是 {{NAME_MEANING}}。Logo 用 {{LOGO_CONCEPT}} 表达这一含义，避免与名字无关的装饰。

## 图形

- 主符号：{{PRIMARY_SYMBOL}}
- 字标：{{WORDMARK_TREATMENT}}
- 品牌色：{{BRAND_COLOR}}；中性色沿用设计 token。
- 深浅主题：符号在两种背景下都保持识别度，必要时调整透明度而非换形状。

## 交付文件

- `public/logo.svg`：可编辑主文件。
- `public/logo.png`：512×512，由 SVG 渲染。
- `public/favicon.svg`：简化单色版本。
- `public/og-image.png`：1200×630，用于分享卡片。

## 提示词模板

```text
Minimal vector logo for {{PRODUCT_NAME}}, concept: {{LOGO_CONCEPT}}, flat geometric mark, no gradients, no mockup, no text other than the product wordmark, works in light and dark themes, SVG-friendly.
```
