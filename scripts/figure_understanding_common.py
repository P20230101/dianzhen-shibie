from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import json
import re
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


def _normalize_panel_label(value: object) -> str | None:
    text = _optional_text(value)
    if text is None:
        return None
    normalized = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return normalized or None


def _normalize_crop_bbox(value: object) -> dict[str, int]:
    if not isinstance(value, dict):
        raise ValueError("crop_bbox must be a mapping")

    normalized: dict[str, int] = {}
    for key in ("l", "t", "r", "b"):
        coordinate = value.get(key)
        if isinstance(coordinate, bool) or not isinstance(coordinate, (int, float)):
            raise ValueError(f"crop_bbox[{key!r}] must be numeric")
        normalized[key] = int(round(float(coordinate)))

    if normalized["r"] <= normalized["l"] or normalized["b"] <= normalized["t"]:
        raise ValueError("crop_bbox must define a non-empty rectangle")
    return normalized


def _normalize_kind(value: object) -> str:
    text = _optional_text(value)
    return text.lower() if text is not None else "panel"


def _normalize_figure_type(value: object) -> str:
    text = _optional_text(value)
    return text.lower() if text is not None else "unknown"


def _source_page_no(raw: dict[str, object]) -> int | None:
    for key in ("source_page_no", "page_no"):
        value = _optional_int(raw.get(key))
        if value is not None:
            return value
    return None


@dataclass(frozen=True)
class FigureUnitRecord:
    paper_id: str
    source_figure_id: str
    unit_id: str
    unit_index: int
    kind: str
    panel_label: str | None
    source_page_no: int | None
    source_image_path: str
    image_path: str
    crop_bbox: dict[str, int]
    caption_text: str | None
    context_text: str | None
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


def build_unit_record(
    raw: dict[str, object],
    interpretation: dict[str, object],
    review_threshold: float,
) -> dict[str, object]:
    confidence = _coerce_float(interpretation.get("confidence"))
    caption_text = _optional_text(raw.get("caption_text"))
    context_text = _optional_text(raw.get("context_text"))

    paper_id = _optional_text(raw.get("paper_id"))
    source_figure_id = _optional_text(raw.get("source_figure_id") or raw.get("figure_id"))
    unit_id = _optional_text(raw.get("unit_id"))
    unit_index = _optional_int(raw.get("unit_index"))
    source_image_path = _optional_text(raw.get("source_image_path"))
    image_path = _optional_text(raw.get("image_path"))

    if paper_id is None:
        raise ValueError("raw unit record is missing paper_id")
    if source_figure_id is None:
        raise ValueError("raw unit record is missing source_figure_id")
    if unit_id is None:
        raise ValueError("raw unit record is missing unit_id")
    if unit_index is None:
        raise ValueError("raw unit record is missing unit_index")
    if source_image_path is None:
        raise ValueError("raw unit record is missing source_image_path")
    if image_path is None:
        raise ValueError("raw unit record is missing image_path")

    record = FigureUnitRecord(
        paper_id=paper_id,
        source_figure_id=source_figure_id,
        unit_id=unit_id,
        unit_index=unit_index,
        kind=_normalize_kind(raw.get("kind")),
        panel_label=_normalize_panel_label(raw.get("panel_label")),
        source_page_no=_source_page_no(raw),
        source_image_path=source_image_path,
        image_path=image_path,
        crop_bbox=_normalize_crop_bbox(raw.get("crop_bbox")),
        caption_text=caption_text,
        context_text=context_text,
        figure_type=_normalize_figure_type(interpretation.get("figure_type")),
        recaption=_optional_text(interpretation.get("recaption")),
        figure_summary=_optional_text(interpretation.get("figure_summary")),
        confidence=confidence,
        needs_manual_review=confidence < review_threshold or caption_text is None or context_text is None,
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
    row["crop_bbox"] = json.dumps(record.get("crop_bbox", {}), ensure_ascii=False)
    row["source_refs"] = ";".join(str(item) for item in record.get("source_refs", []))
    row["needs_manual_review"] = str(bool(record.get("needs_manual_review"))).lower()
    return row


def write_review_csv(records: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "paper_id",
        "source_figure_id",
        "unit_id",
        "unit_index",
        "kind",
        "panel_label",
        "source_page_no",
        "source_image_path",
        "image_path",
        "crop_bbox",
        "caption_text",
        "context_text",
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
