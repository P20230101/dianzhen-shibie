# Task Card

- Task ID: `TASK-020`
- Title: `BCCz+cross sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_3390_ma18040732 into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-020-extract-bccz-cross`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-019`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the 10_3390_ma18040732 lattice target.
- Running the bundle builder appends one new sample and evidence rows for the BCCz+cross representative structure to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-019 baseline.
- Tests cover the BCCz+cross paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_3390_ma18040732`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`
- `sample_count=11, evidence_count=52, KG nodes=74, edges=63`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-22 13:32 | Created on dispatch/tasks`
- `2026-04-22 13:51 | Started on feat/task-020-extract-bccz-cross`
- `2026-04-22 13:56 | Done | bundle appended; sample_count=11, evidence_count=52, KG nodes=74, edges=63`
- `2026-04-22 13:56 | Archived to tasks/archive/`
