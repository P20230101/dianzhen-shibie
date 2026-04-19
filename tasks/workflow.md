# Dispatch Workflow

## 1. Start A Task
1. Assign the next `TASK-xxx`.
2. Create `tasks/assignments/TASK-xxx.md` from `tasks/templates/task-template.md`, keeping the initial `Status Log` entry for `Created`.
3. Add the task entry to `tasks/board.md` under `## To Do`.
4. Add the branch mapping row to `tasks/branches.md` with `Status` set to `To Do`.
5. Commit the dispatch record on `dispatch/tasks`.
6. Create the dev branch from `dispatch/tasks`.

A task is formally created only after steps 1-4 are complete.
Steps 5-6 must still be completed before it can enter `Doing`.

## 2. Execute A Task
1. Switch to the dev branch.
2. When implementation starts, move the board entry to `## Doing`, set the branch mapping `Status` to `Doing`, and append `Started` to `Status Log` on `dispatch/tasks`.
3. Implement and test on the dev branch only.
4. If an external blocker stops progress, move the board entry to `## Blocked`, set the branch mapping `Status` to `Blocked`, and append `Blocked` to `Status Log` on `dispatch/tasks`.
5. When the blocker is cleared and work resumes, move the board entry and branch mapping back to `Doing` and append `Resumed` to `Status Log` on `dispatch/tasks`.
6. For every state change, update the task card, `tasks/board.md`, and `tasks/branches.md` together on `dispatch/tasks`.
7. Keep `Integration Method` limited to `rebase --onto` or `cherry-pick`.

## 3. Finish A Task
1. Record verification evidence in the task card.
2. When verification is complete and the task is ready to close, append `Done` to `Status Log`.
3. Move the board entry to `## Done`.
4. Keep the branch mapping row and mark `Status` as `Done`.
5. Append `Archived` to `Status Log`, then move the task card from `tasks/assignments/` to `tasks/archive/`.

A task is formally done only after verification is recorded, `Done` is logged, the board and branch mapping are `Done`, and the archived task card includes `Archived`.

## 4. Integration Reminder
- Do not merge `dispatch/tasks` directly into `main`.
- Do not merge a dev branch directly into `main` if it still carries dispatch history.
- Bring code to `main` with `rebase --onto` or `cherry-pick`.
