from __future__ import annotations

import argparse
from dataclasses import dataclass
import base64
import json
from pathlib import Path
import urllib.error
import urllib.request


def _require_mapping(payload: object, context: str) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise TypeError(f"{context} must be a JSON object")
    return payload


def _normalize_response(payload: object) -> dict[str, object]:
    data = _require_mapping(payload, "figure response")
    return data


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
        image_data = Path(image_path).read_bytes()
        encoded_image = base64.b64encode(image_data).decode("ascii")
        request_body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return a JSON object with figure_type, recaption, figure_summary, "
                        "panel_labels, subfigure_map, confidence, and source_refs."
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
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            url=f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(request_body).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"figure VLM request failed: {exc}") from exc

        return self._extract_json_content(payload)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _build_prompt(self, caption_text: str | None, context_text: str | None) -> str:
        parts = [
            "Identify the figure type, panel labels, recaption, and summary.",
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
        return _normalize_response(json.loads(content))


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
