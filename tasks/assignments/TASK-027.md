# Task Card

- Task ID: `TASK-027`
- Title: `Figure understanding unit record implementation`
- Goal: `Turn independently cropable PDF subfigures into unit-level structured records with their own crops, review state, and report cards, stored under data/03_figures/ and ready for downstream inspection.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `codex/task-027-figure-unit-record`
- Integration Method: `rebase --onto`
- Dependencies: `None`

## Acceptance Criteria
- `scripts/figure_understanding_common.py`, `scripts/build_figure_understanding.py`, `scripts/figure_understanding_vlm.py`, and `scripts/render_figure_understanding_report.py` exist and cooperate as a standalone unit-record pipeline.
- Running `pytest tests/test_figure_understanding_common.py tests/test_figure_understanding_vlm.py tests/test_build_figure_understanding.py tests/test_render_figure_understanding_report.py tests/test_figure_understanding_smoke.py -q` passes.
- The pipeline writes `data/03_figures/figure_units_v1.jsonl`, `data/03_figures/figure_units_review.csv`, and `data/03_figures/manifest.json` from figure fixtures.
- The branch only writes unit-level figure artifacts and tests, not sample/evidence or KG outputs.

## Verification
- `pytest tests/test_figure_understanding_common.py tests/test_figure_understanding_vlm.py tests/test_build_figure_understanding.py tests/test_render_figure_understanding_report.py tests/test_figure_understanding_smoke.py -q`

## Status Log
Append one line for every state change. Minimum lifecycle entries: `Created`, `Started`, `Blocked` (if any), `Resumed` (if any), `Done`, and `Archived`.
- `2026-04-23 00:00 | Created on task-027 worktree`
- `2026-04-23 00:05 | Started unit-record implementation work`
- `2026-04-23 00:10 | Done: tests passing, metadata pending cleanup`
