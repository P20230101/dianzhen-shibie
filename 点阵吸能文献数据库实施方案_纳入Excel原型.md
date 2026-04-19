# 点阵吸能文献数据库项目实施方案（纳入现有 Excel 原型）

## 1. 文档目的

本文档用于把当前“点阵/吸能文献数据库构建”工作，整理为一条**可落地、可迭代、可验证**的实施路线。  
重点不是直接追求一个“全自动识别整篇 PDF 并一次性吐出完美数据库”的系统，而是先构建一个**可靠的多模态数据工厂**，再逐步增强自动化水平。

本方案已经**纳入你现有的 Excel 数据库原型**进行设计。结论很明确：

**你的 Excel 文档非常有参考价值，应该被视为项目的 v0 数据底座，而不是旁支材料。**

它的价值不在于“格式最终版已经定型”，而在于它已经提供了：

1. 当前最接近你研究目标的字段集合  
2. 你已经人工整理过的一批样本记录  
3. 结构/材料/工艺/加载/性能之间的初步组织方式  
4. 后续自动抽取系统的校验目标（gold-like prototype）

---

## 2. 为什么你的 Excel 有很强参考性

从当前工作流角度看，这份 Excel 至少有四层价值。

### 2.1 它已经是“样本级数据库”的雏形
你的数据库 sheet 已经不是单纯的文献目录，而是在按**单条实验/单个结构样本**组织记录。  
这比“每篇论文一行”的普通文献表更接近真正可用于后续机器学习和候选结构检索的数据库形式。

### 2.2 它已经给出了最初的字段分组逻辑
你当前表头已经隐含了几个核心模块：

- Paper information
- Structure design
- Material properties
- Manufacture procedure
- Analysis conditions
- Mechanical properties

这说明你已经自然形成了一个很重要的思想：  
**数据库不是按论文写作结构组织，而是按“样本描述逻辑”组织。**

这和后续多模态抽取系统的目标是一致的。

### 2.3 它可以直接作为自动抽取系统的“目标 schema 起点”
后续无论你用大模型、VLM、多代理还是规则系统，最终都要落到一个结构化 schema 上。  
而你的 Excel 其实已经给出了第一版 schema 雏形，例如：

- Authors / Title / DOI
- Design / Structure / Type / Optimized? / Relative Densities
- Material / Young Modulus / Density
- Process
- Analysis / Test / Direction / Velocity
- EA / SEA / PCF / MCF / CFE / Plateau Stress

这意味着你不需要从零重新想“数据库到底长什么样”，而是可以在当前 Excel 基础上**升级为标准化 schema v1**。

### 2.4 它是后续评估与人工复核的重要参照
后续系统抽取出的 JSON 或表格，不能只看“模型说得通不通”，还要和一个人工整理过的版本对照。  
因此这份 Excel 可以承担三个角色：

- **种子数据库（seed database）**
- **字段设计参考（schema prototype）**
- **抽取结果核验基准（validation prototype）**

---

## 3. 但 Excel 不能直接作为最终系统，需要升级

虽然 Excel 很有价值，但它更适合作为 **v0 原型**，不能直接当最终数据库规范。  
原因是它还缺少多模态自动抽取系统所必需的几个关键层。

### 3.1 缺少证据追踪字段
当前表格主要是“结果值”，但后续系统需要知道这些值从哪里来。  
建议新增：

- `source_type`：text / table / figure / derived / manual
- `source_page`
- `source_figure_id`
- `source_table_id`
- `source_caption`
- `source_context`
- `evidence_snippet`
- `confidence`

### 3.2 缺少标准化/归一化层
当前 Excel 很适合人工使用，但机器学习前还要进一步统一：

- 单位统一
- 缺失值统一（如 `-`、空白、approx、范围值）
- 分类名统一（Beam、honeycomb、TPMS、lattice 等）
- 布尔字段统一（Yes/No、True/False）
- 材料名统一（316L / Stainless steel / SS316L 等）

### 3.3 缺少“结构 subtype 数组层”
你之前已经明确提出：  
**结构主类下面还要有 subtype，而且 subtype 不应强制单选，最好支持数组。**

这点非常关键。因为一个样本可能同时带有多个结构特征，例如：

- 主类：`tpms`
- 子类：`["gyroid"]`

或者：

- 主类：`honeycomb_2d`
- 子类：`["hexagonal", "graded_honeycomb"]`

Excel 里可以暂时用分号分隔保存，但最终 schema 建议用数组。

### 3.4 缺少“字段来源优先级”
后续系统一定要采用如下优先级：

