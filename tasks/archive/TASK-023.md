# Task Card

- Task ID: `TASK-023`
- Title: `BCC lattice sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_1016_j_matdes_2019_108076 into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-023-extract-matdes-2019-bcc`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-022`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the 10_1016_j_matdes_2019_108076 lattice target.
- Running the bundle builder appends one new BCC sample and evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-022 baseline.
- Tests cover the MATDES 2019 paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_matdes_2019_108076`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`
- `sample_count=14, evidence_count=74, KG nodes=102, edges=88`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-22 15:59 | Created on dispatch/tasks`
- `2026-04-22 15:59 | Started on feat/task-023-extract-matdes-2019-bcc`
- `2026-04-22 16:08 | Done | bundle appended; sample_count=14, evidence_count=74, KG nodes=102, edges=88`
- `2026-04-22 16:08 | Archived to tasks/archive/`
