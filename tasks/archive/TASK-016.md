# Task Card

- Task ID: `TASK-016`
- Title: `3D printed hierarchical honeycomb sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_1016_j_matdes_2017_10_028 into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-016-extract-matdes-hierarchical`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-015`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the Materials and Design hierarchical honeycomb paper target.
- Running the bundle builder appends one new sample and five evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-015 baseline.
- Tests cover the hierarchical honeycomb paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_matdes_2017_10_028`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-21 17:12 | Created on dispatch/tasks`
- `2026-04-21 17:12 | Started on feat/task-016-extract-matdes-hierarchical`
- `2026-04-21 17:47 | Done | paper-derived bundle appended; sample_count=7, evidence_count=29, KG nodes=43, edges=36`
- `2026-04-21 17:47 | Archived to tasks/archive/`