- **T1**：正文 / 表格直接抽取
- **T2**：由明确已知量推导
- **T3**：从图中读数

原因很简单：  
图中读数最脆弱，误差最大，不应该默认优先。

### 3.5 缺少 figure-caption-context 单元
对于点阵结构识别、图像理解和性能图读取，仅靠 Excel 当前字段还不够。  
你还需要把每篇论文中的每张图组织为：

- figure image
- raw caption
- in-text context
- subfigure info
- figure type
- recaption / structured image summary

这样才能真正接上后面的科学图像理解模块。

---

## 4. 项目总目标

最终目标不是做一个“识图 demo”，而是构建一个：

**面向点阵吸能文献的样本级、多模态、可追溯数据库系统**

系统要实现四件事：

1. 从 PDF 文献中抽取样本级信息  
2. 支持结构、材料、工艺、加载条件、性能字段的统一建库  
3. 保留每个字段的证据来源和置信度  
4. 支持后续“按功能需求返回候选结构”的检索与推荐

---

## 5. 推荐总路线（一句话版）

**PDF 解析 → 图/表/文切分 → 文本先抽 → 单图补充 → 样本级融合 → T1/T2/T3 校验 → 人工复核入库**

---

## 6. 系统总体架构

推荐拆成六层，而不是做成一个“大模型黑箱”。

### 6.1 文档解析层
负责把 PDF 变成结构化可处理对象。

输出：

- 页面图像
- 文本 chunk
- 表格
- figure-captions
- in-text references
- subfigure 区域

### 6.2 图像理解层
负责理解科学图像，不直接产出最终数据库。

任务包括：

- 图类型分类
- 复合图切分
- 结构图描述
- 曲线图识别
- SEM/CT 图语义总结
- 图像 recaption

### 6.3 文本抽取层
从正文、表格中先提取显式字段。

这是最稳定的一层，应优先做。

### 6.4 多模态融合层
把文本、表格、图像三个来源的候选信息合并为样本级记录。

### 6.5 校验与标准化层
负责：

- 单位统一
- 字段规范化
- 同义词合并
- 冲突消解
- 缺失值显式化
- 物理合理性检查

### 6.6 数据库与服务层
最终把数据写入：

- JSON
- Excel / CSV
- SQL / Lite 数据库
- 检索接口

---

## 7. Excel 在新系统中的正确定位

你的 Excel 不应该被替代掉，而应该被重新定义为下面四个角色。

### 7.1 角色一：Schema 原型
先基于 Excel 字段，整理出标准化字段表。

### 7.2 角色二：人工入库界面
在系统早期，自动抽取结果可先写回 Excel 供你人工审查。

### 7.3 角色三：抽取评估基准
把已经整理好的记录当成对照集，用来比较：

- 自动抽取是否漏字段
- 单位是否错误
- 结构类别是否错判
- 图中读数是否偏差过大

### 7.4 角色四：候选检索原型库
在真正做数据库服务前，先利用 Excel 进行：

- 结构筛选
- 性能排序
- 功能需求映射

---

## 8. 建议把 Excel 升级为 schema v1

下面是建议的 schema 结构。  
其中前半部分尽量兼容你当前 Excel，后半部分是新增的“自动抽取系统必需字段”。

## 8.1 文献信息
- `paper_id`
- `title`
- `authors`
- `year`
- `journal`
- `doi`

## 8.2 样本身份
- `sample_id`
- `sample_label_in_paper`
- `structure_main_class`
- `structure_subtype[]`
- `design_description`
- `is_optimized`
- `relative_density`
- `porosity`
- `gradient_flag`

## 8.3 材料信息
- `base_material`
- `material_standard_name`
- `young_modulus_gpa`
- `density_g_cm3`
- `yield_strength_mpa`
- `other_material_properties`

## 8.4 制造与后处理
- `manufacturing_process`
- `post_treatment`
- `process_details`

## 8.5 试验/分析条件
- `analysis_type`
- `test_type`
- `loading_mode`
- `loading_direction`
- `strain_rate`
- `velocity_m_s`
- `temperature`
- `boundary_condition`
- `specimen_size`

## 8.6 力学/吸能性能
- `ea_j`
- `ea_j_m3`
- `sea_j_g`
- `sea_j_cm3`
- `pcf_kn`
- `fm_kn`
- `mcf_kn`
- `efficiency_ea_percent`
- `cfe`
- `plateau_stress_mpa`
- `peak_stress_mpa`
- `densification_strain`
- `failure_mode`

