# Dispatch Rules

## Allowed On dispatch/tasks
- Task breakdown
- Task cards
- Board updates
- Branch mapping
- Workflow updates
- Task templates
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
2. Create `tasks/assignments/TASK-xxx.md` from `tasks/templates/task-template.md`, keeping the initial `Created` entry in `Status Log`.
3. Add the task entry to `tasks/board.md` under `## To Do`.
4. Add the branch mapping row to `tasks/branches.md` with `Status` set to `To Do`.
5. Commit the dispatch record on `dispatch/tasks`.
6. Only then create the dev branch from `dispatch/tasks`.

## Completion Gate
1. Record verification evidence in the task card and append `Done` to `Status Log`.
2. Move the board entry to `## Done`.
3. Keep the branch mapping row and mark `Status` as `Done`.
4. Append `Archived` to `Status Log`, then move the task card to `tasks/archive/`.

## Branch Flow
1. Update and commit task records on `dispatch/tasks`.
2. Create the dev branch from `dispatch/tasks`.
3. Implement and test on the dev branch.
4. Bring code to `main` using `rebase --onto` or `cherry-pick`.

## State Flow
- `To Do`: use after the startup gate creates the task card, board entry, and branch mapping row. The board entry stays under `## To Do`, the branch mapping `Status` stays `To Do`, and the task card keeps the `Created` log entry.
- `Doing`: use only after the dev branch exists and implementation starts. Move the board entry to `## Doing`, set the branch mapping `Status` to `Doing`, and append `Started` to `Status Log`.
- `Blocked`: use only when an external blocker stops progress. Move the board entry to `## Blocked`, set the branch mapping `Status` to `Blocked`, and append `Blocked` to `Status Log`.
- `Doing` from `Blocked`: when the blocker is cleared and implementation resumes, move the board entry and branch mapping back to `Doing` and append `Resumed` to `Status Log`.
- `Done`: use only after verification evidence is recorded. Move the board entry to `## Done`, set the branch mapping `Status` to `Done`, and append `Done` to `Status Log`.
- `Archived`: before moving the task card to `tasks/archive/`, append `Archived` to `Status Log`. Archiving does not change the board or branch mapping away from `Done`.

## Status Log Rule
- Every task card must keep `Status Log`.
- Append one line for every state change.
- Minimum lifecycle entries are `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.

## Integration Rule
- Do not merge `dispatch/tasks` directly into `main`.
- Do not merge a dev branch directly into `main` if it still carries dispatch history.
