# Dispatch Task Startup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `dispatch/tasks` 上落地任务启动规范，使每个正式任务都必须经过任务卡、看板、分支映射和归档闭环。

**Architecture:** 本轮只修改调度文档资产，不引入脚本。实现分成四块：先补齐 `workflow` 与任务卡模板，再规范 `board` 和 `branches`，随后补全 `rules`，最后做跨文档一致性验证，确保命名、状态和集成方式在所有入口中一致。

**Tech Stack:** Markdown, Git, PowerShell

---

### Task 1: 新增启动流程文档与任务卡模板

**Files:**
- Create: `tasks/workflow.md`
- Create: `tasks/templates/task-template.md`
- Create: `tasks/templates/`
- Test: startup document presence and required sections

- [ ] **Step 1: 创建模板目录**

Run:

```powershell
New-Item -Path (Join-Path $PWD 'tasks\templates') -ItemType Directory -Force | Out-Null
```

Expected: `tasks/templates/` 存在，可用于存放统一任务模板。

- [ ] **Step 2: 写入 `tasks/workflow.md`**

Write:

```md
# Dispatch Workflow

## 1. Start A Task
1. Assign the next `TASK-xxx`.
2. Create `tasks/assignments/TASK-xxx.md` from `tasks/templates/task-template.md`.
3. Add the task entry to `tasks/board.md` under `## To Do`.
4. Add the branch mapping row to `tasks/branches.md`.
5. Commit the dispatch record on `dispatch/tasks`.
6. Create the dev branch from `dispatch/tasks`.

A task is formally started only after steps 1-4 are complete.

## 2. Execute A Task
1. Switch to the dev branch.
2. Implement and test on the dev branch only.
3. When task status changes, update the task card and `tasks/board.md` on `dispatch/tasks`.
4. Keep `Integration Method` limited to `rebase --onto` or `cherry-pick`.

## 3. Finish A Task
1. Record verification evidence in the task card.
2. Move the board entry to `## Done`.
3. Move the task card from `tasks/assignments/` to `tasks/archive/`.
4. Keep the branch mapping row and mark `Status` as `Done`.

A task is formally done only after verification is recorded and the task card is archived.

## 4. Integration Reminder
- Do not merge `dispatch/tasks` directly into `main`.
- Do not merge a dev branch directly into `main` if it still carries dispatch history.
- Bring code to `main` with `rebase --onto` or `cherry-pick`.
```

Expected: `workflow.md` 固化启动、执行、完成三个阶段，并明确调度线与主线的边界。

- [ ] **Step 3: 写入 `tasks/templates/task-template.md`**

Write:

```md
# Task Card

- Task ID: `TASK-001`
- Title: `<one-line task title>`
- Goal: `<result only>`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-001-example-topic`
- Integration Method: `rebase --onto`
- Dependencies: `None`

## Acceptance Criteria
- `<result condition 1>`
- `<result condition 2>`

## Verification
- `<command or review evidence>`

## Status Log
- `YYYY-MM-DD HH:MM | Created on dispatch/tasks`
```

Expected: 任务卡模板同时覆盖任务标识、执行分支、集成方式、验收标准、验证证据和状态日志。

- [ ] **Step 4: 验证新文件存在且包含关键段落**

Run:

```powershell
$paths = @(
  'tasks\workflow.md',
  'tasks\templates\task-template.md'
)
foreach ($path in $paths) {
  if (-not (Test-Path $path)) { throw "Missing file: $path" }
}
Select-String -Path 'tasks\workflow.md' -Pattern 'Start A Task','Execute A Task','Finish A Task','rebase --onto','cherry-pick'
Select-String -Path 'tasks\templates\task-template.md' -Pattern 'Task ID','Dispatch Branch','Dev Branch','Integration Method','Acceptance Criteria','Verification','Status Log'
```

Expected: 不报错，且输出匹配到工作流阶段标题和任务卡关键字段。

- [ ] **Step 5: 提交新增文档**

Run:

```powershell
git add tasks/workflow.md tasks/templates/task-template.md
git commit -m "docs: add dispatch workflow and task template"
```

Expected: 出现一条只包含启动流程与任务卡模板的提交。

### Task 2: 规范任务看板与分支映射文档

**Files:**
- Modify: `tasks/board.md`
- Modify: `tasks/branches.md`
- Test: board and branch mapping format

- [ ] **Step 1: 重写 `tasks/board.md`**

Write:

```md
# Task Board

Entry format:
`- TASK-001 | <title> | <dev-branch>`

## To Do

## Doing

## Blocked

## Done
```

Expected: 看板保留四种状态，并明确单条任务在看板中的固定格式。

- [ ] **Step 2: 重写 `tasks/branches.md`**

Write:

```md
# Branch Mapping

Rules:
- One task per row.
- `Dispatch Branch` must stay `dispatch/tasks`.
- `Integration Method` must be `rebase --onto` or `cherry-pick`.
- `Status` must match the task state on the board.

| Task ID | Title | Dispatch Branch | Dev Branch | Integration Method | Status |
|---|---|---|---|---|---|
```

Expected: 分支映射文档显式绑定任务编号、执行分支、集成方式和状态，不再是空表头。

- [ ] **Step 3: 验证看板与分支映射格式**

Run:

