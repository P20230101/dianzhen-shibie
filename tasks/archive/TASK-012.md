# Task Card

- Task ID: `TASK-012`
- Title: `AddMA gyroid sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_1016_j_addma_2022_102887 into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-012-addma-gyroid-sample`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-011`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the AddMA gyroid paper target.
- Running the bundle builder appends one new sample and four evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-011 baseline.
- Tests cover the AddMA paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_addma_2022_102887`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-21 13:43 | Created on dispatch/tasks`
- `2026-04-21 13:43 | Started on feat/task-012-addma-gyroid-sample`
- `2026-04-21 14:09 | Done | paper-derived bundle appended; sample_count=3, evidence_count=12, KG nodes=18, edges=15`
- `2026-04-21 14:09 | Archived to tasks/archive/`