## 8.7 证据与溯源（新增）
- `source_priority`（T1/T2/T3/manual）
- `source_type`（text/table/figure/derived/manual）
- `source_page`
- `source_figure_id`
- `source_table_id`
- `source_caption`
- `source_context`
- `evidence_snippet`
- `confidence`

## 8.8 系统处理字段（新增）
- `normalized_flag`
- `review_status`
- `review_notes`
- `parser_version`
- `extraction_time`

---

## 9. 实施阶段建议

---

## 阶段 0：先把 Excel 清洗成标准化原型库

### 目标
把现有 Excel 从“人工整理表”升级为“系统可对接的种子数据库”。

### 任务
1. 字段重命名与规范化
2. 统一缺失值表示
3. 拆分主类 / subtype
4. 统一单位
5. 增加 `sample_id`
6. 增加 `source_priority`、`source_type`、`confidence`
7. 增加 `review_status`

### 输出
- `lattice_db_seed_v1.xlsx`
- `schema_v1.json`
- `field_dictionary.md`

### 这一阶段为什么必须做
因为如果 Excel 本身不标准，后面的自动抽取结果就没有地方可以稳定落地。

---

## 阶段 1：做 PDF 解析与多模态切分

### 目标
把 PDF 从“不可直接利用的文档”变成“结构化输入”。

### 输入
- 点阵/吸能领域 PDF 论文

### 输出
每篇论文形成一个解析目录，例如：

```text
papers/
  paper_001/
    paper.pdf
    meta.json
    pages/
    text_chunks.json
    tables.json
    figures/
      fig_001.png
      fig_001.json
      fig_002.png
      fig_002.json
```

### `fig_001.json` 建议结构
```json
{
  "figure_id": "fig_001",
  "page": 5,
  "caption_raw": "...",
  "context_paragraphs": ["...", "..."],
  "figure_type": "curve_plot",
  "subfigures": [],
  "recaption": null
}
```

### 这一阶段重点
不是抽知识，而是把文档拆干净。

---

## 阶段 2：文本优先抽取（T1）

### 目标
先从正文和表格抽取最可靠信息。

### 优先抽取字段
- DOI / 年份 / 作者
- 结构名称
- 材料
- 制造方法
- 相对密度
- 样本尺寸
- 加载方式
- 速度 / 应变率
- 文中直接给出的性能值

### 原则
- 能从正文或表格直接拿到的，不要先去图里读
- 每个值都保留证据片段

### 输出
`sample_candidates_text.json`

---

## 阶段 3：图像理解与单图补充（T3 辅助）

### 目标
对文本没覆盖到的内容，按图逐张补充。

### 不建议做法
- 把整篇 PDF 和全部图片一次性扔给 VLM

### 建议做法
对每张图单独处理，输入：

- figure image
- raw caption
- context paragraph
- 已有 sample 候选信息

输出：

- 该图补充了哪些字段
- 关联到哪个 sample
- 图像理解摘要
- 置信度

### 图类型建议先分 5 类
1. 结构示意图
2. 曲线图（应力-应变、SEA、EA 等）
3. 微观图（SEM/CT/断口）
4. 实验装置图
5. 表格截图 / 复合图

### 这一阶段重点
图像层先做“补充”和“解释”，不要一开始就承担全部字段抽取任务。

---

## 阶段 4：样本级融合

### 目标
把文本抽取结果和图像补充结果合并成最终样本。

### 关键问题
1. 一个图对应哪个样本？
2. 一个性能值属于哪个结构参数组合？
3. 同篇论文多个样本如何区分？

### 建议字段
- `paper_id + sample_label_in_paper + structure + relative_density + material`
作为初始样本匹配键

### 输出
`paper_level_samples_merged.json`

---

## 阶段 5：标准化、验证、人工复核

### 目标
保证数据库不是“模型瞎猜集合”，而是可用研究数据。

### 必做内容
1. 单位归一化
2. 同义词归并
3. 数值范围检查
4. 来源优先级检查（T1 > T2 > T3）
5. 冲突值标记
6. 缺失值显式 null
7. 人工复核入口

### 输出
- `lattice_db_v1.xlsx`
- `lattice_db_v1.json`
- `review_queue.xlsx`

---

## 阶段 6：支持“按功能需求返回候选结构”

### 目标
从“数据库”走向“可查询系统”。

### 查询示例
- 高 SEA + 低 PCF 的结构有哪些？
- 冲击载荷下表现稳定的 TPMS 子类有哪些？
- 铝合金点阵中，哪类结构在某相对密度范围下更优？

