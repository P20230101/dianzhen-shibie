# Task Card

- Task ID: `TASK-010`
- Title: `P1 sample review promotion and KG population`
- Goal: `Promote the validated P1 sample and evidence into accepted/verified state and regenerate a non-empty knowledge graph.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-010-review-approval`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-008`, `TASK-009`

## Acceptance Criteria
- `scripts/promote_p1_review.py` updates the canonical P1 sample and evidence outputs in place.
- Running `scripts/project_knowledge_graph.py` after promotion yields a non-empty graph.
- The promotion helper and graph projection are covered by tests.

## Verification
- `python -m pytest -q tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-20 21:30 | Created on dispatch/tasks`
- `2026-04-20 21:30 | Started on feat/task-010-review-approval`
- `2026-04-20 21:33 | Done | validation passed; knowledge graph nodes=6, edges=5`
- `2026-04-20 21:33 | Archived to tasks/archive/`
