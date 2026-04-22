from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import json
from pathlib import Path


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _optional_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _coerce_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _normalize_string_list(value: object) -> list[str]:
    if not isinstance(value, (list, tuple, set)):
        return []
    values: list[str] = []
    for item in value:
        if item is None:
            continue
        text = str(item).strip()
        if text:
            values.append(text)
    return values


def _normalize_subfigure_map(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}

    normalized: dict[str, str] = {}
    for key in sorted(value.keys(), key=lambda item: str(item).strip().lower()):
        label = str(key).strip().lower()
        if not label:
            continue
        text = _optional_text(value.get(key))
        if text is None:
            continue
        normalized[label] = text
    return normalized


@dataclass(frozen=True)
class FigureRecord:
    paper_id: str
    figure_id: str
    page_no: int | None
    image_path: str
    caption_text: str | None
    context_text: str | None
    panel_labels: list[str]
    subfigure_map: dict[str, str]
    figure_type: str
    recaption: str | None
    figure_summary: str | None
    confidence: float
    needs_manual_review: bool
    source_refs: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def normalize_panel_labels(value: object) -> list[str]:
    if isinstance(value, str):
        items: list[object] = [value]
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        return []

    labels = {
        str(item).strip().lower()
        for item in items
        if item is not None and str(item).strip()
    }
    return sorted(labels)


def build_figure_record(
    raw: dict[str, object],
    interpretation: dict[str, object],
    review_threshold: float,
) -> dict[str, object]:
    confidence = _coerce_float(interpretation.get("confidence"))
    record = FigureRecord(
        paper_id=str(raw["paper_id"]),
        figure_id=str(raw["figure_id"]),
        page_no=_optional_int(raw.get("page_no")),
        image_path=str(raw["image_path"]),
        caption_text=_optional_text(raw.get("caption_text")),
        context_text=_optional_text(raw.get("context_text")),
        panel_labels=normalize_panel_labels(interpretation.get("panel_labels")),
        subfigure_map=_normalize_subfigure_map(interpretation.get("subfigure_map")),
        figure_type=_optional_text(interpretation.get("figure_type")) or "unknown",
        recaption=_optional_text(interpretation.get("recaption")),
        figure_summary=_optional_text(interpretation.get("figure_summary")),
        confidence=confidence,
        needs_manual_review=confidence < review_threshold,
        source_refs=_normalize_string_list(interpretation.get("source_refs")),
    )
    return record.to_dict()


def write_jsonl(records: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False))
            handle.write("\n")


def _review_row(record: dict[str, object]) -> dict[str, object]:
    row = dict(record)
    row["panel_labels"] = ";".join(str(item) for item in record.get("panel_labels", []))
    row["subfigure_map"] = json.dumps(record.get("subfigure_map", {}), ensure_ascii=False)
    row["source_refs"] = ";".join(str(item) for item in record.get("source_refs", []))
    row["needs_manual_review"] = str(bool(record.get("needs_manual_review"))).lower()
    return row


def write_review_csv(records: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "paper_id",
        "figure_id",
        "page_no",
        "image_path",
        "caption_text",
        "context_text",
        "panel_labels",
        "subfigure_map",
        "figure_type",
        "recaption",
        "figure_summary",
        "confidence",
        "needs_manual_review",
        "source_refs",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(_review_row(record))
