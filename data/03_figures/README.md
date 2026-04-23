# Figure Understanding Artifacts

This directory stores unit-level figure records produced by the figure understanding layer.

Expected outputs:

- `figure_units_v1.jsonl`
- `figure_units_review.csv`
- `manifest.json`

Each unit record should include at least:

- `paper_id`
- `source_figure_id`
- `unit_id`
- `unit_index`
- `kind`
- `panel_label`
- `source_page_no`
- `source_image_path`
- `image_path`
- `crop_bbox`
- `caption_text`
- `context_text`
- `figure_type`
- `recaption`
- `figure_summary`
- `confidence`
- `needs_manual_review`
- `source_refs`

The review CSV is a human-facing subset of the same unit records.
