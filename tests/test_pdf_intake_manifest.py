from __future__ import annotations

import shutil
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_pdf_intake_manifest import build_pdf_intake_manifest  # type: ignore  # noqa: E402


def test_build_pdf_intake_manifest_writes_page_counts_and_excerpts() -> None:
    output_dir = ROOT / "tmp" / "pdf_intake_manifest_test"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "pdf_intake_manifest.json"

    try:
        manifest = build_pdf_intake_manifest(output_path=manifest_path)

        assert len(manifest) == 17
        assert manifest_path.exists()

        target = next(row for row in manifest if row["paper_id"] == "10_1016_j_ijimpeng_2023_104713")
        assert target["family"] == "lattice"
        assert target["structure_main_class"] == "bioinspired"
        assert target["structure_subtype_list"] == ["bionic_honeycomb"]
        assert target["page_count"] == 15
        assert isinstance(target["first_page_excerpt"], str)
        assert "Crashworthiness analysis" in target["first_page_excerpt"]
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
