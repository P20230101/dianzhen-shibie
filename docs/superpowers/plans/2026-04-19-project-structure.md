# 点阵数据库目录骨架 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为点阵吸能文献数据库项目建立统一、可扩展、可审计的目录骨架，并保存与该骨架对应的设计说明和实施计划。

**Architecture:** 项目按“规范资产、数据生命周期、标准化资产、脚本职责、人工复核、最终导出”六类边界组织目录。目录按流程职责划分，不按当前工具名划分，以保证后续 schema、mapping、脚本和 review 队列都有稳定落点。

**Tech Stack:** Windows PowerShell, Markdown, 本地文件系统

---

### Task 1: 建立规划文档目录并写入设计文档

**Files:**
- Create: `docs/superpowers/specs/`
- Create: `docs/superpowers/plans/`
- Create: `docs/superpowers/specs/2026-04-19-project-structure-design.md`
- Create: `docs/superpowers/plans/2026-04-19-project-structure.md`

- [ ] **Step 1: 创建规划文档目录**

Run:

```powershell
$dirs = @(
  'docs\superpowers\specs',
  'docs\superpowers\plans'
)
foreach ($dir in $dirs) {
  New-Item -Path (Join-Path $PWD $dir) -ItemType Directory -Force | Out-Null
}
```

Expected: `docs\superpowers\specs` 和 `docs\superpowers\plans` 均存在。

- [ ] **Step 2: 写入目录骨架设计文档**

Write:

```md
# 点阵吸能文献数据库目录骨架设计

## 1. 目标
## 2. 设计原则
## 3. 目录方案
## 4. 目录职责定义
## 5. 流程规范
## 6. 验收标准
## 7. 本次任务边界结论
```

Expected: 设计文档清楚定义目录边界、职责、规范和验收标准。

- [ ] **Step 3: 写入实施计划文档**

Write:

```md
# 点阵数据库目录骨架 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: ...

**Goal:** ...
**Architecture:** ...
**Tech Stack:** ...
```

Expected: 计划文档包含完整任务、步骤、命令和预期结果。

- [ ] **Step 4: 验证规划文档可读取**

Run:

```powershell
Get-Content 'docs\superpowers\specs\2026-04-19-project-structure-design.md' -TotalCount 10
Get-Content 'docs\superpowers\plans\2026-04-19-project-structure.md' -TotalCount 10
```

Expected: 两份文档都能正常读取，标题和首部段落正确输出。

### Task 2: 创建规范与数据生命周期目录

**Files:**
- Create: `docs/01_scope/`
- Create: `docs/02_schema/`
- Create: `docs/03_workflow/`
- Create: `docs/04_review/`
- Create: `data/01_raw/pdfs/`
- Create: `data/01_raw/excel/`
- Create: `data/02_parsed/`
- Create: `data/03_extracted/`
- Create: `data/04_merged/`
- Create: `data/05_cleaned/`
- Create: `data/06_exports/`

- [ ] **Step 1: 创建规范目录**

Run:

```powershell
$dirs = @(
  'docs\01_scope',
  'docs\02_schema',
  'docs\03_workflow',
  'docs\04_review'
)
foreach ($dir in $dirs) {
  New-Item -Path (Join-Path $PWD $dir) -ItemType Directory -Force | Out-Null
}
```

Expected: `docs` 下出现 4 个按职责划分的规范目录。

- [ ] **Step 2: 创建原始数据目录**

Run:

```powershell
$dirs = @(
  'data\01_raw\pdfs',
  'data\01_raw\excel'
)
foreach ($dir in $dirs) {
  New-Item -Path (Join-Path $PWD $dir) -ItemType Directory -Force | Out-Null
}
```

Expected: `data\01_raw\pdfs` 和 `data\01_raw\excel` 存在。

- [ ] **Step 3: 创建中间层与清洗层目录**

Run:

```powershell
$dirs = @(
  'data\02_parsed',
  'data\03_extracted',
  'data\04_merged',
  'data\05_cleaned',
  'data\06_exports'
)
foreach ($dir in $dirs) {
  New-Item -Path (Join-Path $PWD $dir) -ItemType Directory -Force | Out-Null
}
```

Expected: `data` 生命周期目录完整存在。

- [ ] **Step 4: 验证 `docs` 和 `data` 根目录结构**

Run:

```powershell
Get-ChildItem 'docs' -Directory | Select-Object Name
Get-ChildItem 'data' -Recurse -Directory | Select-Object FullName
```

Expected: 输出与设计文档中的目录骨架一致。

