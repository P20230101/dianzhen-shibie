# Task Card

- Task ID: `TASK-014`
- Title: `Star auxetic honeycomb sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_1016_j_tws_2020_106623 into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-014-extract-star-auxetic`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-013`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the star auxetic honeycomb paper target.
- Running the bundle builder appends one new sample and four evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-013 baseline.
- Tests cover the star auxetic paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_tws_2020_106623`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-21 15:30 | Created on dispatch/tasks`
- `2026-04-21 15:30 | Started on feat/task-014-extract-star-auxetic`
- `2026-04-21 16:14 | Done | paper-derived bundle appended; sample_count=5, evidence_count=20, KG nodes=30, edges=25`
- `2026-04-21 16:14 | Archived to tasks/archive/`
