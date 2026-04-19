# Schema And Mapping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为点阵吸能文献数据库项目创建 `samples schema`、`evidence schema` 和三张标准化 mapping 表的首个正式版本。

**Architecture:** 产物拆成五个职责明确的文件：两个 JSON Schema 负责定义主记录与证据记录契约，三张 CSV 负责结构、材料、工艺的受控映射规则。验证分两层执行：先校验 JSON/CSV 文件本身可解析，再校验关键列、枚举与唯一性约束。

**Tech Stack:** JSON Schema Draft 2020-12, CSV, PowerShell

---

### Task 1: 创建 `samples schema v1`

**Files:**
- Create: `schemas/samples/schema_v1.json`
- Test: `schemas/samples/schema_v1.json`

- [ ] **Step 1: 写入 `samples schema v1`**

Write:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "schemas/samples/schema_v1.json",
  "title": "Lattice Sample Schema v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "paper_id",
    "sample_id",
    "structure_main_class",
    "structure_subtype_list",
    "needs_manual_review",
    "review_status"
  ],
  "properties": {
    "paper_id": { "type": "string", "minLength": 1 },
    "sample_id": { "type": "string", "minLength": 1 },
    "doi": { "type": ["string", "null"] },
    "title": { "type": ["string", "null"] },
    "sample_label_in_paper": { "type": ["string", "null"] },
    "is_multi_sample_paper": { "type": ["boolean", "null"] },

    "raw_design": { "type": ["string", "null"] },
    "raw_structure": { "type": ["string", "null"] },
    "raw_type": { "type": ["string", "null"] },
    "structure_main_class": {
      "type": "string",
      "enum": [
        "truss_lattice",
        "tpms",
        "honeycomb_2d",
        "plate_lattice",
        "tube_lattice",
        "hybrid_lattice",
        "bioinspired",
        "voronoi",
        "unknown"
      ]
    },
    "structure_subtype_list": {
      "type": "array",
      "items": { "type": "string" }
    },
    "is_hierarchical": { "type": ["boolean", "null"] },
    "is_graded": { "type": ["boolean", "null"] },
    "is_optimized": { "type": ["boolean", "null"] },
    "relative_density_raw": { "type": ["string", "null"] },
    "relative_density_value": { "type": ["number", "null"] },

    "raw_material": { "type": ["string", "null"] },
    "raw_material_group": { "type": ["string", "null"] },
    "material_canonical": { "type": ["string", "null"] },
    "material_family": {
      "type": "string",
      "enum": [
        "aluminum_alloy",
        "stainless_steel",
        "titanium_alloy",
        "polymer",
        "resin",
        "ni_ti_shape_memory",
        "magnesium_alloy",
        "steel",
        "composite_polymer",
        "unknown"
      ]
    },
    "raw_process": { "type": ["string", "null"] },
    "process_canonical": { "type": ["string", "null"] },
    "process_family": {
      "type": "string",
      "enum": [
        "slm",
        "sls",
        "sla",
        "fdm",
        "forming_and_assembly",
        "unknown"
      ]
    },

    "analysis_type": {
      "type": "string",
      "enum": [
        "experimental",
        "numerical",
        "experimental_numerical",
        "unknown"
      ]
    },
    "test_mode": {
      "type": "string",
      "enum": [
        "quasi_static",
        "impact",
        "dynamic",
        "unknown"
      ]
    },
    "loading_direction": {
      "type": "string",
      "enum": [
        "uniaxial",
        "biaxial",
        "lateral",
        "concentrated_load",
        "unknown"
      ]
    },
    "velocity_m_s_raw": { "type": ["string", "null"] },
    "velocity_m_s": { "type": ["number", "null"] },
    "sea_j_g_raw": { "type": ["string", "null"] },
    "sea_j_g": { "type": ["number", "null"] },
    "pcf_kn_raw": { "type": ["string", "null"] },
    "pcf_kn": { "type": ["number", "null"] },
    "mcf_kn_raw": { "type": ["string", "null"] },
    "mcf_kn": { "type": ["number", "null"] },
    "cfe_raw": { "type": ["string", "null"] },
    "cfe": { "type": ["number", "null"] },
    "plateau_stress_mpa_raw": { "type": ["string", "null"] },
    "plateau_stress_mpa": { "type": ["number", "null"] },

    "confidence_overall": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 1
    },
    "needs_manual_review": { "type": "boolean" },
    "review_status": {
      "type": "string",
      "enum": [
        "pending",
        "reviewed",
        "accepted",
        "rejected"
      ]
    },
    "review_notes": { "type": ["string", "null"] }
  }
}
```

- [ ] **Step 2: 解析 `samples schema v1`，确认 JSON 合法**

Run:

```powershell
Get-Content 'schemas\samples\schema_v1.json' -Raw -Encoding UTF8 | ConvertFrom-Json | Out-Null
```

Expected: 命令退出码为 `0`，没有 JSON 解析错误。

- [ ] **Step 3: 校验 `samples schema v1` 的关键字段存在**

Run:

```powershell
$schema = Get-Content 'schemas\samples\schema_v1.json' -Raw -Encoding UTF8 | ConvertFrom-Json
$required = @('paper_id','sample_id','structure_main_class','structure_subtype_list','needs_manual_review','review_status')
$missing = $required | Where-Object { $_ -notin $schema.required }
if ($missing.Count -gt 0) { throw ('Missing required keys: ' + ($missing -join ', ')) }
'OK'
```

Expected: 输出 `OK`。

### Task 2: 创建 `evidence schema v1`

**Files:**
- Create: `schemas/evidence/schema_v1.json`
- Test: `schemas/evidence/schema_v1.json`

- [ ] **Step 1: 写入 `evidence schema v1`**

Write:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "schemas/evidence/schema_v1.json",
  "title": "Lattice Evidence Schema v1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "evidence_id",
    "sample_id",
    "field_name",
    "source_priority",
    "source_type",
    "verified_by_human"
  ],
  "properties": {
    "evidence_id": { "type": "string", "minLength": 1 },
    "sample_id": { "type": "string", "minLength": 1 },
    "field_name": { "type": "string", "minLength": 1 },
    "field_value": { "type": ["string", "null"] },
    "source_priority": {
      "type": "string",
      "enum": ["T1", "T2", "T3", "manual"]
    },
    "source_type": {
      "type": "string",
      "enum": ["text", "table", "figure", "derived", "manual"]
    },
    "page_no": {
      "type": ["integer", "null"],
      "minimum": 1
    },
    "figure_id": { "type": ["string", "null"] },
    "table_id": { "type": ["string", "null"] },
    "text_snippet": { "type": ["string", "null"] },
    "extractor": { "type": ["string", "null"] },
    "extract_confidence": {
      "type": ["number", "null"],
      "minimum": 0,
      "maximum": 1
    },
    "verified_by_human": { "type": "boolean" }
  }
}
```

