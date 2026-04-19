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
