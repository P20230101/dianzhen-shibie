# Figure Understanding Artifacts

This directory stores image-level figure records produced by the figure understanding layer.

Expected outputs:

- `figures_v1.jsonl`
- `figures_review.csv`
- `manifest.json`

These artifacts are figure-only. They do not replace `samples_v1.json`, `evidence_v1.json`, or the knowledge graph.

Each figure record should include at least:

- `paper_id`
- `figure_id`
- `page_no`
- `image_path`
- `caption_text`
- `context_text`
- `panel_labels`
- `figure_type`
- `recaption`
- `figure_summary`
- `confidence`
- `needs_manual_review`
- `source_refs`

The review CSV is a human-facing subset of the same figure records.
