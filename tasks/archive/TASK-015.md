# Task Card

- Task ID: `TASK-015`
- Title: `Vertex-based hierarchical honeycomb sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_1016_j_tws_2019_106436 into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-015-extract-hierarchical-honeycomb`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-014`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the vertex-based hierarchical honeycomb paper target.
- Running the bundle builder appends one new sample and four evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-014 baseline.
- Tests cover the hierarchical honeycomb paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_tws_2019_106436`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-21 16:45 | Created on dispatch/tasks`
- `2026-04-21 16:45 | Started on feat/task-015-extract-hierarchical-honeycomb`
- `2026-04-21 16:59 | Done | paper-derived bundle appended; sample_count=6, evidence_count=24, KG nodes=36, edges=30`
- `2026-04-21 16:59 | Archived to tasks/archive/`
