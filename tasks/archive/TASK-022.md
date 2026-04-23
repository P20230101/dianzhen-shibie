# Task Card

- Task ID: `TASK-022`
- Title: `Hybrid plate-rod lattice sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_1016_j_ijimpeng_2025_105321 into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-022-extract-hprl`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-021`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the 10_1016_j_ijimpeng_2025_105321 lattice target.
- Running the bundle builder appends one new HPRL sample and evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-021 baseline.
- Tests cover the HPRL paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_ijimpeng_2025_105321`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`
- `sample_count=13, evidence_count=66, KG nodes=92, edges=79`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-22 15:12 | Created on dispatch/tasks`
- `2026-04-22 15:12 | Started on feat/task-022-extract-hprl`
- `2026-04-22 15:23 | Done | bundle appended; sample_count=13, evidence_count=66, KG nodes=92, edges=79`
- `2026-04-22 15:23 | Archived to tasks/archive/`
