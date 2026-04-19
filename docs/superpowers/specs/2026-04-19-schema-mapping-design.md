# 点阵数据库 Schema 与 Mapping 设计

## 1. 目标

本设计用于为点阵吸能文献数据库项目定义第一版正式数据契约，覆盖以下 5 个文件：

1. `schemas/samples/schema_v1.json`
2. `schemas/evidence/schema_v1.json`
3. `mappings/structure/structure_mapping.csv`
4. `mappings/material/material_mapping.csv`
5. `mappings/process/process_mapping.csv`

本轮目标不是实现抽取脚本，也不是迁移现有 Markdown，而是先锁定后续所有清洗、抽取、融合、校验、复核流程共同依赖的稳定边界。

## 2. 本轮范围与非范围

### 2.1 本轮范围

本轮只定义：

- `samples` 主表的正式字段、类型、必填约束与质量控制字段
- `evidence` 最小证据表的字段、类型与来源优先级规则
- `structure`、`material`、`process` 三张 mapping 表的列设计与受控值规则
- 最小 ID 策略
- 最小校验规则

### 2.2 本轮非范围

本轮不定义：

- 具体脚本实现
- PDF 解析与抽取逻辑
- 图像识别策略
- review 界面形态
- 复杂知识图谱
- 大而全的材料/工艺 ontology
- `ea_j`、`ea_j_m3`、`sea_j_cm3`、`fm_kn`、`youngs_modulus_gpa`、`density_g_cm3` 等 v1 非必需扩展字段

## 3. 设计原则

### 3.1 正式契约优先于 Excel 便利性

这一版 schema 的优先级是服务后续抽取脚本、校验脚本、融合和 review 流程，而不是单纯服务手工编辑体验。

### 3.2 最小严格版

字段和规则必须足够严格，避免后续返工；同时避免一开始做成过度设计的大而全模型。

### 3.3 可追溯但不膨胀

保留少量关键 `raw_*` 字段和关键数值 `*_raw` 字段，用于回溯原始表达；不把主表做成原始 Excel 镜像。

### 3.4 证据独立于主表

`samples` 主表表达最终状态，`evidence` 表表达字段级证据。证据不在主表中重复展开。

### 3.5 显式失败，不做猜测

mapping 未命中、数值无法标准化、多证据冲突时，不允许静默兜底，不允许脚本自行猜测，必须进入 review。

## 4. 产物与职责

### 4.1 `schemas/samples/schema_v1.json`

定义样本主记录的正式契约，负责：

- 固定字段名
- 固定字段类型
- 固定受控枚举
- 固定最小必填约束
- 固定质量控制字段

### 4.2 `schemas/evidence/schema_v1.json`

定义字段级证据记录，负责：

- 表达字段值来自哪里
- 表达字段值的候选原貌
- 表达来源优先级与来源类型
- 表达人工确认状态

### 4.3 `mappings/*.csv`

定义三类标准化规则资产，负责：

- 从 `raw_*` 字段映射到正式受控值
- 固化结构、材料、工艺三类标准化规则
- 为清洗与抽取流程提供统一查表边界

## 5. `samples schema v1` 设计

### 5.1 定位

`samples` 主表只表达“一个样本的最终正式状态”，不重复承载图、表、段落级证据。

### 5.2 字段分组

#### A. 标识与追踪字段

- `paper_id`
- `sample_id`
- `doi`
- `title`
- `sample_label_in_paper`
- `is_multi_sample_paper`

#### B. 结构字段

- `raw_design`
- `raw_structure`
- `raw_type`
- `structure_main_class`
- `structure_subtype_list`
- `is_hierarchical`
- `is_graded`
- `is_optimized`
- `relative_density_raw`
- `relative_density_value`

#### C. 材料与工艺字段

- `raw_material`
- `raw_material_group`
- `material_canonical`
- `material_family`
- `raw_process`
- `process_canonical`
- `process_family`

#### D. 条件与性能字段

- `analysis_type`
- `test_mode`
- `loading_direction`
- `velocity_m_s_raw`
- `velocity_m_s`
- `sea_j_g_raw`
- `sea_j_g`
- `pcf_kn_raw`
- `pcf_kn`
- `mcf_kn_raw`
- `mcf_kn`
- `cfe_raw`
- `cfe`
- `plateau_stress_mpa_raw`
- `plateau_stress_mpa`

#### E. 质量控制字段

- `confidence_overall`
- `needs_manual_review`
- `review_status`
- `review_notes`

### 5.3 必填规则

Schema 级最小必填字段：

- `paper_id`
- `sample_id`
- `structure_main_class`
- `structure_subtype_list`
- `needs_manual_review`
- `review_status`

导出为“可接受样本”时的最低要求：

- `doi`
- `title`
- `structure_main_class`
- 至少一个核心性能字段存在：
  - `sea_j_g`
  - `pcf_kn`
  - `mcf_kn`
  - `cfe`
  - `plateau_stress_mpa`

### 5.4 类型规则

- `structure_subtype_list` 必须是数组
- 所有 `raw_*` 和 `*_raw` 字段必须是 `string | null`
- 所有标准化数值字段必须是 `number | null`
- `needs_manual_review` 必须是布尔值
- `is_multi_sample_paper`、`is_hierarchical`、`is_graded`、`is_optimized` 均为 `boolean | null`
- `confidence_overall` 为 `number | null`
- `review_notes` 为 `string | null`

### 5.5 枚举规则

以下字段必须使用受控枚举：

- `structure_main_class`
- `material_family`
- `process_family`
- `analysis_type`
- `test_mode`
- `loading_direction`
- `review_status`

未知值必须使用受控值 `unknown`，不允许自由文本。

