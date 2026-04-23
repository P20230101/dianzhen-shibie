from __future__ import annotations

import argparse
import base64
import csv
from functools import lru_cache
import re
from pathlib import Path
from typing import Callable, Protocol

from PIL import Image

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from figure_understanding_common import build_unit_record, write_jsonl, write_review_csv
from figure_understanding_vlm import FixtureFigureInterpreter, VlmFigureInterpreter
from retrieval_kg_common import write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTER_PATH = ROOT / "data" / "01_raw" / "pdfs" / "paper_register.csv"
DEFAULT_LIBRARY_ROOT = ROOT / "data" / "01_raw" / "pdfs" / "library"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "03_figures" / "figure_units_v1.jsonl"
DEFAULT_MANIFEST_PATH = ROOT / "data" / "03_figures" / "manifest.json"
DEFAULT_REVIEW_PATH = ROOT / "data" / "03_figures" / "figure_units_review.csv"
CAPTION_LINE_RE = re.compile(r"^(?:Fig\.|Figure)\s*\d+\.")


class FigureInterpreter(Protocol):
    def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
        ...


@lru_cache(maxsize=1)
def _converter() -> DocumentConverter:
    pipeline_options = PdfPipelineOptions(
        do_ocr=True,
        force_backend_text=True,
        generate_page_images=True,
        generate_picture_images=True,
        do_picture_classification=False,
        do_picture_description=False,
        do_chart_extraction=False,
        do_code_enrichment=False,
        do_formula_enrichment=False,
    )
    return DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)},
    )


def _load_register_rows(register_path: Path) -> list[dict[str, str]]:
    with register_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def _resolve_register_pdf_path(row: dict[str, str]) -> str | None:
    for key in ("pdf_path", "source_path", "library_path", "file_path"):
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return None


def _resolve_caption_text(picture: dict[str, object], texts: list[dict[str, object]]) -> str | None:
    caption_parts: list[str] = []
    captions = picture.get("captions")
    if isinstance(captions, list):
        for item in captions:
            if isinstance(item, dict):
                ref = item.get("$ref")
                if isinstance(ref, str):
                    resolved = _resolve_text_ref(ref, texts)
                    if resolved:
                        caption_parts.append(resolved)
                    continue
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    caption_parts.append(text.strip())
                    continue
            if isinstance(item, str) and item.strip():
                caption_parts.append(item.strip())

    if caption_parts:
        return " ".join(caption_parts).strip()

    for key in ("caption_text", "caption", "text"):
        value = picture.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    page_no = _resolve_page_no(picture)
    picture_bbox = _resolve_bbox(picture)
    if page_no is not None and picture_bbox is not None:
        recovered = _recover_caption_from_page_texts(page_no, picture_bbox, texts)
        if recovered:
            return recovered
    return None


def _resolve_text_ref(ref: str, texts: list[dict[str, object]]) -> str | None:
    if not ref.startswith("#/texts/"):
        return None
    index_text = ref.rsplit("/", 1)[-1]
    try:
        index = int(index_text)
    except ValueError:
        return None
    if index < 0 or index >= len(texts):
        return None
    candidate = texts[index]
    text = candidate.get("text")
    if isinstance(text, str):
        stripped = text.strip()
        if stripped:
            return stripped
    return None


def _resolve_context_text(picture: dict[str, object], caption_text: str | None) -> str | None:
    for key in ("description", "context_text", "summary", "text"):
        value = picture.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return caption_text


def _resolve_page_no(picture: dict[str, object]) -> int | None:
    prov = picture.get("prov")
    if not isinstance(prov, list) or not prov:
        return None
    first = prov[0]
    if not isinstance(first, dict):
        return None
    page_no = first.get("page_no")
    if isinstance(page_no, bool):
        return None
    if isinstance(page_no, int):
        return page_no
    return None