```powershell
Select-String -Path 'tasks\board.md' -Pattern 'Entry format','## To Do','## Doing','## Blocked','## Done'
Select-String -Path 'tasks\branches.md' -Pattern 'Dispatch Branch','Integration Method','rebase --onto','cherry-pick','Status'
```

Expected: 不报错，且输出匹配到看板格式说明和分支映射规则。

- [ ] **Step 4: 提交格式规范化**

Run:

```powershell
git add tasks/board.md tasks/branches.md
git commit -m "docs: normalize dispatch board and branch mapping"
```

Expected: 出现一条只包含 `board` 与 `branches` 规范化的提交。

### Task 3: 补全调度规则文档

**Files:**
- Modify: `tasks/rules.md`
- Test: rules coverage for naming, startup gate, completion gate, and integration constraints

- [ ] **Step 1: 重写 `tasks/rules.md`**

Write:

```md
# Dispatch Rules

## Allowed On dispatch/tasks
- Task breakdown
- Task cards
- Board updates
- Branch mapping
- Dispatch rules
- Task archive

## Not Allowed On dispatch/tasks
- Business code development
- Feature implementation
- Direct code integration to main

## Task ID Rule
- Use `TASK-001`, `TASK-002`, `TASK-003`, and so on.
- Do not reuse archived task IDs.

## Dev Branch Naming
- `feat/task-001-<topic>`
- `fix/task-001-<topic>`
- `data/task-001-<topic>`

## Startup Gate
1. Assign a task ID.
2. Create `tasks/assignments/TASK-xxx.md`.
3. Add the task entry to `tasks/board.md`.
4. Add the mapping row to `tasks/branches.md`.
5. Only then create the dev branch.

## Completion Gate
1. Record verification in the task card.
2. Move the board entry to `## Done`.
3. Move the task card to `tasks/archive/`.
4. Keep integration limited to `rebase --onto` or `cherry-pick`.

## Branch Flow
1. Update task records on `dispatch/tasks`.
2. Create the dev branch from `dispatch/tasks`.
3. Implement and test on the dev branch.
4. Bring code to `main` using `rebase --onto` or `cherry-pick`.

## Integration Rule
- Do not merge `dispatch/tasks` directly into `main`.
- Do not merge a dev branch directly into `main` if it still carries dispatch history.
```

Expected: `rules.md` 同时约束“允许什么、禁止什么、怎么命名、何时可以启动、何时可以完成、怎样回主线”。

- [ ] **Step 2: 验证规则覆盖范围**

Run:

```powershell
Select-String -Path 'tasks\rules.md' -Pattern 'Allowed On dispatch/tasks','Not Allowed On dispatch/tasks','Task ID Rule','Dev Branch Naming','Startup Gate','Completion Gate','Branch Flow','Integration Rule'
Select-String -Path 'tasks\rules.md' -Pattern 'TASK-001','feat/task-001-<topic>','rebase --onto','cherry-pick'
```

Expected: 不报错，且输出覆盖命名规则、启动/完成门禁和集成约束。

- [ ] **Step 3: 提交规则补全**

Run:

```powershell
git add tasks/rules.md
git commit -m "docs: expand dispatch rules"
```

Expected: 出现一条只包含调度规则增强的提交。

### Task 4: 做跨文档一致性验证

**Files:**
- Test: `tasks/workflow.md`
- Test: `tasks/templates/task-template.md`
- Test: `tasks/board.md`
- Test: `tasks/branches.md`
- Test: `tasks/rules.md`

- [ ] **Step 1: 验证所有目标文件存在**

Run:

```powershell
$paths = @(
  'tasks\workflow.md',
  'tasks\templates\task-template.md',
  'tasks\board.md',
  'tasks\branches.md',
  'tasks\rules.md'
)
foreach ($path in $paths) {
  if (-not (Test-Path $path)) { throw "Missing file: $path" }
}
Write-Output 'OK: dispatch task startup docs exist'
```

Expected: 输出 `OK: dispatch task startup docs exist`。

- [ ] **Step 2: 验证命名与集成规则跨文档一致**

Run:

```powershell
Select-String -Path 'tasks\workflow.md','tasks\templates\task-template.md','tasks\branches.md','tasks\rules.md' -Pattern 'dispatch/tasks','rebase --onto','cherry-pick'
Select-String -Path 'tasks\templates\task-template.md','tasks\rules.md' -Pattern 'TASK-001','feat/task-001'
Select-String -Path 'tasks\board.md','tasks\branches.md' -Pattern 'Done','Status'
```

Expected: 不报错，且四类关键信息在对应文档中都能被匹配到。

- [ ] **Step 3: 验证 Git 工作区与文本质量**

Run:

```powershell
git diff --check
git status --short --branch
```

Expected: `git diff --check` 无输出；`git status --short --branch` 显示当前位于 `dispatch/tasks`，且工作区干净。

- [ ] **Step 4: 输出人工复核结论**

Run:

```powershell
Get-Content 'tasks\workflow.md'
Get-Content 'tasks\templates\task-template.md'
Get-Content 'tasks\board.md'
Get-Content 'tasks\branches.md'
Get-Content 'tasks\rules.md'
```

Expected: 五份文档内容可直接人工检查，确认字段、规则、流程彼此闭环。