- [ ] **Step 2: 解析 `evidence schema v1`，确认 JSON 合法**

Run:

```powershell
Get-Content 'schemas\evidence\schema_v1.json' -Raw -Encoding UTF8 | ConvertFrom-Json | Out-Null
```

Expected: 命令退出码为 `0`，没有 JSON 解析错误。

- [ ] **Step 3: 校验 `source_priority` 与 `source_type` 枚举**

Run:

```powershell
$schema = Get-Content 'schemas\evidence\schema_v1.json' -Raw -Encoding UTF8 | ConvertFrom-Json
$priority = $schema.properties.source_priority.enum
$sourceType = $schema.properties.source_type.enum
if (('T1','T2','T3','manual' | Where-Object { $_ -notin $priority }).Count -gt 0) { throw 'Bad source_priority enum' }
if (('text','table','figure','derived','manual' | Where-Object { $_ -notin $sourceType }).Count -gt 0) { throw 'Bad source_type enum' }
'OK'
```

Expected: 输出 `OK`。

### Task 3: 创建 `structure_mapping.csv`

**Files:**
- Create: `mappings/structure/structure_mapping.csv`
- Test: `mappings/structure/structure_mapping.csv`

- [ ] **Step 1: 写入 `structure_mapping.csv`**

Write:

