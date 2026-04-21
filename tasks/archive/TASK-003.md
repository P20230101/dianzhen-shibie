# Task Card

- Task ID: `TASK-003`
- Title: `PDF first-pass register extractor`
- Goal: `Extract the first-pass paper register from the canonical PDF library with title, DOI, family, structure class, status, and file path.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-003-input-pdf`
- Integration Method: `rebase --onto`
- Dependencies: `canonical PDF library`

## Acceptance Criteria
- The extractor scans `data/01_raw/pdfs/library`.
- The extractor emits `paper_register_first_pass.csv` and `paper_register_first_pass.md`.
- Each record includes `paper_id`, `title`, `doi`, `family`, `structure_main_class`, `status`, and `file_path`.

## Verification
- `pytest -q tests/test_pdf_register_extractor.py tests/test_p1_workbook_seed_adapter.py` -> passed
- `python .\scripts\build_pdf_register.py` -> wrote 17 rows to `paper_register_first_pass.csv` and `paper_register_first_pass.md`

## Status Log
- `2026-04-20 14:47 | Created on dispatch/tasks`
- `2026-04-20 15:17 | Started on feat/task-003-input-pdf`
- `2026-04-20 15:31 | Done on feat/task-003-input-pdf`
- `2026-04-20 15:31 | Archived to tasks/archive/TASK-003.md`
