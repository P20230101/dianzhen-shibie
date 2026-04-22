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


def test_fixture_backend_returns_stable_figure_semantics() -> None:
    backend = FixtureFigureInterpreter(Path("tests/fixtures/figure_understanding/mini_vlm_response.json"))
    result = backend.interpret(
        image_path="tests/fixtures/figure_understanding/mini_figure_image.png",
        caption_text="Figure 2. Stress-strain curves under quasi-static compression.",
        context_text="Figure 2 shows the comparison between gyroid and diamond lattices.",
    )

    assert result["figure_type"] == "curve_plot"
    assert result["confidence"] > 0.8
    assert "gyroid" in str(result["figure_summary"]).lower()
    assert result["subfigure_map"] == {
        "a": "gyroid lattice",
        "b": "diamond lattice",
    }


def test_vlm_cli_writes_fixture_json(tmp_path: Path) -> None:
    output_path = tmp_path / "vlm_output.json"

    exit_code = figure_understanding_vlm_main(
        [
            "--image",
            str(ROOT / "tests" / "fixtures" / "figure_understanding" / "mini_figure_image.png"),
            "--caption",
            "Figure 2. Stress-strain curves under quasi-static compression.",
            "--context",
            "The figure compares gyroid and diamond lattice responses under compression.",
            "--fixture-response",
            str(ROOT / "tests" / "fixtures" / "figure_understanding" / "mini_vlm_response.json"),
            "--out",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert exit_code == 0
    assert payload["figure_type"] == "curve_plot"
    assert payload["panel_labels"] == ["b", "a"]
    assert payload["subfigure_map"] == {
        "a": "gyroid lattice",
        "b": "diamond lattice",
    }


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

    assert result["figure_type"]
    assert isinstance(result.get("subfigure_map"), dict)