def _resolve_bbox(item: dict[str, object]) -> dict[str, object] | None:
    prov = item.get("prov")
    if not isinstance(prov, list) or not prov:
        return None
    first = prov[0]
    if not isinstance(first, dict):
        return None
    bbox = first.get("bbox")
    if isinstance(bbox, dict):
        return bbox
    return None


def _resolve_image_size(item: dict[str, object]) -> tuple[float, float] | None:
    image = item.get("image")
    if not isinstance(image, dict):
        return None
    size = image.get("size")
    if not isinstance(size, dict):
        return None
    width = size.get("width")
    height = size.get("height")
    if isinstance(width, (int, float)) and isinstance(height, (int, float)):
        return float(width), float(height)
    return None


def _caption_distance(
    picture_bbox: dict[str, object],
    caption_bbox: dict[str, object],
) -> float | None:
    picture_top = picture_bbox.get("t")
    picture_bottom = picture_bbox.get("b")
    caption_top = caption_bbox.get("t")
    caption_bottom = caption_bbox.get("b")
    if not all(isinstance(value, (int, float)) for value in (picture_top, picture_bottom, caption_top, caption_bottom)):
        return None

    if caption_top <= picture_bottom:
        return float(picture_bottom - caption_top)
    if caption_bottom >= picture_top:
        return float(caption_bottom - picture_top)
    return 0.0


def _recover_caption_from_page_texts(
    page_no: int,
    picture_bbox: dict[str, object],
    texts: list[dict[str, object]],
) -> str | None:
    candidates: list[tuple[float, str]] = []
    for item in texts:
        if not isinstance(item, dict):
            continue
        if _resolve_page_no(item) != page_no:
            continue
        text = item.get("text")
        if not isinstance(text, str):
            continue
        stripped = " ".join(text.split())
        if not stripped or not CAPTION_LINE_RE.match(stripped):
            continue
        caption_bbox = _resolve_bbox(item)
        if caption_bbox is None:
            continue
        distance = _caption_distance(picture_bbox, caption_bbox)
        if distance is None:
            continue
        if distance <= 220.0:
            candidates.append((distance, stripped))

    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def _should_skip_page_one_noise(
    picture: dict[str, object],
    page_no: int | None,
    caption_text: str | None,
    context_text: str | None,
) -> bool:
    if page_no != 1 or caption_text is not None or context_text is not None:
        return False
    size = _resolve_image_size(picture)
    if size is None:
        return False
    width, height = size
    return max(width, height) <= 80.0


def _resolve_image_path(picture: dict[str, object]) -> str:
    for key in ("image_path", "image_uri", "image_file"):
        value = picture.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    image = picture.get("image")
    if isinstance(image, dict):
        uri = image.get("uri")
        if isinstance(uri, str) and uri.startswith("data:"):
            raise ValueError("picture image URI must be materialized before resolving path")
    raise ValueError("picture is missing image_path/image_uri/image_file")


def _materialize_picture_image(
    picture: dict[str, object],
    paper_id: str,
    figure_id: str,
    image_output_root: Path,
) -> str | None:
    image = picture.get("image")
    if not isinstance(image, dict):
        return None
    uri = image.get("uri")
    if not isinstance(uri, str) or not uri.startswith("data:"):
        return None
    header, _, payload = uri.partition(",")
    if not payload:
        return None
    mimetype = str(image.get("mimetype") or "image/png").strip()
    suffix = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/webp": ".webp",
    }.get(mimetype, ".png")
    target_dir = image_output_root / paper_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{figure_id}{suffix}"
    target_path.write_bytes(base64.b64decode(payload))
    return str(target_path)


