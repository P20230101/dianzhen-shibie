# Task Card

- Task ID: `TASK-019`
- Title: `3D metamaterial sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_1016_j_engstruct_2023_116510 into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-019-extract-engstruct-metamaterial`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-018`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the EngStruct 2023 3D metamaterial target.
- Running the bundle builder appends one new sample and six evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-018 baseline.
- Tests cover the 3D metamaterial paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_engstruct_2023_116510`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-21 19:36 | Created on dispatch/tasks`
- `2026-04-21 19:36 | Started on feat/task-019-extract-engstruct-metamaterial`
- `2026-04-21 20:04 | Done | bundle appended; sample_count=10, evidence_count=46, KG nodes=66, edges=56`
- `2026-04-21 20:04 | Archived to tasks/archive/`
