# Project Roadmap Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `dianzhen shujuku` 落地长期项目总览、阶段路线、分支策略视图，并把长期任务记忆与这些仓库内入口对齐，服务 `2026-04-21` 的 `M0 可控开发启动验收`。

**Architecture:** 本轮只实现治理与可视化入口，不碰业务功能。仓库内新增三份 `tasks/` 总览文档，分别回答“项目在做什么”“项目接下来怎么走”“任务怎么拆支线”；同时复用已存在的 `.codex-memory` 长期任务骨架，对齐简报与引用索引，最后做跨文档一致性验证，确保仓库内入口与长期任务记忆相互指向且不冲突。

**Tech Stack:** Markdown, Git, PowerShell

---

### Task 1: 新增项目总览入口

**Files:**
- Create: `tasks/project-overview.md`
- Test: overview scope, milestone, deliverables, next actions

- [ ] **Step 1: 写入 `tasks/project-overview.md`**

Write:

```md
# Project Overview

## One-Sentence Goal

Build a controlled lattice crashworthiness literature database that turns paper evidence into normalized sample-level data.

## Current Phase

- `P0 / M0: 可控开发启动阶段`
- `Nearest Milestone: 2026-04-21 | M0 可控开发启动验收`

## What The Project Is Doing Now

- Stabilizing the repository structure and dispatch workflow
- Locking the sample/evidence schema and mapping contract
- Preparing the first executable development packages and branch policy

## In Scope Now

- Repository governance and dispatch workflow
- Schema and mapping contract
- Task decomposition and branch policy
- Acceptance-ready project overview materials

## Not In Scope Now

- Full paper ingestion pipeline
- Full extraction automation
- Full review tooling
- Final UI or complete product shell

## Current Deliverables

- `schemas/samples/schema_v1.json`
- `schemas/evidence/schema_v1.json`
- `mappings/structure/structure_mapping.csv`
- `mappings/material/material_mapping.csv`
- `mappings/process/process_mapping.csv`
- `tasks/workflow.md`
- `tasks/rules.md`
- `tasks/templates/task-template.md`

## Next Actions

1. Prepare the first real execution branch for `P1`.
2. Keep long-term roadmap and branch strategy on `dispatch/tasks`.
3. Use `rebase --onto` or `cherry-pick` for code integration to `main`.
```

Expected: `project-overview.md` 在第一屏就能回答项目目标、当前阶段、最近里程碑、当前范围和下一步动作。

- [ ] **Step 2: 验证总览入口字段**

Run:

```powershell
Select-String -Path 'tasks\project-overview.md' -Pattern 'One-Sentence Goal','P0 / M0','2026-04-21','In Scope Now','Not In Scope Now','Current Deliverables','Next Actions'
```

Expected: 不报错，且输出命中总览必需段落。

- [ ] **Step 3: 提交项目总览入口**

Run:

```powershell
git add tasks/project-overview.md
git commit -m "docs: add project overview entry"
```

Expected: 出现一条只包含 `tasks/project-overview.md` 的提交。

### Task 2: 新增阶段路线图

**Files:**
- Create: `tasks/roadmap.md`
- Test: phase structure, current phase marker, milestone definition

- [ ] **Step 1: 写入 `tasks/roadmap.md`**

Write:

```md
# Project Roadmap

## Current Position

- `NOW: P0 / M0`
- `Milestone Date: 2026-04-21`
- `Milestone Name: M0 可控开发启动验收`

| Phase | Goal | What Must Be Ready | Exit Signal | Branch Policy |
|---|---|---|---|---|
| `P0 / M0` | Establish controllable development state | dispatch workflow, schema/mapping contract, overview docs, branch policy | `2026-04-21` M0 accepted | Governance stays on `dispatch/tasks` |
| `P1` | Run the first minimal end-to-end chain | input entry, parsed layer, extracted output, sample/evidence alignment, minimal review/export path | first real task runs through one execution branch | Same execution branch |
| `P2` | Expand capabilities in parallel | stable interfaces from `P1` | modular work packages can run without conflicting writes | New execution branches allowed by package |
| `P3` | Integrate and package deliverables | stabilized outputs from `P2` | integration-ready deliverable set | Isolated integration branch |

## Phase Priorities

### `P0 / M0`
- Project goal and boundary are clear
- Dispatch workflow is operational
- Schema and mapping contract are stable enough for execution planning
- Next execution packages are visible

### `P1`
- First minimal chain is runnable
- Core interfaces are no longer drifting

### `P2`
- Input adapters, extraction modules, review helpers, and export outputs can split safely

### `P3`
- Parallel outputs are collected into a stable delivery set
```

