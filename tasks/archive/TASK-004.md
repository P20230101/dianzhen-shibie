# Task Card

- Task ID: `TASK-004`
- Title: `PDF subtype enrichment and register sync`
- Goal: `Populate structure_subtype_list from PDF title/abstract cues and keep the canonical paper register synchronized with the PDF library.`
- Dispatch Branch: `dispatch/tasks`
- Dev Branch: `feat/task-004-extract-subtypes`
- Integration Method: `rebase --onto`
- Dependencies: `canonical PDF library`

## Acceptance Criteria
- The PDF register builder emits `structure_subtype_list` for explicit subtype cues in title or abstract text.
- The builder writes both `paper_register_first_pass.csv` / `.md` and the canonical `paper_register.csv` / `.md`.
- Representative honeycomb and lattice papers resolve to expected subtype tokens.
- Ambiguous papers may keep `structure_subtype_list` empty; main class classification remains unchanged.

## Verification
- `pytest -q tests/test_pdf_register_extractor.py` -> passed
- `python .\scripts\build_pdf_register.py` -> wrote 17 rows to `paper_register_first_pass.csv` / `.md` and `paper_register.csv` / `.md`

## Status Log
- `2026-04-20 19:51 | Created on dispatch/tasks`
- `2026-04-20 19:51 | Started on feat/task-004-extract-subtypes`
- `2026-04-20 20:08 | Done | subtype enrichment and canonical sync verified`
- `2026-04-20 20:08 | Archived to tasks/archive/TASK-004.md`
