# Task Card

- Task ID: `TASK-026`
- Title: `JMRT 2021 radial hybrid sample expansion`
- Goal: `Append one additional paper-derived sample bundle from 10_1016_j_jmrt_2021_08_092, representing the radial hybrid TPMS lattice, into the canonical P1 extracted outputs and confirm the knowledge graph grows again.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `codex/task-026-jmrt-radial-hybrid`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-025`

## Acceptance Criteria
- `scripts/build_pdf_sample_bundle.py` supports the `10_1016_j_jmrt_2021_08_092` paper target.
- Running the bundle builder appends one new radial hybrid TPMS sample and evidence rows to the canonical P1 extracted outputs.
- Running `scripts/promote_p1_review.py` and `scripts/project_knowledge_graph.py` after the append yields a graph larger than the TASK-025 baseline.
- Tests cover the JMRT 2021 paper bundle path and the KG growth boundary.

## Verification
- `python -m pytest -q tests/test_build_pdf_sample_bundle.py tests/test_promote_p1_review.py tests/test_project_knowledge_graph.py`
- `python scripts/build_pdf_sample_bundle.py --paper-id 10_1016_j_jmrt_2021_08_092`
- `python scripts/promote_p1_review.py`
- `python scripts/project_knowledge_graph.py`
- `sample_count=17, evidence_count=97, KG nodes=131, edges=114`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-22 17:54 | Created on dispatch/tasks`
- `2026-04-22 17:54 | Started on codex/task-026-jmrt-radial-hybrid`
- `2026-04-22 17:59 | Done | bundle appended; sample_count=17, evidence_count=97, KG nodes=131, edges=114`
- `2026-04-22 17:59 | Archived to tasks/archive/`
