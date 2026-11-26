# 产品数据契约

数据页是唯一事实源。落地页只读派生结果，任何“最新动态”“核心指标”都从 `product.json` 生成，不手写第二份。

## 归一流程

1. 识别来源：本地 JSON/MDX/CSV、远程 API、网页表格或用户粘贴文本。
2. 映射到 `assets/product.schema.json`：产品、作者、指标、更新、能力、画廊、FAQ、免责声明。
3. 本地化字段用 `{ zh, en }`；没有译文时保留空字符串并在 README 标记待补，不自动把未确认译文当成事实。
4. 运行 `scripts/normalize_data.py` 校验、排序并生成 `src/data/highlights.json`。
5. 数据页读完整 `product.json`；落地页读 `highlights.json`。

## 派生规则

- `latest`：按 `updates.date` 倒序取前 3 条；要有日期、标题、摘要和来源 URL。
- `metrics`：优先 `highlight: true`，再按 `period` 倒序，取前 3-6 条；必须带单位与时间。
- `features`：优先 `highlight: true`，其余保留在数据页。
- `gallery`：只引用本地 `public/images/` 或可信外链；每张图有本地化 alt。
- `faq`：来自数据，不为了 SEO 编问题；答案必须能在数据页找到依据。

## 单项展示规范

指标卡按“标签 → 数值+单位 → 变化 → 周期 → 来源”组织。变化值只在数据里有 `delta` 时显示；没有就留空，不写“持续增长”之类无依据措辞。表格列按读者决策顺序排列，默认列：指标、数值、周期、来源、更新时间。

## 缺失与异常

- 缺字段：保留键、值为空字符串，并在 `docs/data-sources.md` 记录缺失原因。
- 日期非法或未来日期：校验失败，要求用户确认，不自动改成今天。
- 远程数据源失败：保留上次成功快照并标注 `sourceFetchedAt`，不让页面空白。
- 示例数据：所有示例文案必须含“示例/Example”字样，README 列出替换点。

## 最小可读样例

见 `assets/product.example.json`。它是结构参考，不是真实产品数据；生成项目时必须替换或明确标注为示例。
