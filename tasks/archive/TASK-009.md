# Task Card

- Task ID: `TASK-009`
- Title: `External retrieval KG smoke verification`
- Goal: `Prove the retrieval corpus, query ranking, and KG projection chain runs end to end on fixtures.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-009-smoke-retrieval-kg`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-006`, `TASK-007`, and `TASK-008` complete

## Acceptance Criteria
- `tests/test_external_retrieval_kg_smoke.py` exercises the full fixture chain.
- The smoke path produces ranked candidates and a non-empty projected graph on fixture data.
- The smoke test validates the boundary between retrieval, ranking, and KG projection.

## Verification
- `python -m pytest -q tests/test_external_retrieval_kg_smoke.py`
- `python -m pytest -q tests/test_external_retrieval_kg_smoke.py` -> passed

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-20 21:16 | Created on dispatch/tasks`
- `2026-04-20 21:20 | Started on feat/task-009-smoke-retrieval-kg`
- `2026-04-20 21:20 | Done | end-to-end fixture smoke verified`
- `2026-04-20 21:20 | Archived to tasks/archive/`
