from __future__ import annotations

import argparse
from dataclasses import dataclass
import base64
import io
import json
import time
from pathlib import Path
import urllib.error
import urllib.request

try:
    from PIL import Image
except ImportError:  # pragma: no cover - optional runtime dependency
    Image = None


def _require_mapping(payload: object, context: str) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise TypeError(f"{context} must be a JSON object")
    return payload


def _normalize_response(payload: object) -> dict[str, object]:
    data = _require_mapping(payload, "figure response")
    units = data.get("units")
    if not isinstance(units, list) or not units:
        raise ValueError("figure response must include a non-empty units list")
    for index, unit in enumerate(units, start=1):
        if not isinstance(unit, dict):
            raise TypeError(f"figure response unit {index} must be a JSON object")
    return data


def _extract_json_text(content: str) -> dict[str, object]:
    raw = content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:].lstrip()
    try:
        return _normalize_response(json.loads(raw))
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return _normalize_response(json.loads(raw[start : end + 1]))
        raise


def _prepare_image_bytes(image_path: str) -> bytes:
    raw_bytes = Path(image_path).read_bytes()
    if Image is None:
        return raw_bytes

    with Image.open(io.BytesIO(raw_bytes)) as image:
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGB")
        else:
            image = image.convert("RGB")
        max_edge = 1536
        if max(image.size) > max_edge:
            image.thumbnail((max_edge, max_edge))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()


def _figure_response_schema() -> dict[str, object]:
    return {
        "name": "figure_unit_response",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "units": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "properties": {
                            "panel_label": {"type": "string"},
                            "kind": {"type": "string"},
                            "crop_bbox": {
                                "type": "object",
                                "properties": {
                                    "l": {"type": "number"},
                                    "t": {"type": "number"},
                                    "r": {"type": "number"},
                                    "b": {"type": "number"},
                                },
                                "required": ["l", "t", "r", "b"],
                                "additionalProperties": False,
                            },
                            "figure_type": {"type": "string"},
                            "recaption": {"type": "string"},
                            "figure_summary": {"type": "string"},
                            "confidence": {"type": "number"},
                            "source_refs": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": [
                            "panel_label",
                            "kind",
                            "crop_bbox",
                            "figure_type",
                            "recaption",
                            "figure_summary",
                            "confidence",
                            "source_refs",
                        ],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["units"],
            "additionalProperties": False,
        },
    }


@dataclass(frozen=True)
class FixtureFigureInterpreter:
    response_path: Path

    def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
        payload = json.loads(self.response_path.read_text(encoding="utf-8"))
        return _normalize_response(payload)


@dataclass(frozen=True)
class VlmFigureInterpreter:
    base_url: str
    model: str
    api_key: str | None = None
    timeout_s: float = 60.0

    def interpret(self, image_path: str, caption_text: str | None, context_text: str | None) -> dict[str, object]:
        prompt = self._build_prompt(caption_text, context_text)
        image_data = _prepare_image_bytes(image_path)
        encoded_image = base64.b64encode(image_data).decode("ascii")
        request_body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return a JSON object with a non-empty units array. "
                        "Each unit must include panel_label, kind, crop_bbox, figure_type, recaption, "
                        "figure_summary, confidence, and source_refs."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{encoded_image}"},
                        },
                    ],
                },
            ],
            "temperature": 0,
            "response_format": {
                "type": "json_schema",
                "json_schema": _figure_response_schema(),
            },
        }
        request = urllib.request.Request(
            url=f"{self.base_url.rstrip('/')}/v1/chat/completions",
            data=json.dumps(request_body).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        last_error: Exception | None = None
        for attempt in range(5):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                return self._extract_json_content(payload)
            except urllib.error.URLError as exc:
                last_error = exc
            except ValueError as exc:
                last_error = exc
            if attempt < 4:
                time.sleep(2.0 * (attempt + 1))
        if last_error is not None:
            raise RuntimeError(f"figure VLM request failed: {last_error}") from last_error
        raise RuntimeError("figure VLM request failed")

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_prompt(self, caption_text: str | None, context_text: str | None) -> str:
        parts = [
            "Split the figure into independently crop-able units and describe each unit.",
            "Return one unit object per visible panel or standalone figure region.",
            "For each unit, provide panel_label, kind, crop_bbox, figure_type, recaption, figure_summary, confidence, and source_refs.",
        ]
        if caption_text:
            parts.append(f"Caption: {caption_text}")
        if context_text:
            parts.append(f"Context: {context_text}")
        return "\n".join(parts)

    def _extract_json_content(self, payload: dict[str, object]) -> dict[str, object]:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("VLM response is missing choices")
        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise TypeError("VLM response choice must be a JSON object")
        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise TypeError("VLM response message must be a JSON object")
        content = message.get("content")
        if isinstance(content, dict):
            return _normalize_response(content)
        if not isinstance(content, str):
            raise TypeError("VLM response content must be text or JSON")
        return _extract_json_text(content)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a single figure understanding interpretation")
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--caption")
    parser.add_argument("--context")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--fixture-response", type=Path)
    parser.add_argument("--base-url")
    parser.add_argument("--model")
    parser.add_argument("--api-key")
    parser.add_argument("--timeout-s", type=float, default=60.0)
    return parser


def _build_interpreter(args: argparse.Namespace) -> FixtureFigureInterpreter | VlmFigureInterpreter:
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


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    interpreter = _build_interpreter(args)

    result = interpreter.interpret(
        image_path=str(args.image),
        caption_text=args.caption,
        context_text=args.context,
    )

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
