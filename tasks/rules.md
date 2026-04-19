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
2. Create `tasks/assignments/TASK-xxx.md` from `tasks/templates/task-template.md`.
3. Add the task entry to `tasks/board.md` under `## To Do`.
4. Add the branch mapping row to `tasks/branches.md`.
5. Commit the dispatch record on `dispatch/tasks`.
6. Only then create the dev branch from `dispatch/tasks`.

## Completion Gate
1. Record verification evidence in the task card.
2. Move the board entry to `## Done`.
3. Move the task card to `tasks/archive/`.
4. Keep the branch mapping row and mark `Status` as `Done`.

## Branch Flow
1. Update and commit task records on `dispatch/tasks`.
2. Create the dev branch from `dispatch/tasks`.
3. Implement and test on the dev branch.
4. Bring code to `main` using `rebase --onto` or `cherry-pick`.

## Integration Rule
- Do not merge `dispatch/tasks` directly into `main`.
- Do not merge a dev branch directly into `main` if it still carries dispatch history.