## 6. `evidence schema v1` 设计

### 6.1 定位

`evidence` 为字段级证据表。单条 evidence 只服务一个 `sample_id` 的一个 `field_name`。

### 6.2 字段

- `evidence_id`
- `sample_id`
- `field_name`
- `field_value`
- `source_priority`
- `source_type`
- `page_no`
- `figure_id`
- `table_id`
- `text_snippet`
- `extractor`
- `extract_confidence`
- `verified_by_human`

### 6.3 类型规则

- `evidence_id`、`sample_id`、`field_name`、`source_priority`、`source_type` 为必填字符串
- `field_value` 为 `string | null`
- `page_no` 为 `number | null`
- `figure_id`、`table_id`、`text_snippet`、`extractor` 为 `string | null`
- `extract_confidence` 为 `number | null`
- `verified_by_human` 为布尔值

### 6.4 优先级与来源规则

最终决策顺序：

- `manual`
- `T1`
- `T2`
- `T3`

机器候选之间的顺序：

- `T1 > T2 > T3`

`source_priority` 只允许：

- `T1`
- `T2`
- `T3`
- `manual`

`source_type` 只允许：

- `text`
- `table`
- `figure`
- `derived`
- `manual`

### 6.5 冲突规则

允许同一个 `sample_id + field_name` 存在多条 evidence。

冲突不在 `evidence` 层解决，只在样本融合与 review 层解决。

## 7. Mapping 表设计

### 7.1 总规则

三张 mapping 表共用以下规则：

1. 只做单向映射
2. 只输出受控正式值
3. 未命中不猜测
4. 先做字符串标准化，再做查表
5. mapping 资产不承载证据

### 7.2 `structure_mapping.csv`

列：

- `raw_design`
- `raw_structure`
- `raw_type`
- `structure_main_class`
- `structure_subtype_list_json`
- `is_hierarchical`
- `is_graded`
- `mapping_notes`

联合唯一键：

- `normalized(raw_design)`
- `normalized(raw_structure)`
- `normalized(raw_type)`

`structure_subtype_list_json` 必须是 JSON 数组字符串。

`structure_main_class` 闭集：

- `truss_lattice`
- `tpms`
- `honeycomb_2d`
- `plate_lattice`
- `tube_lattice`
- `hybrid_lattice`
- `bioinspired`
- `voronoi`
- `unknown`

### 7.3 `material_mapping.csv`

列：

- `raw_material`
- `material_canonical`
- `material_family`
- `mapping_notes`

唯一键：

- `normalized(raw_material)`

`material_family` 闭集：

- `aluminum_alloy`
- `stainless_steel`
- `titanium_alloy`
- `polymer`
- `resin`
- `ni_ti_shape_memory`
- `magnesium_alloy`
- `steel`
- `composite_polymer`
- `unknown`

### 7.4 `process_mapping.csv`

列：

- `raw_process`
- `process_canonical`
- `process_family`
- `mapping_notes`

唯一键：

- `normalized(raw_process)`

`process_family` 闭集：

- `slm`
- `sls`
- `sla`
- `fdm`
- `forming_and_assembly`
- `unknown`

## 8. 字符串标准化规则

三张 mapping 共用轻量标准化规则：

1. 去除首尾空白
2. 连续空格压缩为一个空格
3. 将 Unicode 连字符统一为 ASCII `-`
4. 匹配时大小写不敏感
5. 空字符串、`-`、纯空白视为缺失
6. 缺失值不参与材料/工艺匹配
7. 结构三元组允许部分为空，但不能三列全空

此阶段只解决格式问题，不做语义推断。

## 9. ID 规则

### 9.1 `paper_id`

`paper_id` 作为论文级正式标识字段，在 schema 中视为必填。

### 9.2 `sample_id`

`sample_id` 作为样本级正式标识字段，在 schema 中视为必填。

### 9.3 本轮边界

本轮只锁定 `paper_id` 和 `sample_id` 的存在性与正式地位，不在 schema 层定义具体生成算法。生成逻辑留到 implementation plan 与实现阶段锁定。

## 10. 最小校验规则

本轮只锁定以下校验：

1. `structure_main_class`、`material_family`、`process_family` 必须命中闭集
2. `structure_subtype_list` 必须是数组
3. `needs_manual_review`、`verified_by_human` 必须是布尔值
4. 关键标准化数值字段必须是 `number | null`
5. 关键 `raw_*` / `*_raw` 字段必须是 `string | null`
6. mapping 未命中、数值解析失败、多证据冲突时，必须显式打上 review 标记
7. `unknown` 是合法受控值，自由文本不是

## 11. 流程边界

本轮设计固定的数据流如下：

`raw source -> mapping/evidence -> normalized samples -> validation -> review/export`

各层职责：

- `mapping`：负责规则化归一
- `evidence`：负责字段级证据留痕
- `samples`：负责样本最终状态
- `validation`：负责质量门槛
- `review`：负责 unresolved 情况

## 12. 错误处理规则

本轮只接受显式失败，不接受隐式兜底：

- mapping 未命中：进入 review
- 数值无法标准化：保留 `*_raw`，标准值设为 `null`
- 多证据冲突：保留多条 evidence，样本进入 review
- 非闭集枚举：视为校验失败

## 13. 本轮结论

本轮设计的核心结论是：

1. 先锁定正式契约，再做实现
2. `samples` 和 `evidence` 分层，不混合
3. `raw_*` 只保留关键字段，不做原表镜像
4. mapping 只做规则化映射，不做猜测
5. review 是显式流程节点，不是隐式兜底逻辑

后续实现必须严格以本设计为准，不得在实现阶段新增自由字段、自由枚举或模糊兜底行为。
