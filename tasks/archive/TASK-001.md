# Task Card

- Task ID: `TASK-001`
- Title: `P1 first minimal chain`
- Goal: `Run the first minimal end-to-end chain on one execution branch.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-001-min-pipeline`
- Integration Method: `rebase --onto`
- Dependencies: `None`

## Acceptance Criteria
- The first minimal chain is runnable on `feat/task-001-min-pipeline`.
- The chain stays on one execution branch and covers input entry, parsed layer, extracted output, sample/evidence alignment, and minimal review/export closure.

## Verification
- `python .\scripts\p1_seed.py` -> wrote `data/p1/seed_input.json` and `outputs/p1/seed/seed_input.json`.
- `python .\scripts\p1_transform.py` -> wrote `outputs/p1/parsed/parsed_sample.json`, `outputs/p1/extracted/samples_v1.json`, and `outputs/p1/extracted/evidence_v1.json`.
- `python .\scripts\p1_validate_export.py` -> schema checks passed and wrote `outputs/p1/review/p1_chain_report.json`.

## Status Log
- `2026-04-20 13:43 | Created on dispatch/tasks`
- `2026-04-20 13:51 | Started on feat/task-001-min-pipeline`
- `2026-04-20 13:58 | Done | seed/transform/validate passed`
- `2026-04-20 13:58 | Archived to tasks/archive/`