Expected: `roadmap.md` 明确展示当前阶段、四段路线、每阶段目标、退出信号和分支政策。

- [ ] **Step 2: 验证路线图关键结构**

Run:

```powershell
Select-String -Path 'tasks\roadmap.md' -Pattern 'Current Position','NOW: P0 / M0','2026-04-21','P0 / M0','P1','P2','P3','Branch Policy','Phase Priorities'
```

Expected: 不报错，且输出命中阶段路线与当前位置字段。

- [ ] **Step 3: 提交阶段路线图**

Run:

```powershell
git add tasks/roadmap.md
git commit -m "docs: add project roadmap view"
```

Expected: 出现一条只包含 `tasks/roadmap.md` 的提交。

### Task 3: 新增分支策略视图

**Files:**
- Create: `tasks/branch-strategy.md`
- Test: dispatch-only, same-branch, split-later rules

- [ ] **Step 1: 写入 `tasks/branch-strategy.md`**

Write:

```md
# Branch Strategy

## Reading Guide

- `留在 dispatch/tasks` = dispatch-only asset, do not open an execution branch
- `同支线推进` = keep the package in one execution branch until the package is stable
- `可新开支线` = open a new execution branch only after the package-specific preconditions are satisfied

## Current Branch Classes

| Classification | Work Package | Current Rule | Suggested Branch Pattern |
|---|---|---|---|
| `留在 dispatch/tasks` | Project overview, roadmap, branch policy, board, branch map, workflow, templates, rules | Maintain only on `dispatch/tasks` | `N/A` |
| `同支线推进` | Data contract bundle (`schemas/`, `mappings/`, validation boundary) | Keep in one execution branch until the contract is stable | `feat/task-xxx-data-contract` |
| `同支线推进` | First minimal end-to-end chain | Keep in one execution branch until the first chain is truly runnable | `feat/task-xxx-min-pipeline` |
| `可新开支线` | Input adapters | Allowed only after `P1` interfaces are stable | `feat/task-xxx-input-<topic>` |
| `可新开支线` | Extraction enhancements | Allowed only after sample/evidence interfaces are stable | `feat/task-xxx-extract-<topic>` |
| `可新开支线` | Review / cleaning helpers | Allowed only after the review boundary is stable | `feat/task-xxx-review-<topic>` |
| `可新开支线` | Export / delivery outputs | Allowed only after the output contract is stable | `feat/task-xxx-export-<topic>` |

## Do Not Split Yet

- Any work that changes `schemas/` and `mappings/` together
- Any work that defines the first real sample/evidence flow
- Any work whose acceptance criteria are still shared by multiple packages

## Can Split Later Only If

1. The input and output contract is stable.
2. The write set is not shared.
3. The acceptance boundary is independent.

## Recommended Next Execution Package

- `P1 first minimal chain`
- `Suggested first branch: feat/task-xxx-min-pipeline`
- `Package scope: input entry, parsed layer, extracted output, sample/evidence alignment, minimal review/export closure`
```

Expected: `branch-strategy.md` 能一眼区分“留在 dispatch/tasks / 同支线推进 / 可新开支线”，并给出下一条推荐执行包。

- [ ] **Step 2: 验证分支策略标记**

Run:

```powershell
Select-String -Path 'tasks\branch-strategy.md' -Pattern 'Reading Guide','留在 dispatch/tasks','同支线推进','可新开支线','Current Branch Classes','Do Not Split Yet','Can Split Later Only If','Recommended Next Execution Package'
```

Expected: 不报错，且输出命中三类分支规则和推荐执行包。

- [ ] **Step 3: 提交分支策略视图**

Run:

```powershell
git add tasks/branch-strategy.md
git commit -m "docs: add branch strategy view"
```

Expected: 出现一条只包含 `tasks/branch-strategy.md` 的提交。

### Task 4: 对齐长期任务记忆与仓库入口

**Files:**
- Modify: `.codex-memory/tasks/index.md`
- Modify: `.codex-memory/tasks/active/lattice-db-product-roadmap/brief.md`
- Modify: `.codex-memory/tasks/active/lattice-db-product-roadmap/refs.md`
- Test: memory links to repository entry files

