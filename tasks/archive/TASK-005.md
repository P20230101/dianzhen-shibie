# Task Card

- Task ID: `TASK-005`
- Title: `PDF intake manifest adapter`
- Goal: `Build a downstream-ready intake manifest from the canonical PDF register with PDF page counts and stable file paths.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-005-input-pdf-intake`
- Integration Method: `rebase --onto`
- Dependencies: `canonical paper register`

## Acceptance Criteria
- The adapter reads `data/01_raw/pdfs/paper_register.csv`.
- The adapter writes `data/02_parsed/pdf_intake_manifest.json`.
- Each manifest row includes `paper_id`, `title`, `doi`, `family`, `structure_main_class`, `structure_subtype_list`, `status`, `file_path`, and `page_count`.
- Representative records match known PDF page counts and subtype tokens.

## Verification
- `pytest -q tests/test_pdf_register_extractor.py tests/test_pdf_intake_manifest.py` -> passed
- `python .\scripts\build_pdf_intake_manifest.py` -> wrote 17 rows to `data/02_parsed/pdf_intake_manifest.json`

## Status Log
- `2026-04-20 20:08 | Created on dispatch/tasks`
- `2026-04-20 20:16 | Started on feat/task-005-input-pdf-intake`
- `2026-04-20 20:24 | Done | manifest generation and PDF page counts verified`
- `2026-04-20 20:24 | Archived to tasks/archive/TASK-005.md`
