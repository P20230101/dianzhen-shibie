# PDF Library Framework

This directory is the canonical intake layer for source papers.
Raw PDFs stay here; parsed, extracted, merged, cleaned, and exported artifacts stay in the later `data/0x_*` layers.

## Current source folders

- `C:\Users\Administrator\Desktop\dianzhen shujuku\1蜂窝 Honeycomb`
- `C:\Users\Administrator\Desktop\dianzhen shujuku\2晶格 Lattice`

Use those two folders as the current staging area for the existing corpus.

## Canonical storage

| Location | Purpose |
|---|---|
| `data/01_raw/pdfs/inbox/honeycomb/` | Raw honeycomb papers waiting for first-pass identification |
| `data/01_raw/pdfs/inbox/lattice/` | Raw lattice papers waiting for first-pass identification |
| `data/01_raw/pdfs/library/honeycomb/<paper_id>/original.pdf` | Canonical honeycomb paper folder after identification |
| `data/01_raw/pdfs/library/lattice/<paper_id>/original.pdf` | Canonical lattice paper folder after identification |
| `data/01_raw/pdfs/paper_register_template.csv` | Manual paper inventory template |
| `data/01_raw/pdfs/paper_register.csv` | Canonical paper register after first-pass identification |
| `data/01_raw/pdfs/paper_register.md` | Human-readable view of the canonical paper register |
| `data/01_raw/pdfs/paper_register_first_pass.csv` | Audit snapshot of the initial title/abstract pass |
| `data/01_raw/pdfs/paper_register_first_pass.md` | Human-readable view of the initial title/abstract pass |
| `scripts/build_pdf_register.py` | Regenerates the first-pass paper register from the canonical PDF library |

## Classification rules

Keep `family` and `structure_main_class` separate:

| Family | When to use | Typical `structure_main_class` values |
|---|---|---|
| `honeycomb` | 2D honeycomb, auxetic honeycomb, circular-celled honeycomb, hierarchical honeycomb | `honeycomb_2d` |
| `lattice` | TPMS, truss lattice, plate lattice, tube lattice, hybrid lattice, bioinspired lattice, Voronoi lattice | `tpms`, `truss_lattice`, `plate_lattice`, `tube_lattice`, `hybrid_lattice`, `bioinspired`, `voronoi` |
| `mixed` | The paper genuinely spans both shelves and cannot be assigned cleanly yet | Keep in inbox until resolved |
| `unknown` | Not enough evidence yet | Keep in inbox until resolved |

When a paper has explicit subtype cues, store them in `structure_subtype_list` as `;`-separated `snake_case` tokens. Leave the field blank when no explicit subtype cue is present.

## Paper identity

- Use `paper_id = doi_slug` when a DOI exists.
- Otherwise use `paper_id = title_slug`.
- Keep one `original.pdf` per paper folder.
- Do not put parsed or extracted outputs inside the raw library.

## Workflow

1. Put the raw PDF in the correct inbox folder.
2. Record it in the paper register.
3. Assign `family`, `paper_id`, `structure_main_class`, and `structure_subtype_list`.
4. Move it to `library/<family>/<paper_id>/original.pdf`.
5. Let later stages write to `data/02_parsed/`, `data/03_extracted/`, `data/04_merged/`, `data/05_cleaned/`, and `data/06_exports/`.

The first parsed-layer artifact produced from this library is `data/02_parsed/pdf_intake_manifest.json`, which keeps the register rows together with PDF page counts and first-page excerpts.

## Example mapping

- A honeycomb paper becomes `family=honeycomb`, `structure_main_class=honeycomb_2d`.
- A TPMS or truss paper becomes `family=lattice`, `structure_main_class=tpms` or `truss_lattice`.
- If a paper is ambiguous, leave it in the inbox and mark it `unknown`.