### Task 3: 创建映射、schema、脚本、复核与导出目录

**Files:**
- Create: `mappings/structure/`
- Create: `mappings/material/`
- Create: `mappings/process/`
- Create: `schemas/samples/`
- Create: `schemas/evidence/`
- Create: `scripts/ingest/`
- Create: `scripts/extract/`
- Create: `scripts/merge/`
- Create: `scripts/validate/`
- Create: `scripts/export/`
- Create: `reviews/pending/`
- Create: `reviews/done/`
- Create: `outputs/json/`
- Create: `outputs/csv/`
- Create: `outputs/xlsx/`
- Create: `archive/`

- [ ] **Step 1: 创建标准化映射目录**

Run:

```powershell
$dirs = @(
  'mappings\structure',
  'mappings\material',
  'mappings\process'
)
foreach ($dir in $dirs) {
  New-Item -Path (Join-Path $PWD $dir) -ItemType Directory -Force | Out-Null
}
```

Expected: `mappings` 下出现结构、材料、工艺三个子目录。

- [ ] **Step 2: 创建 schema 目录**

Run:

```powershell
$dirs = @(
  'schemas\samples',
  'schemas\evidence'
)
foreach ($dir in $dirs) {
  New-Item -Path (Join-Path $PWD $dir) -ItemType Directory -Force | Out-Null
}
```

Expected: `schemas\samples` 和 `schemas\evidence` 存在。

- [ ] **Step 3: 创建脚本职责目录**

Run:

```powershell
$dirs = @(
  'scripts\ingest',
  'scripts\extract',
  'scripts\merge',
  'scripts\validate',
  'scripts\export'
)
foreach ($dir in $dirs) {
  New-Item -Path (Join-Path $PWD $dir) -ItemType Directory -Force | Out-Null
}
```

Expected: `scripts` 下出现 5 个按职责划分的目录。

- [ ] **Step 4: 创建复核、输出和归档目录**

Run:

```powershell
$dirs = @(
  'reviews\pending',
  'reviews\done',
  'outputs\json',
  'outputs\csv',
  'outputs\xlsx',
  'archive'
)
foreach ($dir in $dirs) {
  New-Item -Path (Join-Path $PWD $dir) -ItemType Directory -Force | Out-Null
}
```

Expected: `reviews`、`outputs`、`archive` 目录均存在。

### Task 4: 进行完整性校验并锁定验收标准

**Files:**
- Test: `docs/superpowers/specs/2026-04-19-project-structure-design.md`
- Test: `docs/superpowers/plans/2026-04-19-project-structure.md`
- Test: 整体目录骨架

- [ ] **Step 1: 执行目录存在性校验**

Run:

```powershell
$required = @(
  'docs',
  'docs\01_scope',
  'docs\02_schema',
  'docs\03_workflow',
  'docs\04_review',
  'docs\superpowers\specs',
  'docs\superpowers\plans',
  'data',
  'data\01_raw',
  'data\01_raw\pdfs',
  'data\01_raw\excel',
  'data\02_parsed',
  'data\03_extracted',
  'data\04_merged',
  'data\05_cleaned',
  'data\06_exports',
  'mappings',
  'mappings\structure',
  'mappings\material',
  'mappings\process',
  'schemas',
  'schemas\samples',
  'schemas\evidence',
  'scripts',
  'scripts\ingest',
  'scripts\extract',
  'scripts\merge',
  'scripts\validate',
  'scripts\export',
  'reviews',
  'reviews\pending',
  'reviews\done',
  'outputs',
  'outputs\json',
  'outputs\csv',
  'outputs\xlsx',
  'archive'
)
$missing = $required | Where-Object { -not (Test-Path (Join-Path $PWD $_)) }
if ($missing.Count -gt 0) {
  throw ('Missing directories: ' + ($missing -join ', '))
}
'OK'
```

Expected: 输出 `OK`，没有缺失目录。

- [ ] **Step 2: 输出目录快照供人工复核**

Run:

```powershell
Get-ChildItem -Directory
Get-ChildItem 'docs' -Recurse -Directory | Select-Object FullName
Get-ChildItem 'data' -Recurse -Directory | Select-Object FullName
```

Expected: 目录快照与设计文档一致，根目录没有新增无关目录。

- [ ] **Step 3: 对照设计文档执行自检**

Checklist:

```text
1. 所有目录命名均为 ASCII
2. 目录边界按流程职责划分
3. 本次未创建空模板文件
4. 现有 4 篇 Markdown 未被移动或覆盖
5. spec 与 plan 已保存
```

Expected: 5 项全部满足。
