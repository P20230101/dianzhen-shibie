# Task Card

- Task ID: `TASK-023`
- Title: `Figure understanding layer implementation`
- Goal: `Turn PDF figures into image-level structured records with type, panel labels, recaption, summary, and confidence, stored under data/03_figures/ and ready for downstream sample extraction.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-023-figure-understanding`
- Integration Method: `rebase --onto`
- Dependencies: `None`

## Acceptance Criteria
- `scripts/figure_understanding_common.py`, `scripts/build_figure_understanding.py`, and `scripts/figure_understanding_vlm.py` exist and cooperate as a standalone figure-understanding pipeline.
- Running `pytest tests/test_figure_understanding_common.py tests/test_build_figure_understanding.py tests/test_figure_understanding_vlm.py tests/test_figure_understanding_smoke.py -v` passes.
- The pipeline writes `data/03_figures/figures_v1.jsonl`, `data/03_figures/figures_review.csv`, and `data/03_figures/manifest.json` from figure fixtures.
- The branch only writes figure artifacts and tests, not sample/evidence or KG outputs.

## Verification
- `pytest tests/test_figure_understanding_common.py tests/test_build_figure_understanding.py tests/test_figure_understanding_vlm.py tests/test_figure_understanding_smoke.py -v`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-22 15:30 | Created on dispatch/tasks`
- `2026-04-22 15:44 | Started on feat/task-023-figure-understanding`
- `2026-04-22 16:12 | Done | figure-understanding layer implemented, tests passed, PR #2 merged`
- `2026-04-22 16:12 | Archived to tasks/archive/`