```csv
raw_design,raw_structure,raw_type,structure_main_class,structure_subtype_list_json,is_hierarchical,is_graded,mapping_notes
Gyroid,,TPMS,tpms,"[""gyroid""]",false,false,
Diamond,,TPMS,tpms,"[""diamond""]",false,false,
,BCC,Truss,truss_lattice,"[""bcc""]",false,false,
,BCCZ,Truss,truss_lattice,"[""bccz""]",false,false,
,Octet,Truss,truss_lattice,"[""octet""]",false,false,
,Hexagonal,General 2D,honeycomb_2d,"[""hexagonal""]",false,false,
,Re-entrant,General 2D,honeycomb_2d,"[""reentrant""]",false,false,
Bioinspired,,Bioinspired,bioinspired,[],false,false,canonical spelling
```

- [ ] **Step 2: 导入 `structure_mapping.csv`，确认列头正确**

Run:

```powershell
$rows = Import-Csv 'mappings\structure\structure_mapping.csv'
$expected = @('raw_design','raw_structure','raw_type','structure_main_class','structure_subtype_list_json','is_hierarchical','is_graded','mapping_notes')
$actual = ($rows | Select-Object -First 1 | Get-Member -MemberType NoteProperty).Name
$missing = $expected | Where-Object { $_ -notin $actual }
if ($missing.Count -gt 0) { throw ('Missing columns: ' + ($missing -join ', ')) }
'OK'
```

Expected: 输出 `OK`。

- [ ] **Step 3: 校验联合唯一键不重复**

Run:

```powershell
$rows = Import-Csv 'mappings\structure\structure_mapping.csv'
$dups = $rows |
  Group-Object {
    (($_.raw_design).Trim().ToLowerInvariant()) + '|' +
    (($_.raw_structure).Trim().ToLowerInvariant()) + '|' +
    (($_.raw_type).Trim().ToLowerInvariant())
  } |
  Where-Object { $_.Count -gt 1 }
if ($dups.Count -gt 0) { throw 'Duplicate structure mapping keys found' }
'OK'
```

Expected: 输出 `OK`。

### Task 4: 创建 `material_mapping.csv` 与 `process_mapping.csv`

**Files:**
- Create: `mappings/material/material_mapping.csv`
- Create: `mappings/process/process_mapping.csv`
- Test: `mappings/material/material_mapping.csv`
- Test: `mappings/process/process_mapping.csv`

- [ ] **Step 1: 写入 `material_mapping.csv`**

Write:

```csv
raw_material,material_canonical,material_family,mapping_notes
Aluminium,Aluminum,aluminum_alloy,UK spelling
Aluminum,Aluminum,aluminum_alloy,US spelling
316L,316L,stainless_steel,
304L,304L,stainless_steel,
304 SS,304 SS,stainless_steel,
Ti-6Al-4V,Ti-6Al-4V,titanium_alloy,
Ti–6Al–4V,Ti-6Al-4V,titanium_alloy,unicode hyphen normalized
Nylon 12,PA12,polymer,
Nylon-12,PA12,polymer,
PA12,PA12,polymer,
PA-12,PA12,polymer,
Polyamide 12,PA12,polymer,
```

- [ ] **Step 2: 写入 `process_mapping.csv`**

Write:

```csv
raw_process,process_canonical,process_family,mapping_notes
SLM,SLM,slm,
SLS,SLS,sls,
SLA,SLA,sla,
FDM,FDM,fdm,
Forming and assembly,Forming and Assembly,forming_and_assembly,canonical spacing and casing
```

- [ ] **Step 3: 导入两张 CSV 并校验列头**

Run:

