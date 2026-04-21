# Task Card

- Task ID: `TASK-002`
- Title: `Excel input adapter for seed intake`
- Goal: `Convert the prototype workbook into the normalized seed input used by the first minimal chain.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-002-input-excel`
- Integration Method: `rebase --onto`
- Dependencies: `TASK-001`

## Acceptance Criteria
- The adapter reads the prototype workbook and emits one normalized seed input record.
- The emitted seed matches the current P1 chain input contract and can feed the existing seed/transform/validate path.

## Verification
- `python -m pytest tests/test_p1_workbook_seed_adapter.py -q` -> passed.
- `python .\scripts\p1_seed.py` -> wrote `data/p1/seed_input.json` and `outputs/p1/seed/seed_input.json`.
- `python .\scripts\p1_transform.py` -> wrote `outputs/p1/parsed/parsed_sample.json`, `outputs/p1/extracted/samples_v1.json`, and `outputs/p1/extracted/evidence_v1.json`.
- `python .\scripts\p1_validate_export.py` -> schema checks passed and wrote `outputs/p1/review/p1_chain_report.json`.

## Status Log
- `2026-04-20 14:12 | Created on dispatch/tasks`
- `2026-04-20 14:15 | Started on feat/task-002-input-excel`
- `2026-04-20 14:47 | Done | workbook seed adapter and chain validation passed`
- `2026-04-20 14:47 | Archived to tasks/archive/`
