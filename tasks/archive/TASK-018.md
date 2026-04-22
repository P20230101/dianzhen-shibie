# Task Card

- Task ID: `TASK-018`
- Title: `Bio-inspired spatial lattice sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_1016_j_ijimpeng_2023_104713 into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-018-extract-bioinspired-spatial-lattice`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-017`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the bio-inspired spatial lattice paper target.
- Running the bundle builder appends one new sample and six evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-017 baseline.
- Tests cover the spatial lattice paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_ijimpeng_2023_104713`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-21 19:10 | Created on dispatch/tasks`
- `2026-04-21 19:10 | Started on feat/task-018-extract-bioinspired-spatial-lattice`
- `2026-04-21 19:24 | Done | bundle appended; sample_count=9, evidence_count=40, KG nodes=58, edges=49`
- `2026-04-21 19:24 | Archived to tasks/archive/`
