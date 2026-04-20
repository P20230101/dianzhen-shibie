# Branch Mapping

Rules:
- One task per row.
- `Dispatch Branch` must stay `dispatch/tasks`.
- `Integration Method` must be `rebase --onto` or `cherry-pick`.
- `Status` must match the task state on the board.

| Task ID | Title | Dispatch Branch | Dev Branch | Integration Method | Status |
|---|---|---|---|---|---|
| TASK-001 | P1 first minimal chain | dispatch/tasks | feat/task-001-min-pipeline | rebase --onto | Done |
| TASK-002 | Excel input adapter for seed intake | dispatch/tasks | feat/task-002-input-excel | rebase --onto | Doing |
