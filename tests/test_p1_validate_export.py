from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from p1_pipeline_common import EVIDENCE_PATH, EVIDENCE_SCHEMA_PATH, SAMPLE_SCHEMA_PATH, SAMPLES_PATH, validate_instance_file  # type: ignore  # noqa: E402


def test_canonical_p1_extracted_outputs_are_schema_valid() -> None:
    assert validate_instance_file(SAMPLES_PATH, SAMPLE_SCHEMA_PATH, "samples") == []
    assert validate_instance_file(EVIDENCE_PATH, EVIDENCE_SCHEMA_PATH, "evidence") == []