def _normalize_unit_label(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    cleaned = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return cleaned or None


def _build_unit_id(source_figure_id: str, panel_label: object, unit_index: int, unit_count: int) -> str:
    normalized_label = _normalize_unit_label(panel_label)
    if normalized_label is not None:
        return f"{source_figure_id}_{normalized_label}"
    return f"{source_figure_id}_u{unit_index:02d}"


def _normalize_crop_bbox(
    bbox: object,
    image_width: int,
    image_height: int,
) -> dict[str, int]:
    if not isinstance(bbox, dict):
        raise ValueError("unit crop_bbox must be a mapping")

    raw_values: dict[str, float] = {}
    for key in ("l", "t", "r", "b"):
        value = bbox.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"unit crop_bbox[{key!r}] must be numeric")
        raw_values[key] = float(value)

    if all(0.0 <= value <= 1.0 for value in raw_values.values()):
        scaled = {
            "l": raw_values["l"] * float(image_width),
            "t": raw_values["t"] * float(image_height),
            "r": raw_values["r"] * float(image_width),
            "b": raw_values["b"] * float(image_height),
        }
    else:
        scaled = dict(raw_values)

    normalized = {
        "l": int(round(max(0.0, min(scaled["l"], float(image_width))))),
        "t": int(round(max(0.0, min(scaled["t"], float(image_height))))),
        "r": int(round(max(0.0, min(scaled["r"], float(image_width))))),
        "b": int(round(max(0.0, min(scaled["b"], float(image_height))))),
    }
    if normalized["r"] <= normalized["l"] or normalized["b"] <= normalized["t"]:
        raise ValueError("unit crop_bbox must define a non-empty rectangle")
    return normalized


def _write_unit_crop(source_path: Path, target_path: Path, crop_bbox: dict[str, int]) -> None:
    with Image.open(source_path) as source_image:
        cropped = source_image.crop((crop_bbox["l"], crop_bbox["t"], crop_bbox["r"], crop_bbox["b"]))
        target_path.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(target_path)


def _export_payload(document: object) -> dict[str, object]:
    if hasattr(document, "export_to_dict"):
        payload = document.export_to_dict()
    else:
        payload = document
    if not isinstance(payload, dict):
        raise TypeError("document export must be a dictionary")
    return payload


def extract_figures(
    document: object,
    paper_id: str,
    source_path: str,
    interpreter: FigureInterpreter,
    review_threshold: float,
    image_output_root: Path | None = None,
) -> list[dict[str, object]]:
    payload = _export_payload(document)
    texts = payload.get("texts", [])
    pictures = payload.get("pictures", [])
    if not isinstance(texts, list):
        texts = []
    if not isinstance(pictures, list):
        pictures = []
    if image_output_root is None:
        raise ValueError("image_output_root is required for unit crop output")

    records: list[dict[str, object]] = []
    for index, item in enumerate(pictures, start=1):
        if not isinstance(item, dict):
            continue
        figure_id = str(item.get("figure_id") or f"fig_{index:03d}")
        page_no = _resolve_page_no(item)
        image_path = None
        try:
            image_path = _resolve_image_path(item)
        except ValueError:
            image_path = _materialize_picture_image(item, paper_id, figure_id, image_output_root)
        if not image_path:
            raise ValueError("picture is missing image_path/image_uri/image_file")
        caption_text = _resolve_caption_text(item, texts)
        context_text = _resolve_context_text(item, caption_text)
        if _should_skip_page_one_noise(item, page_no, caption_text, context_text):
            continue
        interpretation = interpreter.interpret(
            image_path=image_path,
            caption_text=caption_text,
            context_text=context_text,
        )
        units = interpretation.get("units")
        if not isinstance(units, list) or not units:
            raise ValueError("figure interpretation must include a non-empty units list")

        with Image.open(image_path) as source_image:
            source_width, source_height = source_image.size

        for unit_index, unit in enumerate(units, start=1):
            if not isinstance(unit, dict):
                raise TypeError("each unit interpretation must be a JSON object")

            unit_id = _build_unit_id(figure_id, unit.get("panel_label"), unit_index, len(units))
            crop_bbox = _normalize_crop_bbox(unit.get("crop_bbox"), source_width, source_height)
            unit_image_path = image_output_root / paper_id / f"{unit_id}.png"
            _write_unit_crop(Path(image_path), unit_image_path, crop_bbox)

            raw = {
                "paper_id": paper_id,
                "source_figure_id": figure_id,
                "unit_id": unit_id,
                "unit_index": unit_index,
                "kind": unit.get("kind"),
                "panel_label": unit.get("panel_label"),
                "source_page_no": page_no,
                "source_image_path": image_path,
                "image_path": str(unit_image_path),
                "crop_bbox": crop_bbox,
                "caption_text": caption_text,
                "context_text": context_text,
            }
            records.append(build_unit_record(raw, unit, review_threshold))
    return records


