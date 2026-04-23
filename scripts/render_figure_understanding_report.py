from __future__ import annotations

import argparse
import csv
import json
import shutil
from datetime import datetime
from html import escape as html_escape
from pathlib import Path


RECORDS_FILENAME = "figures_v1.jsonl"
MANIFEST_FILENAME = "manifest.json"
REVIEW_FILENAME = "figures_review.csv"


def _read_jsonl_records(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            payload = json.loads(stripped)
            if not isinstance(payload, dict):
                raise ValueError(f"{path} line {line_number} must contain a JSON object")
            records.append(payload)
    return records


def _read_review_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _review_status(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text == "true":
        return True
    if text == "false":
        return False
    return None


def _manual_review_flag(value: object) -> bool:
    parsed = _review_status(value)
    if parsed is None:
        raise ValueError(f"invalid needs_manual_review value: {value!r}")
    return parsed


def _record_key(paper_id: str, figure_id: str) -> tuple[str, str]:
    return paper_id.strip(), figure_id.strip()


def _normalize_image_path(artifact_dir: Path, paper_id: str, image_path_value: object) -> str:
    if not isinstance(image_path_value, str):
        raise ValueError("image_path must be a string")
    raw_path_text = image_path_value.strip()
    if not raw_path_text:
        raise ValueError("image_path must not be blank")

    raw_path = Path(raw_path_text)
    artifact_root = artifact_dir.resolve()
    image_root = artifact_root / "images"
    if raw_path.is_absolute():
        candidate = raw_path.resolve()
    elif raw_path.parts[: len(artifact_dir.parts)] == artifact_dir.parts:
        candidate = (artifact_root / Path(*raw_path.parts[len(artifact_dir.parts) :])).resolve()
    elif raw_path.parts and raw_path.parts[0].lower() == "images":
        candidate = (artifact_root / raw_path).resolve()
    else:
        raise ValueError(
            f"{raw_path_text!r} is not under the expected artifact image root {image_root}"
        )

    try:
        relative_path = candidate.relative_to(image_root)
    except ValueError as exc:
        raise ValueError(
            f"{candidate} is not under the expected image root {image_root}"
        ) from exc

    return (Path("images") / relative_path).as_posix()


def _normalize_record(artifact_dir: Path, record: dict[str, object]) -> dict[str, object]:
    normalized = dict(record)
    paper_id = str(record.get("paper_id") or "").strip()
    normalized["image_path"] = _normalize_image_path(artifact_dir, paper_id, record.get("image_path"))
    normalized["needs_manual_review"] = _manual_review_flag(record.get("needs_manual_review"))
    return normalized


def _validate_review_row(
    record: dict[str, object],
    row: dict[str, str],
    review_path: Path,
    figure_id: str,
) -> None:
    row_status = _review_status(row.get("needs_manual_review"))
    if row_status is None:
        raise ValueError(
            f"invalid needs_manual_review value in {review_path}: {row.get('needs_manual_review')!r}"
        )
    record_status = _manual_review_flag(record.get("needs_manual_review"))
    if row_status != record_status:
        raise ValueError(
            f"needs_manual_review mismatch for {figure_id!r} in {review_path}: "
            f"csv={row_status!r}, jsonl={record_status!r}"
        )


def load_records(artifact_dir: Path) -> list[dict[str, object]]:
    jsonl_path = artifact_dir / RECORDS_FILENAME
    review_path = artifact_dir / REVIEW_FILENAME

    records = _read_jsonl_records(jsonl_path)
    review_rows = _read_review_rows(review_path)
    records_by_key: dict[tuple[str, str], dict[str, object]] = {}
    for record in records:
        paper_id = str(record.get("paper_id") or "").strip()
        figure_id = str(record.get("figure_id") or "").strip()
        if not paper_id or not figure_id:
            raise ValueError(
                f"{jsonl_path} contains a record with missing paper_id or figure_id"
            )
        record_key = _record_key(paper_id, figure_id)
        if record_key in records_by_key:
            raise ValueError(
                f"{jsonl_path} contains duplicate paper_id/figure_id pair {paper_id!r}/{figure_id!r}"
            )
        records_by_key[record_key] = record

    ordered_records: list[dict[str, object]] = []
    seen_keys: set[tuple[str, str]] = set()
    seen_paper_ids: set[str] = set()

    for row in review_rows:
        paper_id = str(row.get("paper_id") or "").strip()
        figure_id = str(row.get("figure_id") or "").strip()
        if not paper_id:
            raise ValueError(f"missing paper_id in {review_path}")
        if not figure_id:
            raise ValueError(f"missing figure_id in {review_path}")
        record_key = _record_key(paper_id, figure_id)
        if record_key not in records_by_key:
            raise ValueError(
                f"{review_path} references unknown paper_id/figure_id pair {paper_id!r}/{figure_id!r}"
            )
        if record_key in seen_keys:
            raise ValueError(
                f"{review_path} contains duplicate paper_id/figure_id pair {paper_id!r}/{figure_id!r}"
            )
        record = dict(records_by_key[record_key])
        _validate_review_row(record, row, review_path, figure_id)
        ordered_records.append(_normalize_record(artifact_dir, record))
        seen_keys.add(record_key)
        seen_paper_ids.add(paper_id)

    extra_keys = [
        record_key
        for record_key in records_by_key
        if record_key not in seen_keys
    ]
    if extra_keys:
        raise ValueError(
            f"{jsonl_path} contains paper_id/figure_id pairs not listed in {review_path}: "
            f"{', '.join(f'{paper_id}/{figure_id}' for paper_id, figure_id in sorted(extra_keys))}"
        )

    if len(seen_paper_ids) > 1:
        raise ValueError(
            f"{artifact_dir} contains multiple paper_id values: {', '.join(sorted(seen_paper_ids))}"
        )

    return ordered_records


def load_manifest(artifact_dir: Path) -> dict[str, object]:
    manifest_path = artifact_dir / MANIFEST_FILENAME
    with manifest_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{manifest_path} must contain a JSON object")
    return payload


def _escape_text(value: object | None) -> str:
    if value is None:
        return "N/A"
    text = str(value).strip()
    if not text:
        return "N/A"
    return html_escape(text, quote=True)


def _render_empty_or_items(items: list[str]) -> str:
    if not items:
        return '<span class="empty-value">N/A</span>'
    return '<div class="chip-list">' + "".join(
        f'<span class="chip">{html_escape(item, quote=True)}</span>'
        for item in items
    ) + "</div>"


def _render_subfigure_map(subfigure_map: object) -> str:
    if not isinstance(subfigure_map, dict) or not subfigure_map:
        return '<span class="empty-value">N/A</span>'

    rows: list[str] = []
    for key in sorted(subfigure_map.keys(), key=lambda item: str(item).strip().lower()):
        label = html_escape(str(key).strip(), quote=True)
        value = html_escape(str(subfigure_map[key]).strip(), quote=True)
        rows.append(
            '<div class="subfigure-row">'
            f'<span class="subfigure-key">{label}</span>'
            f'<span class="subfigure-value">{value}</span>'
            "</div>"
        )
    return '<div class="subfigure-map-list">' + "".join(rows) + "</div>"


def _render_subfigures_section(record: dict[str, object]) -> str:
    subfigure_map = record.get("subfigure_map")
    panel_labels = [
        str(item).strip()
        for item in record.get("panel_labels", [])
        if str(item).strip()
    ]

    if isinstance(subfigure_map, dict) and subfigure_map:
        body_html = _render_subfigure_map(subfigure_map)
    elif panel_labels:
        body_html = (
            '<div class="subfigure-label-list">'
            + "".join(
                f'<span class="subfigure-label-chip">{html_escape(item, quote=True)}</span>'
                for item in panel_labels
            )
            + "</div>"
        )
    else:
        body_html = (
            '<div class="subfigure-empty">'
            f"{html_escape('No subfigure data available', quote=True)}"
            "</div>"
        )

    return (
        '<section class="subfigures-section" aria-label="Subfigures">'
        '<div class="subfigures-heading">'
        f"<h3>{html_escape('Subfigures', quote=True)}</h3>"
        "</div>"
        f"{body_html}"
        "</section>"
    )


def _render_field(label: str, value_html: str) -> str:
    return (
        '<div class="field-block">'
        f'<div class="field-label">{html_escape(label, quote=True)}</div>'
        f'<div class="field-value">{value_html}</div>'
        "</div>"
    )


def _status_for_record(record: dict[str, object]) -> str:
    return "manual-review" if _manual_review_flag(record.get("needs_manual_review")) else "auto-pass"


def _render_record_card(record: dict[str, object]) -> str:
    status = _status_for_record(record)
    image_src = html_escape(str(record.get("image_path") or ""), quote=True)
    figure_id = _escape_text(record.get("figure_id"))
    card_title = _escape_text(record.get("figure_id"))

    return (
        f'<article class="figure-card" data-status="{status}">'
        '<div class="figure-media">'
        f'<img src="{image_src}" alt="Crop for figure {card_title}">'
        "</div>"
        '<div class="figure-content">'
        '<div class="figure-heading">'
        f"<h2>{card_title}</h2>"
        f'<span class="status-badge">{html_escape(status, quote=True)}</span>'
        "</div>"
        '<div class="field-grid">'
        f"{_render_field('figure_id', figure_id)}"
        f"{_render_field('page_no', _escape_text(record.get('page_no')))}"
        f"{_render_field('figure_type', _escape_text(record.get('figure_type')))}"
        f"{_render_field('confidence', _escape_text(record.get('confidence')))}"
        f"{_render_field('needs_manual_review', html_escape(str(bool(record.get('needs_manual_review'))).lower(), quote=True))}"
        f"{_render_field('caption_text', _escape_text(record.get('caption_text')))}"
        f"{_render_field('recaption', _escape_text(record.get('recaption')))}"
        f"{_render_field('figure_summary', _escape_text(record.get('figure_summary')))}"
        "</div>"
        f"{_render_subfigures_section(record)}"
        "</div>"
        "</article>"
    )


def render_report_html(
    paper_id: str,
    manifest: dict[str, object],
    records: list[dict[str, object]],
    generated_at: str,
) -> str:
    auto_pass_count = sum(1 for record in records if not _manual_review_flag(record.get("needs_manual_review")))
    manual_review_count = len(records) - auto_pass_count
    card_html = "".join(_render_record_card(record) for record in records)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Figure Understanding Report - {html_escape(paper_id, quote=True)}</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4efe4;
      --panel: rgba(255, 253, 248, 0.98);
      --ink: #1f1a14;
      --muted: #6f6558;
      --line: #ddd4c6;
      --shadow: 0 18px 40px rgba(53, 39, 20, 0.08);
      --auto: #20563b;
      --auto-bg: #e5f2ea;
      --manual: #7d321f;
      --manual-bg: #fae7de;
      --chip-bg: #eee4d3;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      color: var(--ink);
      font: 15px/1.55 "Segoe UI", "Aptos", system-ui, sans-serif;
      background:
        radial-gradient(circle at top left, rgba(214, 194, 165, 0.36), transparent 36%),
        radial-gradient(circle at top right, rgba(185, 210, 194, 0.3), transparent 30%),
        linear-gradient(180deg, #fbf8f2 0%, var(--bg) 100%);
    }}

    .page {{
      max-width: 1320px;
      margin: 0 auto;
      padding: 28px 22px 48px;
    }}

    .hero {{
      display: flex;
      gap: 18px;
      justify-content: space-between;
      align-items: end;
      margin-bottom: 22px;
    }}

    .hero h1 {{
      margin: 0;
      font-size: clamp(2rem, 4vw, 3rem);
      line-height: 1.05;
      letter-spacing: -0.04em;
    }}

    .hero p {{
      margin: 8px 0 0;
      color: var(--muted);
      max-width: 68ch;
    }}

    .summary-block {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin-bottom: 24px;
    }}

    .summary-item {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: var(--shadow);
      padding: 14px 16px;
      min-height: 88px;
    }}

    .summary-label {{
      display: block;
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 8px;
    }}

    .summary-value {{
      font-size: 1.18rem;
      font-weight: 700;
      word-break: break-word;
    }}

    .cards {{
      display: grid;
      gap: 18px;
    }}

    .figure-card {{
      display: grid;
      grid-template-columns: minmax(280px, 0.95fr) minmax(0, 1.45fr);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 24px;
      overflow: hidden;
      box-shadow: var(--shadow);
    }}

    .figure-media {{
      background:
        linear-gradient(180deg, rgba(23, 19, 15, 0.06), rgba(23, 19, 15, 0.02)),
        #221d18;
      padding: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .figure-media img {{
      display: block;
      width: 100%;
      max-height: 420px;
      object-fit: contain;
      background: #ffffff;
      border-radius: 14px;
      box-shadow: 0 10px 24px rgba(0, 0, 0, 0.14);
    }}

    .figure-content {{
      padding: 20px 22px 24px;
    }}

    .figure-heading {{
      display: flex;
      gap: 12px;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
    }}

    .figure-heading h2 {{
      margin: 0;
      font-size: 1.35rem;
      letter-spacing: -0.03em;
    }}

    .status-badge {{
      flex: none;
      padding: 6px 12px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      white-space: nowrap;
    }}

    .figure-card[data-status="auto-pass"] .status-badge {{
      background: var(--auto-bg);
      color: var(--auto);
    }}

    .figure-card[data-status="manual-review"] .status-badge {{
      background: var(--manual-bg);
      color: var(--manual);
    }}

    .field-grid {{
      display: grid;
      gap: 14px;
    }}

    .field-block {{
      border-top: 1px solid var(--line);
      padding-top: 12px;
    }}

    .field-block:first-child {{
      border-top: 0;
      padding-top: 0;
    }}

    .field-label {{
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .field-value {{
      overflow-wrap: anywhere;
    }}

    .subfigures-section {{
      margin-top: 18px;
      padding: 16px 16px 18px;
      border: 1px solid rgba(111, 101, 88, 0.18);
      border-radius: 18px;
      background: linear-gradient(180deg, rgba(255, 247, 236, 0.96), rgba(248, 242, 233, 0.94));
      display: grid;
      gap: 12px;
    }}

    .subfigures-heading h3 {{
      margin: 0;
      font-size: 0.98rem;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--muted);
    }}

    .subfigure-map-list {{
      display: grid;
      gap: 10px;
    }}

    .subfigure-row {{
      display: grid;
      grid-template-columns: max-content minmax(0, 1fr);
      gap: 12px;
      align-items: start;
      padding: 10px 12px;
      border-radius: 14px;
      background: rgba(255, 255, 255, 0.75);
      border: 1px solid rgba(221, 212, 198, 0.88);
    }}

    .subfigure-key {{
      font-weight: 700;
      color: var(--ink);
    }}

    .subfigure-value {{
      color: var(--ink);
      overflow-wrap: anywhere;
    }}

    .subfigure-label-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .subfigure-label-chip {{
      display: inline-flex;
      align-items: center;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(32, 86, 59, 0.12);
      color: var(--ink);
      border: 1px solid rgba(32, 86, 59, 0.14);
      font-size: 0.92rem;
      font-weight: 600;
    }}

    .subfigure-empty {{
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px dashed rgba(111, 101, 88, 0.34);
      background: rgba(255, 255, 255, 0.58);
      color: var(--muted);
      font-style: italic;
    }}

    @media (max-width: 920px) {{
      .hero {{
        flex-direction: column;
        align-items: start;
      }}

      .figure-card {{
        grid-template-columns: 1fr;
      }}

      .figure-media img {{
        max-height: 320px;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <header class="hero">
      <div>
        <h1>Figure Understanding Report</h1>
        <p>Static review page for the figure-understanding layer artifacts.</p>
      </div>
    </header>

    <section class="summary-block" aria-label="Report summary">
      <div class="summary-item">
        <span class="summary-label">Paper ID</span>
        <div class="summary-value">{html_escape(paper_id, quote=True)}</div>
      </div>
      <div class="summary-item">
        <span class="summary-label">Figure count</span>
        <div class="summary-value">{len(records)}</div>
      </div>
      <div class="summary-item">
        <span class="summary-label">Auto-pass count</span>
        <div class="summary-value">{auto_pass_count}</div>
      </div>
      <div class="summary-item">
        <span class="summary-label">Manual-review count</span>
        <div class="summary-value">{manual_review_count}</div>
      </div>
      <div class="summary-item">
        <span class="summary-label">Generated at</span>
        <div class="summary-value">{html_escape(generated_at, quote=True)}</div>
      </div>
    </section>

    <main class="cards">
      {card_html}
    </main>
  </div>
</body>
</html>
"""


def write_report_html(output_path: Path, html: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def _infer_paper_id(records: list[dict[str, object]]) -> str:
    paper_ids = sorted(
        {
            str(record.get("paper_id") or "").strip()
            for record in records
            if str(record.get("paper_id") or "").strip()
        }
    )
    if not paper_ids:
        raise ValueError("report requires at least one record with a paper_id")
    if len(paper_ids) > 1:
        raise ValueError(f"report requires exactly one paper_id, found: {', '.join(paper_ids)}")
    return paper_ids[0]


def _copy_report_images(artifact_dir: Path, output_dir: Path, records: list[dict[str, object]]) -> None:
    for record in records:
        image_path_value = str(record.get("image_path") or "").strip()
        if not image_path_value:
            raise ValueError(f"missing image_path for figure {record.get('figure_id')!r}")
        source_path = artifact_dir / Path(image_path_value)
        if not source_path.exists():
            raise FileNotFoundError(f"missing figure crop: {source_path}")
        destination_path = output_dir / Path(image_path_value)
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a static figure-understanding report")
    parser.add_argument("--artifact-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    artifact_dir = args.artifact_dir
    output_dir = args.output_dir

    records = load_records(artifact_dir)
    manifest = load_manifest(artifact_dir)
    paper_id = _infer_paper_id(records)

    _copy_report_images(artifact_dir, output_dir, records)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = render_report_html(paper_id, manifest, records, generated_at)

    output_path = output_dir / "index.html"
    write_report_html(output_path, html)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
