# Task Card

- Task ID: `TASK-025`
- Title: `High-density honeycomb sample expansion`
- Goal: `Append one additional paper-derived sample bundle from pii_s0734_743x_97_00040_7, representing the aluminum honeycomb variant, into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `codex/task-025-extract-high-density-honeycomb`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-024`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the `pii_s0734_743x_97_00040_7` paper target.
- Running the bundle builder appends one new aluminum honeycomb sample and evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-024 baseline.
- Tests cover the high-density honeycomb paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id pii_s0734_743x_97_00040_7`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`
- `sample_count=16, evidence_count=89, KG nodes=121, edges=105`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-22 17:41 | Created on dispatch/tasks`
- `2026-04-22 17:41 | Started on codex/task-025-extract-high-density-honeycomb`
- `2026-04-22 17:41 | Done | bundle appended; sample_count=16, evidence_count=89, KG nodes=121, edges=105`
- `2026-04-22 17:41 | Archived to tasks/archive/`
