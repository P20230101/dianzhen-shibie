# 图像理解层设计稿

> 本设计定义一个独立执行支线，用于让系统真正识别文献图像内容，而不是只记录图注或 figure 元数据。

**Goal:** 从 PDF 图像中产出可回指原文的图像级结构化记录，包含图像类型、面板标识、图像摘要和置信度，供后续样本抽取使用。

**Architecture:** 以 PDF 解析结果为输入，先生成 figure registry，再做 figure-caption-context 对齐和 panel OCR，接着用 VLM 对单图进行 recaption / summary / classification，最后导出 figure JSONL 和 review CSV。该支线只输出图像级结果，不直接改写 sample/evidence/KG。

**Tech Stack:** Docling, Uni-Parser, PaddleOCR, VLM (Qwen2.5-VL or GPT-4o), JSONL/CSV, pytest fixtures

---

## 1. 为什么需要这一层

当前主线已经把 PDF 解析、正文抽取、表格抽取、样本级融合和证据链放进了路线，但图像内容本身仍然停留在“图注可见、图像元数据可见”的层面。对于点阵结构、失效模式、曲线图、复合图 panel 这些信息，只靠 caption 不能满足“真正识别图像内容”的目标。

这一层的职责很明确：把“图像”变成可计算的结构化对象，而不是把整篇 PDF 或所有图片一次性喂给下游模型。

## 2. 目标与非目标

### 2.1 目标

- 对每个 figure 生成稳定的图像级记录
- 将 figure、caption、page context 绑定到同一条证据链
- 识别图像类型，例如 `curve_plot`、`microstructure_image`、`schematic`、`composite_figure`
- 识别 panel / subfigure 标识，例如 `a`、`b`、`c`
- 生成结构化图像摘要和 recaption
- 保留置信度与人工复核标记

### 2.2 非目标

- 不直接生成 sample/evidence 记录
- 不直接写入 KG
- 不做模型训练或微调
- 不做整篇 PDF 端到端黑箱识别
- 不把 YOLO、DePlot 之类专项能力塞进第一版

## 3. 输入与输出

### 3.1 输入

输入来自现有 PDF 解析链的图像相关产物，最少包含：

- `paper_id`
- `pdf_path`
- `figure_id`
- `page_no`
- `image_path`
- `caption_text`
- `context_text`
- `figure_bbox`（如已有）

### 3.2 输出

输出建议写入 `data/03_figures/` 下的三类文件：

- `figures_v1.jsonl`
- `figures_review.csv`
- `manifest.json`

每条 figure 记录至少包含：

- `paper_id`
- `figure_id`
- `page_no`
- `image_path`
- `caption_text`
- `context_text`
- `panel_labels`
- `figure_type`
- `recaption`
- `figure_summary`
- `confidence`
- `needs_manual_review`
- `source_refs`

## 4. 处理链路

### 4.1 Figure Registry

先把 PDF 中的 figure 变成登记表。登记表只负责回答三个问题：

- 图在哪一页
- 图对应哪个 `figure_id`
- 图的原始图片路径是什么

### 4.2 Figure Binding

把 figure 与 caption、page context 对齐，避免后续只看图不看文，或只看 caption 不看图。

这一层的核心产物是：

- `caption_text`
- `context_text`
- `panel_labels`
- `subfigure_map`

### 4.3 Figure Understanding

对单张图做语义理解，输出：

- 图像类型
- 图像摘要
- recaption
- 置信度

如果图像包含 panel 标识，优先保留 panel 级信息，再生成整图摘要。

### 4.4 Validation and Export

把图像理解结果按统一 schema 导出到 JSONL，并同步生成人工复核表。复核表只保留需要人看的一部分，不把整批结果重新整理成另一个手工库。

## 5. 结果判定规则

### 5.1 置信度

每条 figure 记录都必须带置信度。置信度低于配置阈值时，`needs_manual_review` 置为 `true`。

### 5.2 面板识别

如果图中有 `a/b/c` 之类的 panel 标识，必须保留到 `panel_labels` 或 `subfigure_map`，不能只保留整图摘要。

### 5.3 图像类型

图像类型必须是明确枚举，不允许只写“图片”或“figure”。至少覆盖：

- `curve_plot`
- `microstructure_image`
- `schematic`
- `composite_figure`
- `unknown`

### 5.4 来源可回指

每条输出必须能回指到：

- 原始 PDF
- 页码
- figure 图片路径
- caption 或 context 来源

## 6. 错误处理

- 图像文件缺失：不直接失败整批任务，保留该 figure 的错误状态并进入复核表
- caption 为空：仍然允许做图像理解，但必须标记来源不完整
- panel OCR 失败：保留整图结果，并把 panel 级字段置空，不伪造 panel 信息
- 置信度过低：进入人工复核，不直接进入后续 sample/evidence 线

## 7. 验证方式

验证只看图像理解这一层是否独立闭合，不和 sample/evidence 混在一起。

最小验证包括：

- 选一组带图的 PDF fixture
- 每张 figure 都能产出一条结构化记录
- 记录里有 figure 类型、摘要、置信度和来源回指
- 带 panel 的图能保留 panel 信息
- 低置信度图能进入复核表

## 8. 本层与其他层的边界

### 8.1 不做什么

- 不写 sample/evidence
- 不写 KG
- 不替代文本抽取层
- 不把图像理解直接当最终数据库

### 8.2 后续怎么接

后续 sample 抽取可以消费本层输出的 `figure_summary`、`recaption`、`panel_labels` 和 `source_refs`，但那是下一条执行链的事，不属于本支线本身。

## 9. 交付物

- `data/03_figures/figures_v1.jsonl`
- `data/03_figures/figures_review.csv`
- `data/03_figures/manifest.json`
- 对应的图像理解层 smoke tests