```powershell
$material = Import-Csv 'mappings\material\material_mapping.csv'
$process = Import-Csv 'mappings\process\process_mapping.csv'
$materialExpected = @('raw_material','material_canonical','material_family','mapping_notes')
$processExpected = @('raw_process','process_canonical','process_family','mapping_notes')
$materialActual = ($material | Select-Object -First 1 | Get-Member -MemberType NoteProperty).Name
$processActual = ($process | Select-Object -First 1 | Get-Member -MemberType NoteProperty).Name
if (($materialExpected | Where-Object { $_ -notin $materialActual }).Count -gt 0) { throw 'Bad material mapping header' }
if (($processExpected | Where-Object { $_ -notin $processActual }).Count -gt 0) { throw 'Bad process mapping header' }
'OK'
```

Expected: 输出 `OK`。

- [ ] **Step 4: 校验材料与工艺映射主键不重复**

Run:

```powershell
$materialDup = Import-Csv 'mappings\material\material_mapping.csv' |
  Group-Object { ($_.raw_material).Trim().ToLowerInvariant() } |
  Where-Object { $_.Count -gt 1 }
$processDup = Import-Csv 'mappings\process\process_mapping.csv' |
  Group-Object { ($_.raw_process).Trim().ToLowerInvariant() } |
  Where-Object { $_.Count -gt 1 }
if ($materialDup.Count -gt 0) { throw 'Duplicate material mapping keys found' }
if ($processDup.Count -gt 0) { throw 'Duplicate process mapping keys found' }
'OK'
```

Expected: 输出 `OK`。

### Task 5: 执行整体验证并锁定产物一致性

**Files:**
- Test: `schemas/samples/schema_v1.json`
- Test: `schemas/evidence/schema_v1.json`
- Test: `mappings/structure/structure_mapping.csv`
- Test: `mappings/material/material_mapping.csv`
- Test: `mappings/process/process_mapping.csv`

- [ ] **Step 1: 全量解析所有新文件**

Run:

```powershell
Get-Content 'schemas\samples\schema_v1.json' -Raw -Encoding UTF8 | ConvertFrom-Json | Out-Null
Get-Content 'schemas\evidence\schema_v1.json' -Raw -Encoding UTF8 | ConvertFrom-Json | Out-Null
Import-Csv 'mappings\structure\structure_mapping.csv' | Out-Null
Import-Csv 'mappings\material\material_mapping.csv' | Out-Null
Import-Csv 'mappings\process\process_mapping.csv' | Out-Null
'OK'
```

Expected: 输出 `OK`。

- [ ] **Step 2: 交叉检查 schema 和 mapping 的闭集值一致**

Run:

```powershell
$samples = Get-Content 'schemas\samples\schema_v1.json' -Raw -Encoding UTF8 | ConvertFrom-Json
$structureAllowed = $samples.properties.structure_main_class.enum
$materialAllowed = $samples.properties.material_family.enum
$processAllowed = $samples.properties.process_family.enum
$structureBad = Import-Csv 'mappings\structure\structure_mapping.csv' | Where-Object { $_.structure_main_class -notin $structureAllowed }
$materialBad = Import-Csv 'mappings\material\material_mapping.csv' | Where-Object { $_.material_family -notin $materialAllowed }
$processBad = Import-Csv 'mappings\process\process_mapping.csv' | Where-Object { $_.process_family -notin $processAllowed }
if ($structureBad.Count -gt 0) { throw 'Structure mapping contains out-of-schema values' }
if ($materialBad.Count -gt 0) { throw 'Material mapping contains out-of-schema values' }
if ($processBad.Count -gt 0) { throw 'Process mapping contains out-of-schema values' }
'OK'
```

Expected: 输出 `OK`。

- [ ] **Step 3: 输出文件清单供人工复核**

Run:

```powershell
Get-ChildItem 'schemas\samples'
Get-ChildItem 'schemas\evidence'
Get-ChildItem 'mappings\structure'
Get-ChildItem 'mappings\material'
Get-ChildItem 'mappings\process'
```

Expected: 五个目标文件全部存在。
