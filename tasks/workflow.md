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
