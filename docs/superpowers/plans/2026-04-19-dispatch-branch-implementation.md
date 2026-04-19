# Dispatch Branch Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将当前项目纳入 Git 管理，并建立 `main + dispatch/tasks + 子开发支线` 的分支模型与任务调度骨架。

**Architecture:** 实施拆成四块：先初始化 Git 仓库并建立干净的 `main` 基线，再创建只承载任务调度资产的 `dispatch/tasks` 支线，然后在该支线上落 `tasks/` 目录骨架与规则文档，最后用一次最小分支烟雾验证确认该工作流可用。`main` 保持不含任务调度资产，`dispatch/tasks` 保持不含业务代码开发提交。

**Tech Stack:** Git, PowerShell, Markdown

---

### Task 1: 初始化 Git 仓库并建立 `main` 基线

**Files:**
- Create: `.gitignore`
- Create: `.git/`
- Test: Git repository state

- [ ] **Step 1: 写入最小 `.gitignore`**

Write:

```gitignore
.worktrees/
```

Expected: 为后续可能使用的项目内 worktree 预留忽略规则，避免未来目录污染 Git 状态。

- [ ] **Step 2: 初始化 Git 仓库并显式创建 `main`**

Run:

```powershell
git init --initial-branch=main
```

Expected: 当前目录成为 Git 仓库，当前分支名为 `main`。

- [ ] **Step 3: 添加首个基线提交**

Run:

```powershell
git add .
git commit -m "chore: initialize repository baseline"
```

Expected: 仓库出现第一个提交，当前所有现有文件纳入版本控制。

- [ ] **Step 4: 验证仓库与主分支状态**

Run:

```powershell
git status --short --branch
```

Expected: 输出中包含 `## main`，且工作区为干净状态。

### Task 2: 创建 `dispatch/tasks` 分支并切换到该分支

**Files:**
- Create: Git branch `dispatch/tasks`
- Test: Branch topology

- [ ] **Step 1: 从 `main` 创建 `dispatch/tasks`**

Run:

```powershell
git switch -c dispatch/tasks
```

Expected: 当前分支切换为 `dispatch/tasks`。

- [ ] **Step 2: 验证 `main` 与 `dispatch/tasks` 同时存在**

Run:

```powershell
git branch --list
```

Expected: 输出中至少包含 `main` 与 `dispatch/tasks` 两个分支。

- [ ] **Step 3: 确认 `dispatch/tasks` 仅基于 `main` 当前基线**

Run:

```powershell
git log --oneline --decorate -n 3
```

Expected: `dispatch/tasks` 当前仅包含基线初始化提交，没有额外任务调度提交。

### Task 3: 在 `dispatch/tasks` 上建立任务调度资产骨架

**Files:**
- Create: `tasks/board.md`
- Create: `tasks/branches.md`
- Create: `tasks/rules.md`
- Create: `tasks/assignments/.gitkeep`
- Create: `tasks/archive/.gitkeep`

- [ ] **Step 1: 创建 `tasks/` 目录与占位文件**

Run:

```powershell
$dirs = @('tasks','tasks\\assignments','tasks\\archive')
foreach ($dir in $dirs) {
  New-Item -Path (Join-Path $PWD $dir) -ItemType Directory -Force | Out-Null
}
New-Item -Path (Join-Path $PWD 'tasks\\assignments\\.gitkeep') -ItemType File -Force | Out-Null
New-Item -Path (Join-Path $PWD 'tasks\\archive\\.gitkeep') -ItemType File -Force | Out-Null
```

Expected: `tasks/` 目录结构存在，空目录可被 Git 跟踪。

- [ ] **Step 2: 写入 `tasks/board.md`**

Write:

```md
# Task Board

## To Do

## Doing

## Blocked

## Done
```

Expected: 看板文件为后续任务状态管理提供固定入口。

- [ ] **Step 3: 写入 `tasks/branches.md`**

Write:

```md
# Branch Mapping

| Task ID | Description | Dispatch Branch | Dev Branch | Integration Method | Status |
|---|---|---|---|---|---|
```

Expected: 建立任务编号与开发支线的固定映射表。

- [ ] **Step 4: 写入 `tasks/rules.md`**

Write:

```md
# Dispatch Rules

## Allowed On dispatch/tasks
- Task breakdown
- Status updates
- Branch assignment
- Dispatch rules
- Task archive

## Not Allowed On dispatch/tasks
- Business code development
- Feature implementation
- Direct code integration to main

## Branch Flow
1. Update task records on `dispatch/tasks`
2. Create dev branch from `dispatch/tasks`
3. Implement on dev branch
4. Move code to `main` using `rebase --onto` or `cherry-pick`

## Integration Rule
- Do not merge `dispatch/tasks` directly into `main`
- Do not merge a dev branch directly into `main` if it still carries dispatch history
```

Expected: 将调度支线职责与禁用行为写死在仓库内。

- [ ] **Step 5: 提交任务调度骨架**

Run:

```powershell
git add tasks
git commit -m "chore: add dispatch task management skeleton"
```

Expected: `dispatch/tasks` 出现专属调度提交，且该提交不进入 `main`。

### Task 4: 执行最小分支烟雾验证

**Files:**
- Test: Branch workflow

- [ ] **Step 1: 从 `dispatch/tasks` 创建临时开发支线**

Run:

```powershell
git switch -c feat/dispatch-smoke
```

Expected: 成功从 `dispatch/tasks` 切出开发支线。

- [ ] **Step 2: 验证临时开发支线的祖先关系**

Run:

```powershell
git log --oneline --decorate -n 5
```

Expected: 日志中包含基线提交与 `dispatch/tasks` 的调度提交，证明开发支线确实从调度支线切出。

- [ ] **Step 3: 切回 `dispatch/tasks` 并删除临时开发支线**

Run:

```powershell
git switch dispatch/tasks
git branch -D feat/dispatch-smoke
```

Expected: 烟雾验证分支被清理，仓库中仅保留 `main` 与 `dispatch/tasks`。

- [ ] **Step 4: 验证当前分支拓扑**

Run:

```powershell
git branch --list
git status --short --branch
```

Expected: 输出中包含 `main` 与 `dispatch/tasks`；当前位于 `dispatch/tasks`；工作区干净。

### Task 5: 进行职责隔离验证

**Files:**
- Test: `main`
- Test: `dispatch/tasks`
- Test: `tasks/` asset visibility

- [ ] **Step 1: 验证 `main` 不含调度资产提交**

Run:

```powershell
git switch main
if (Test-Path 'tasks') { throw 'tasks directory should not exist on main' }
git log --oneline --decorate -n 3
```

Expected: `main` 上不存在 `tasks/` 目录，且只有基线提交。

- [ ] **Step 2: 切回 `dispatch/tasks` 并验证调度资产存在**

Run:

```powershell
git switch dispatch/tasks
Get-ChildItem 'tasks' -Recurse
```

Expected: `dispatch/tasks` 上存在 `board.md`、`branches.md`、`rules.md`、`assignments/.gitkeep`、`archive/.gitkeep`。

- [ ] **Step 3: 输出最终状态供人工复核**

Run:

```powershell
git status --short --branch
git branch --list
```

Expected: 当前位于 `dispatch/tasks`，工作区干净，只存在 `main` 与 `dispatch/tasks` 两个长期分支。
