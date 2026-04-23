# P3 Closeout Boundary and Completion Window

## Context

The repository has already completed the task chain through `TASK-026`.

- `tasks/board.md` has no open work in `To Do`, `Doing`, or `Blocked`.
- `tasks/branches.md` marks every task row through `TASK-026` as `Done`.
- `tasks/workspace-map.md` says `TASK-026` is closed locally.
- `tasks/project-overview.md` and `tasks/roadmap.md` still need a final phase-level closeout statement so the roadmap and execution state stop reading as an unfinished sample-expansion run.

This spec defines the terminal `P3` boundary for that closeout. It does not introduce any new sample-expansion task.

## Decision

`P3` is a closeout phase only. Its purpose is to integrate the current results, accept them as the final sample-expansion output set, archive the task trail, and synchronize the repository's overview documents so no further phase ambiguity remains.

Allowed work in `P3`:

- Integrating the current sample-expansion results into the final repository state.
- Accepting the results as the closed output set for this run.
- Archiving the completed task trail.
- Final phase-state synchronization across `tasks/project-overview.md`, `tasks/roadmap.md`, `tasks/workspace-map.md`, `tasks/board.md`, and `tasks/branches.md`.
- Final verification that all completed tasks remain closed and no open task rows reappear.
- A single closeout commit or equivalent documentation pass if needed to keep the state files consistent.

Not allowed in `P3`:

- New task IDs.
- New sample bundles.
- New extraction rules or expansion targets.
- New execution branches for the closed sample-expansion line.
- Reopening completed tasks just to move work around.

## Completion Window

Target completion window: the current working day, `2026-04-23`, assuming the repository does not reopen any task or discover a new blocker.

This window is valid because the work left after `TASK-026` is not feature work. It is document reconciliation and closeout confirmation only.

## Completion Criteria

`P3` is complete when all of the following are true:

1. `tasks/project-overview.md` says the repository is in the closeout state, not still in an active sample-expansion phase.
2. `tasks/roadmap.md` shows the current position as the closeout state and no longer frames the run as unfinished.
3. `tasks/workspace-map.md` remains aligned with the actual branch/task status.
4. `tasks/board.md` has no open rows in `To Do`, `Doing`, or `Blocked`.
5. `tasks/branches.md` has every task row marked `Done`.
6. The task archive remains the source of record for closed tasks and no new sample-expansion task is added during closeout.

## Verification

Use the following checks to confirm the closeout:

- `rg -n "P2|P3|TASK-026|To Do|Doing|Blocked|Done" tasks/project-overview.md tasks/roadmap.md tasks/workspace-map.md tasks/board.md tasks/branches.md`
- `git status --short`
- Manual review of the five task-state documents to ensure they say the same thing about the current phase.

## Failure Handling

If any of the five task-state documents disagree, treat that as a documentation-sync defect and repair it in the same pass.

If a reopened task or new blocker appears, pause the closeout and re-evaluate the boundary before making any further roadmap claim.
