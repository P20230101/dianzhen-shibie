# P3 Closeout Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Record `P3` as the repository closeout state and remove the last active sample-expansion framing from the phase-facing docs.

**Architecture:** One documentation pass updates the phase summary files, a second pass audits the task-state inventory for consistency, and a final verification pass confirms the repo is closed without reopening any task. No product code changes are made.

**Tech Stack:** Markdown, Git, PowerShell

---

### Task 1: Rewrite the phase summary docs

**Files:**
- Modify: `tasks/project-overview.md`
- Modify: `tasks/roadmap.md`
- Test: `rg`, `git diff --check`

- [ ] **Step 1: Replace the current phase block in `tasks/project-overview.md`**

Replace the current phase section and surrounding status prose with:

```md
## Current Phase

- `P3 / closeout phase`
- `Nearest Milestone: 2026-04-23 | P3 closeout active`

## What The Project Is Doing Now

- Integrating the current sample-expansion results into the closed repository state
- Reconciling the phase-facing documentation so P3 reads as a closeout state
- Freezing the current output set and avoiding new sample-expansion tasks

## In Scope Now

- Closeout reconciliation of the sample-expansion line
- Final verification that all completed tasks remain closed
- Repository governance and dispatch workflow
- Task decomposition and branch policy

## Not In Scope Now

- New sample bundles
- New extraction targets
- New execution branches for the closed line
- Reopening completed tasks

## Next Actions

1. Keep `dispatch/tasks` aligned with the closed state.
2. Do not open any new sample-expansion task from the finished run.
```

- [ ] **Step 2: Replace the current position block in `tasks/roadmap.md`**

Replace the top block with:

```md
## Current Position

- `NOW: P3`
- `Milestone Date: 2026-04-23`
- `Milestone Name: P3 closeout`
- `Acceptance Focus: integrate current results, freeze the completed run, and sync phase-facing docs`
```

Then update the `P3` priority section so it reads as closeout, not an open-ended expansion target:

```md
### `P3`

- The sample-expansion line is closed and the deliverable set is frozen
```

Keep the `P0 / M0`, `P1`, and `P2` rows unchanged.

- [ ] **Step 3: Verify the phase words**

Run:

```powershell
rg -n "P2 / sample-expansion phase|NOW: P2|P3 closeout|sample-expansion phase active" tasks/project-overview.md tasks/roadmap.md
```

Expected: `P2` wording is gone from the top sections; `P3 closeout` wording is present.

- [ ] **Step 4: Check markdown hygiene**

Run:

```powershell
git diff --check -- tasks/project-overview.md tasks/roadmap.md
```

Expected: no whitespace or patch-format errors.

- [ ] **Step 5: Commit the phase-doc update**

Run:

```powershell
git add tasks/project-overview.md tasks/roadmap.md
git commit -m "docs: close out p3 phase docs"
```

Expected: a single commit containing the closeout wording for the phase-facing docs.

### Task 2: Audit the task-state inventory

**Files:**
- Review: `tasks/workspace-map.md`
- Review: `tasks/board.md`
- Review: `tasks/branches.md`
- Test: `rg`, `git diff --check`

- [ ] **Step 1: Verify the closed-task inventory**

Run:

```powershell
rg -n "TASK-026|TASK-025|## To Do|## Doing|## Blocked|## Done|closed locally|Merged locally" tasks/workspace-map.md tasks/board.md tasks/branches.md
```

Expected: the board has no open task rows, the branch map marks every task through `TASK-026` as `Done`, and the workspace map still says `TASK-026` is closed locally.

- [ ] **Step 2: Repair any stale closeout wording**

If any of the three files still describe an active sample-expansion run, patch only those files so they match the closeout state from the spec. Leave the other files unchanged.

- [ ] **Step 3: Recheck consistency**

Run:

```powershell
git diff --check -- tasks/workspace-map.md tasks/board.md tasks/branches.md
```

Expected: no markdown or whitespace errors.

### Task 3: Final closeout verification and commit

**Files:**
- Stage only the files that changed in Tasks 1-2
- Test: `git status`, `rg`

- [ ] **Step 1: Confirm the repository only changed where expected**

Run:

```powershell
git status --short
```

Expected: only the closeout docs that were intentionally updated appear as modified.

- [ ] **Step 2: Run the final cross-doc check**

Run:

```powershell
rg -n "P3 closeout|P2 / sample-expansion phase|NOW: P2|sample-expansion phase active|TASK-026|Doing|Blocked" tasks/project-overview.md tasks/roadmap.md tasks/workspace-map.md tasks/board.md tasks/branches.md
```

Expected: the phase docs read as closeout, and the task-state inventory still shows a fully closed run.

- [ ] **Step 3: Commit the closeout pass**

Run:

```powershell
git add tasks/project-overview.md tasks/roadmap.md tasks/workspace-map.md tasks/board.md tasks/branches.md
git commit -m "docs: close out p3 documentation state"
```

Expected: one clean commit that records the closeout-state documentation update.
