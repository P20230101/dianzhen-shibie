# 点阵吸能文献数据库目录骨架设计

## 1. 目标

本设计用于为 `C:\Users\Administrator\Desktop\dianzhen shujuku` 建立一套可持续维护的项目目录骨架。

本次任务只做三件事：

1. 统一项目目录分层。
2. 固化目录与流程的对应关系。
3. 为后续 schema、mapping、抽取脚本、复核流程预留稳定落点。

本次任务不做以下内容：

1. 不初始化空模板文件。
2. 不编写抽取脚本。
3. 不迁移现有 4 篇根目录 Markdown。
4. 不修改 Excel 内容或 schema 内容。

## 2. 设计原则

### 2.1 按流程边界建目录

目录服务于“原始输入 -> 解析中间层 -> 抽取结果 -> 融合结果 -> 清洗结果 -> 最终导出”的数据生命周期，而不是服务于当前工具名。

### 2.2 根目录保持干净

根目录只允许保留总览性文件与一级功能目录，不继续堆放过程性资产。

### 2.3 规范资产与数据资产分离

规范文档、schema、mapping、review 队列、最终导出必须分目录管理，避免中间产物和规则资产混放。

### 2.4 目录名统一使用 ASCII

所有新建目录统一使用 ASCII，避免后续脚本、命令行工具和跨平台处理时出现路径编码问题。

## 3. 目录方案

推荐目录骨架如下：

```text
docs/
  01_scope/
  02_schema/
  03_workflow/
  04_review/
  superpowers/
    specs/
    plans/

data/
  01_raw/
    pdfs/
    excel/
  02_parsed/
  03_extracted/
  04_merged/
  05_cleaned/
  06_exports/

mappings/
  structure/
  material/
  process/

schemas/
  samples/
  evidence/

scripts/
  ingest/
  extract/
  merge/
  validate/
  export/

reviews/
  pending/
  done/

outputs/
  json/
  csv/
  xlsx/

archive/
```

## 4. 目录职责定义

### 4.1 `docs/`

保存项目规范、范围、工作流和复核规则。

- `01_scope/`：项目范围、阶段边界、目标定义。
- `02_schema/`：字段体系、数据字典、schema 说明。
- `03_workflow/`：处理链路、执行顺序、流程约束。
- `04_review/`：人工复核标准、验收规则、问题清单。
- `superpowers/specs/`：设计说明。
- `superpowers/plans/`：实施计划。

### 4.2 `data/`

保存全流程数据资产，严格按生命周期分层。

- `01_raw/pdfs/`：原始 PDF 文献。
- `01_raw/excel/`：原始 Excel 或人工种子表。
- `02_parsed/`：PDF 解析后的 paper-level 中间产物。
- `03_extracted/`：文本、表格、图像抽取结果。
- `04_merged/`：样本级融合结果。
- `05_cleaned/`：标准化、校验后的清洗结果。
- `06_exports/`：对外导出的中间版本数据。

### 4.3 `mappings/`

保存标准化映射资产。

- `structure/`：结构主类与 subtype 映射。
- `material/`：材料 canonical 与 family 映射。
- `process/`：工艺标准化映射。

### 4.4 `schemas/`

保存正式 schema 资产。

- `samples/`：样本主表 schema。
- `evidence/`：证据表 schema。

### 4.5 `scripts/`

保存按职责划分的脚本目录。

- `ingest/`：导入与解析入口。
- `extract/`：字段抽取。
- `merge/`：样本级融合。
- `validate/`：规则校验与标准化。
- `export/`：导出与回写。

### 4.6 `reviews/`

保存人工复核队列。

- `pending/`：待复核对象。
- `done/`：已复核对象。

### 4.7 `outputs/`

保存最终对外交付物。

- `json/`：JSON 导出。
- `csv/`：CSV 导出。
- `xlsx/`：Excel 导出。

### 4.8 `archive/`

保存不再处于主流程中的历史资产，避免主流程目录污染。

## 5. 流程规范

后续所有新文件都必须先判断其所属阶段，再决定落点：

1. 原始输入只进 `data/01_raw/`。
2. 解析中间层只进 `data/02_parsed/`。
3. 抽取候选结果只进 `data/03_extracted/`。
4. 样本融合结果只进 `data/04_merged/`。
5. 清洗校验结果只进 `data/05_cleaned/`。
6. 对外交付结果只进 `outputs/` 或 `data/06_exports/`。
7. 结构、材料、工艺标准化规则只进 `mappings/`。
8. schema 只进 `schemas/`。
9. 审核队列只进 `reviews/`。
10. 规范文档只进 `docs/`。

## 6. 验收标准

本次目录骨架任务完成时，必须满足：

1. 所有批准目录均已创建。
2. 根目录不出现临时命名目录。
3. 新建目录全部为 ASCII 命名。
4. spec 与 plan 文档存在并可读取。
5. 目录结构可通过脚本存在性校验。

## 7. 本次任务边界结论

本次最短路径实现为：

1. 保留现有 4 篇根目录 Markdown 不动。
2. 新建标准目录骨架。
3. 写入 design 和 implementation plan。
4. 用脚本校验目录完整性。

这条路径满足“先规划、再落目录、保证流程规范性”的目标，同时不引入额外实现范围。