- [ ] **Step 1: 重写 `.codex-memory/tasks/index.md`**

Write:

```md
# 任务索引

- `lattice-db-product-roadmap`：`dianzhen shujuku` 项目的长期产品路线、研发路线、`2026-04-21` M0 验收与分支治理任务。
```

Expected: 任务索引能够一句话指向该长期任务的治理范围。

- [ ] **Step 2: 重写 `brief.md`**

Write:

```md
<!-- codex-memory:template=task-brief:v1 -->

# 任务简报
## 目标

- 建立 `dianzhen shujuku` 项目的长期产品路线与研发路线治理入口。
- 将 `2026-04-21` 定义为 `M0 可控开发启动验收`。
- 让后续开发能一眼看清：项目在做什么、当前阶段是什么、哪些任务可新开支线、哪些任务必须同支线推进。

## 范围 / 不做

- 做：
  - 长期目标
  - 阶段路线
  - 明天验收视图
  - 分支拆分策略
  - 长期任务记忆
- 不做：
  - 业务功能实现
  - 自动化脚本
  - UI
  - 全量数据导入

## 当前状态
- 已完成：
  - 项目目录骨架
  - schema / mapping v1
  - `dispatch/tasks` 调度体系
  - 任务启动规范
  - `tasks/project-overview.md`
  - `tasks/roadmap.md`
  - `tasks/branch-strategy.md`
- 进行中：
  - 首条真实任务的执行编排准备
- 未开始：
  - 首条真实任务按新规范跑通

## 已确认决定
- 详见 `decisions.md`

## 关键索引

- 详见 `refs.md`

## 风险 / 下一步
- 风险：
  - 首次真实任务尚未按新规范跑通
  - `2026-04-21` 验收以后仍需用真实任务验证可操作性
- 下一步：
  - 选择第一条真实执行任务
  - 从 `dispatch/tasks` 切出第一条 `P1` 执行支线
  - 用真实任务验证总览、路线与分支策略是否可用
```

Expected: `brief.md` 与仓库内入口文件同步，反映当前阶段目标和下一步。

- [ ] **Step 3: 重写 `refs.md`**

Write:

```md
<!-- codex-memory:template=task-refs:v1 -->

# 关键引用

只保留这个任务后续还会继续用到的关键索引。
## 引用

- 主画板：
  - `tasks/project-overview.md`
  - `tasks/roadmap.md`
  - `tasks/branch-strategy.md`
  - `tasks/board.md`
  - `tasks/branches.md`
- 主节点：
  - `tasks/workflow.md`
  - `tasks/rules.md`
  - `tasks/templates/task-template.md`
- 公共组件来源：
  - `schemas/samples/schema_v1.json`
  - `schemas/evidence/schema_v1.json`
  - `mappings/structure/structure_mapping.csv`
  - `mappings/material/material_mapping.csv`
  - `mappings/process/process_mapping.csv`
- 素材路径：
  - `Lattice crashworthiness data.xlsx`
  - 根目录四份项目说明 Markdown
- 其他关键引用：
  - `docs/superpowers/specs/2026-04-19-project-structure-design.md`
  - `docs/superpowers/specs/2026-04-19-schema-mapping-design.md`
  - `docs/superpowers/specs/2026-04-19-dispatch-branch-design.md`
  - `docs/superpowers/specs/2026-04-19-dispatch-task-startup-design.md`
  - `docs/superpowers/specs/2026-04-20-project-roadmap-governance-design.md`
```

Expected: 长期任务记忆直接索引到新增的仓库内总览入口。

- [ ] **Step 4: 验证长期任务记忆对齐**

Run:

```powershell
Select-String -Path '.codex-memory\tasks\index.md' -Pattern 'lattice-db-product-roadmap','M0'
Select-String -Path '.codex-memory\tasks\active\lattice-db-product-roadmap\brief.md' -Pattern 'tasks/project-overview.md','tasks/roadmap.md','tasks/branch-strategy.md','M0 可控开发启动验收'
Select-String -Path '.codex-memory\tasks\active\lattice-db-product-roadmap\refs.md' -Pattern 'tasks/project-overview.md','tasks/roadmap.md','tasks/branch-strategy.md'
```