### 最小实现方式
先不用复杂推荐模型，可先做规则筛选：

1. 功能需求转为指标约束  
2. 指标约束映射到数据库字段  
3. 返回候选结构及对应文献证据

---

## 10. MVP（最小可运行版本）建议

我建议你不要一步做到“大系统”，而是先做 MVP。

## 10.1 MVP 目标
选 20 篇代表性论文，跑通完整流程：

- 解析 PDF
- 切分图/表/文
- 抽取 15~20 个核心字段
- 输出样本级 JSON
- 回写 Excel 供人工复核

## 10.2 MVP 必选字段
建议只做这些核心字段：

- DOI
- Title
- Structure main class
- Structure subtype[]
- Material
- Relative density
- Manufacturing process
- Test type
- Velocity / strain rate
- EA
- SEA
- Plateau stress
- PCF
- MCF
- CFE
- source_type
- source_priority
- confidence

## 10.3 MVP 不必一开始做的内容
- 复杂知识图谱
- 端到端训练
- 大规模自动图中数字精准读取
- 高级推荐模型
- 前端网站

---

## 11. 推荐目录结构

```text
project/
  docs/
    实施方案.md
    schema_v1.json
    field_dictionary.md
    prompt_library.md

  data/
    raw_papers/
    parsed_papers/
    extracted_candidates/
    merged_samples/
    reviewed_database/

  excel/
    Lattice crashworthiness data.xlsx
    lattice_db_seed_v1.xlsx
    lattice_db_review.xlsx

  src/
    pdf_parser/
    text_extractor/
    figure_parser/
    merger/
    validator/
    exporter/

  outputs/
    json/
    xlsx/
    reports/
```

---

## 12. 推荐开发顺序（非常重要）

正确顺序：

1. 先清洗 Excel
2. 再定义 schema
3. 再做 PDF 解析
4. 再做文本抽取
5. 再做单图补充
6. 再做融合与校验
7. 最后才考虑训练/微调

不推荐顺序：

1. 先训一个识图模型
2. 再想字段怎么存
3. 再回头处理 Excel

原因是如果 schema 和种子库不先稳定，后面所有模型输出都会变成漂浮结果。

---

## 13. 工具与模块建议

## 13.1 当前阶段推荐工具组合
- PDF 解析：文档解析工具 + 自己的切分脚本
- 文本抽取：LLM + 规则抽取
- 图像理解：VLM / MLLM
- 表格和数据库管理：Excel + JSON
- 复核与对照：人工校验表

## 13.2 不建议当前阶段过度投入的内容
- 一开始就重训练大模型
- 一开始就搭复杂 Web 前端
- 一开始就追求完全无人值守

---

## 14. 你的 Excel 在后续工作中的具体用法

这里给出一个最实际的用法建议。

### 14.1 作为 `seed_db`
把你当前 Excel 整理成标准版，作为种子库。

### 14.2 作为 `evaluation_set`
挑出其中你最确信的一部分记录，作为人工高可信对照集。

### 14.3 作为 `review_interface`
自动抽取结果先回写到 Excel，让你进行人工修正。

### 14.4 作为 `query prototype`
在真正做数据库检索服务前，先在 Excel 里验证筛选逻辑。

---

## 15. 当前最值得立刻执行的三件事

### 第一件：整理 Excel 为 schema v1
也就是明确：

- 哪些列保留
- 哪些列重命名
- 哪些列拆分
- 哪些值归一化
- 哪些新列必须新增

### 第二件：建立“样本级记录”的唯一标识
建议新增：

- `paper_id`
- `sample_id`
- `sample_label_in_paper`

### 第三件：建立证据链字段
哪怕先手工加，也必须把：

- `source_type`
- `source_priority`
- `source_page`
- `evidence_snippet`

补进去。

---

## 16. 最终结论

你的 Excel 文档**不仅有参考性，而且应该成为整个项目实施路线中的核心基础件之一**。  
正确做法不是绕开它，而是：

**把 Excel 升级为标准化种子数据库 + 抽取评估基准 + 人工复核接口。**

整个项目最合理的实施路线是：

**先做“可追溯的多模态数据工厂”，再逐步增强自动抽取能力，最后再走向功能检索与候选结构返回。**

换句话说：

- Excel 不是终点
- 但它绝对是起点
- 而且是现在最有工程价值的起点

---

## 17. 下一步建议

建议你下一步直接继续做两份文档：

1. `数据库清洗与字段标准化方案.md`
2. `最小系统实现方案.md`

前者解决“字段如何定”；  
后者解决“代码和流程如何跑”。
