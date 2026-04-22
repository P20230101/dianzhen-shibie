from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from figure_understanding_vlm import FixtureFigureInterpreter  # type: ignore  # noqa: E402


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