Expected: 不报错，且 memory 文档指向新增的仓库入口文件。

- [ ] **Step 5: 提交长期任务记忆对齐**

Run:

```powershell
git add .codex-memory/tasks/index.md .codex-memory/tasks/active/lattice-db-product-roadmap/brief.md .codex-memory/tasks/active/lattice-db-product-roadmap/refs.md
git commit -m "chore: align project roadmap task memory"
```

Expected: 出现一条只包含长期任务记忆对齐的提交。

### Task 5: 做最终跨文档验收

**Files:**
- Test: `tasks/project-overview.md`
- Test: `tasks/roadmap.md`
- Test: `tasks/branch-strategy.md`
- Test: `.codex-memory/tasks/index.md`
- Test: `.codex-memory/tasks/active/lattice-db-product-roadmap/brief.md`
- Test: `.codex-memory/tasks/active/lattice-db-product-roadmap/refs.md`
- Test: `tasks/workflow.md`
- Test: `tasks/board.md`
- Test: `tasks/branches.md`
- Test: `tasks/rules.md`

- [ ] **Step 1: 验证所有目标文件存在**

Run:

```powershell
$paths = @(
  'tasks\project-overview.md',
  'tasks\roadmap.md',
  'tasks\branch-strategy.md',
  '.codex-memory\tasks\index.md',
  '.codex-memory\tasks\active\lattice-db-product-roadmap\brief.md',
  '.codex-memory\tasks\active\lattice-db-product-roadmap\refs.md'
)
foreach ($path in $paths) {
  if (-not (Test-Path $path)) { throw "Missing file: $path" }
}
Write-Output 'OK: roadmap governance assets exist'
```

Expected: 输出 `OK: roadmap governance assets exist`。

- [ ] **Step 2: 做逐文件强校验**

Run:

```powershell
$patterns = @(
  @{Path='tasks/project-overview.md'; Needles=@('P0 / M0','2026-04-21','In Scope Now','Not In Scope Now','Next Actions')},
  @{Path='tasks/roadmap.md'; Needles=@('NOW: P0 / M0','M0 可控开发启动验收','P1','P2','P3','Branch Policy')},
  @{Path='tasks/branch-strategy.md'; Needles=@('留在 dispatch/tasks','同支线推进','可新开支线','Do Not Split Yet','Can Split Later Only If','feat/task-xxx-min-pipeline')},
  @{Path='.codex-memory/tasks/index.md'; Needles=@('lattice-db-product-roadmap','M0')},
  @{Path='.codex-memory/tasks/active/lattice-db-product-roadmap/brief.md'; Needles=@('M0 可控开发启动验收','tasks/project-overview.md','tasks/roadmap.md','tasks/branch-strategy.md')},
  @{Path='.codex-memory/tasks/active/lattice-db-product-roadmap/refs.md'; Needles=@('tasks/project-overview.md','tasks/roadmap.md','tasks/branch-strategy.md','tasks/workflow.md','tasks/rules.md')}
)
foreach ($item in $patterns) {
  foreach ($needle in $item.Needles) {
    $null = Select-String -Path $item.Path -SimpleMatch -Pattern $needle -ErrorAction Stop
  }
}
Write-Output 'OK: per-file governance verification passed'
```

Expected: 输出 `OK: per-file governance verification passed`。

- [ ] **Step 3: 验证 Git 状态与文本质量**

Run:

```powershell
git diff --check
git status --short --branch
git ls-files --eol -- tasks/project-overview.md tasks/roadmap.md tasks/branch-strategy.md
```

Expected: `git diff --check` 无输出；`git status --short --branch` 显示当前位于 `dispatch/tasks` 且工作区干净；3 个新增总览文件显示为 `w/lf`。

- [ ] **Step 4: 输出人工复核顺序**

Run:

```powershell
Get-Content 'tasks\project-overview.md'
Get-Content 'tasks\roadmap.md'
Get-Content 'tasks\branch-strategy.md'
Get-Content 'tasks\board.md'
Get-Content 'tasks\branches.md'
Get-Content 'tasks\workflow.md'
Get-Content '.codex-memory\tasks\active\lattice-db-product-roadmap\brief.md'
```

Expected: 可直接人工检查“项目在做什么 / 接下来怎么走 / 怎样拆分支线 / 当前调度状态 / 长期任务记忆入口”。