def _load_document(document_provider: Callable[[Path], object] | None, pdf_path: Path) -> object:
    if document_provider is not None:
        return document_provider(pdf_path)
    conversion_result = _converter().convert(str(pdf_path))
    document = getattr(conversion_result, "document", conversion_result)
    return document


def build_figure_understanding_corpus(
    register_path: Path,
    library_root: Path,
    output_path: Path,
    manifest_path: Path,
    review_path: Path,
    interpreter: FigureInterpreter,
    review_threshold: float = 0.8,
    document_provider: Callable[[Path], object] | None = None,
) -> list[dict[str, object]]:
    rows = _load_register_rows(register_path)
    records: list[dict[str, object]] = []
    paper_ids: list[str] = []
    image_output_root = output_path.parent / "images"

    for row in rows:
        paper_id = str(row.get("paper_id") or "").strip()
        pdf_path_value = _resolve_register_pdf_path(row)
        if not paper_id or not pdf_path_value:
            continue
        pdf_path = Path(pdf_path_value)
        if not pdf_path.is_absolute():
            pdf_path = library_root / pdf_path
        paper_ids.append(paper_id)
        document = _load_document(document_provider, pdf_path)
        records.extend(
            extract_figures(
                document=document,
                paper_id=paper_id,
                source_path=str(pdf_path),
                interpreter=interpreter,
                review_threshold=review_threshold,
                image_output_root=image_output_root,
            )
        )

    write_jsonl(records, output_path)
    write_review_csv(records, review_path)
    write_json(
        manifest_path,
        {
            "register_path": str(register_path),
            "library_root": str(library_root),
            "output_path": str(output_path),
            "image_output_root": str(image_output_root),
            "review_path": str(review_path),
            "paper_count": len(set(paper_ids)),
            "source_figure_count": len({str(record.get("source_figure_id") or "").strip() for record in records if str(record.get("source_figure_id") or "").strip()}),
            "unit_count": len(records),
            "paper_ids": sorted(set(paper_ids)),
        },
    )
    return records


def _build_interpreter(args: argparse.Namespace) -> FigureInterpreter:
    fixture_response = getattr(args, "fixture_response", None)
    if fixture_response is not None:
        return FixtureFigureInterpreter(Path(fixture_response))

    base_url = getattr(args, "base_url", None)
    model = getattr(args, "model", None)
    if not base_url or not model:
        raise SystemExit("provide either --fixture-response or both --base-url and --model")
    return VlmFigureInterpreter(
        base_url=str(base_url),
        model=str(model),
        api_key=getattr(args, "api_key", None),
        timeout_s=float(getattr(args, "timeout_s", 60.0)),
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the figure understanding corpus from canonical PDF inputs")
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER_PATH)
    parser.add_argument("--library-root", type=Path, default=DEFAULT_LIBRARY_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    parser.add_argument("--review-threshold", type=float, default=0.8)
    parser.add_argument("--fixture-response", type=Path)
    parser.add_argument("--base-url")
    parser.add_argument("--model")
    parser.add_argument("--api-key")
    parser.add_argument("--timeout-s", type=float, default=60.0)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    interpreter = _build_interpreter(args)

    records = build_figure_understanding_corpus(
        register_path=args.register,
        library_root=args.library_root,
        output_path=args.output,
        manifest_path=args.manifest,
        review_path=args.review,
        interpreter=interpreter,
        review_threshold=float(args.review_threshold),
    )
    print(f"figure unit records written: {len(records)} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
