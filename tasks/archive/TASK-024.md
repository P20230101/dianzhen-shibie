# Task Card

- Task ID: `TASK-024`
- Title: `Octagonal lattice sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_1016_j_matdes_2018_05_059 into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-024-extract-matdes-2018-octagonal`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-023`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the 10_1016_j_matdes_2018_05_059 lattice target.
- Running the bundle builder appends one new Octagonal sample and evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-023 baseline.
- Tests cover the MATDES 2018 paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_matdes_2018_05_059`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`
- `sample_count=15, evidence_count=82, KG nodes=112, edges=97`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-22 16:40 | Created on dispatch/tasks`
- `2026-04-22 16:40 | Started on feat/task-024-extract-matdes-2018-octagonal`
- `2026-04-22 17:11 | Done | bundle appended; sample_count=15, evidence_count=82, KG nodes=112, edges=97`
- `2026-04-22 17:11 | Archived to tasks/archive/`
