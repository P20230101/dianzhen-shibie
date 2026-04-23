from __future__ import annotations

import json
import os
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from figure_understanding_vlm import FixtureFigureInterpreter  # type: ignore  # noqa: E402
from figure_understanding_vlm import main as figure_understanding_vlm_main  # type: ignore  # noqa: E402


def _write_fixture_response(tmp_path: Path) -> Path:
    response_path = tmp_path / "unit_vlm_response.json"
    response = {
        "units": [
            {
                "panel_label": "a",
                "kind": "panel",
                "crop_bbox": {"l": 0, "t": 0, "r": 4, "b": 4},
                "figure_type": "curve_plot",
                "recaption": "Panel a shows the stress-strain response.",
                "figure_summary": "The left half shows the response curve.",
                "confidence": 0.92,
                "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:3", "figure:fig_001"],
            },
            {
                "panel_label": "b",
                "kind": "panel",
                "crop_bbox": {"l": 4, "t": 0, "r": 8, "b": 4},
                "figure_type": "curve_plot",
                "recaption": "Panel b shows the deformed specimen.",
                "figure_summary": "The right half shows the post-compression state.",
                "confidence": 0.90,
                "source_refs": ["paper:10_1016_j_addma_2022_102887", "page:3", "figure:fig_001"],
            },
        ]
    }
    response_path.write_text(json.dumps(response, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return response_path


def test_fixture_backend_returns_stable_unit_semantics(tmp_path: Path) -> None:
    backend = FixtureFigureInterpreter(_write_fixture_response(tmp_path))
    result = backend.interpret(
        image_path="tests/fixtures/figure_understanding/mini_figure_image.png",
        caption_text="Figure 2. Stress-strain curves under quasi-static compression.",
        context_text="Figure 2 shows the comparison between gyroid and diamond lattices.",
    )

    assert isinstance(result.get("units"), list)
    assert len(result["units"]) == 2
    assert result["units"][0]["panel_label"] == "a"
    assert result["units"][0]["crop_bbox"] == {"l": 0, "t": 0, "r": 4, "b": 4}
    assert result["units"][1]["panel_label"] == "b"


def test_vlm_cli_writes_fixture_json(tmp_path: Path) -> None:
    output_path = tmp_path / "vlm_output.json"
    fixture_response = _write_fixture_response(tmp_path)

    exit_code = figure_understanding_vlm_main(
        [
            "--image",
            str(ROOT / "tests" / "fixtures" / "figure_understanding" / "mini_figure_image.png"),
            "--caption",
            "Figure 2. Stress-strain curves under quasi-static compression.",
            "--context",
            "The figure compares gyroid and diamond lattice responses under compression.",
            "--fixture-response",
            str(fixture_response),
            "--out",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert isinstance(payload["units"], list)
    assert payload["units"][0]["figure_type"] == "curve_plot"
    assert payload["units"][0]["panel_label"] == "a"
    assert payload["units"][1]["panel_label"] == "b"


@pytest.mark.skipif(
    not (
        (ROOT / "tests" / "fixtures" / "figure_understanding" / "mini_figure_image.png").exists()
        and bool(os.environ.get("FIGURE_VLM_BASE_URL"))
        and bool(os.environ.get("FIGURE_VLM_MODEL"))
    ),
    reason="live figure VLM backend not configured",
)
def test_live_vlm_backend_is_callable() -> None:
    from figure_understanding_vlm import VlmFigureInterpreter  # type: ignore  # noqa: E402

    backend = VlmFigureInterpreter(
        base_url=os.environ["FIGURE_VLM_BASE_URL"],
        model=os.environ["FIGURE_VLM_MODEL"],
        api_key=os.environ.get("FIGURE_VLM_API_KEY"),
        timeout_s=float(os.environ.get("FIGURE_VLM_TIMEOUT_S", "60")),
    )

    result = backend.interpret(
        image_path=str(ROOT / "tests" / "fixtures" / "figure_understanding" / "mini_figure_image.png"),
        caption_text="Figure 2. Stress-strain curves under quasi-static compression.",
        context_text="The figure compares gyroid and diamond lattice responses under compression.",
    )

    assert isinstance(result.get("units"), list)
