# Task Card

- Task ID: `TASK-011`
- Title: `PDF sample expansion from the library`
- Goal: `Promote one additional paper from the current PDF library, starting with 10_1016_j_jmrt_2023_05_167, into an accepted sample and verified evidence bundle and confirm the KG grows beyond the workbook seed.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-011-extract-paper-sample`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-010`

## Acceptance Criteria
- One additional paper-derived sample and evidence bundle is created from the PDF library.
- The promoted bundle passes schema validation and becomes KG-eligible.
- Running `scripts/project_knowledge_graph.py` after promotion yields a graph larger than the workbook-only baseline.
- Tests cover the new paper sample bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_extract_pdf_sample.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_jmrt_2023_05_167`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-21 13:16 | Created on dispatch/tasks`
- `2026-04-21 13:16 | Started on feat/task-011-extract-paper-sample`
- `2026-04-21 13:16 | Done | paper-derived bundle appended; KG nodes=12, edges=10`
- `2026-04-21 13:16 | Archived to tasks/archive/`
