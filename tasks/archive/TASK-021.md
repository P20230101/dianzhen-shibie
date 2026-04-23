# Task Card

- Task ID: `TASK-021`
- Title: `Octet truss lattice sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_1016_j_cirpj_2024_06_009 into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-021-extract-octet`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-020`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the 10_1016_j_cirpj_2024_06_009 lattice target.
- Running the bundle builder appends one new Octet sample and evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-020 baseline.
- Tests cover the Octet paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_cirpj_2024_06_009`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`
- `sample_count=12, evidence_count=58, KG nodes=82, edges=70`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-22 14:38 | Created on dispatch/tasks`
- `2026-04-22 14:38 | Started on feat/task-021-extract-octet`
- `2026-04-22 14:50 | Done | bundle appended; sample_count=12, evidence_count=58, KG nodes=82, edges=70`
- `2026-04-22 14:50 | Archived to tasks/archive/`
