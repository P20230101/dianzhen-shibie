from __future__ import annotations

import shutil
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_pdf_register import DEFAULT_LIBRARY_ROOT, build_first_pass_register, build_pdf_register_bundle, extract_register_row  # type: ignore  # noqa: E402


def _paper_pdf(family: str, paper_id: str) -> Path:
    return ROOT / "data" / "01_raw" / "pdfs" / "library" / family / paper_id / "original.pdf"


def test_extract_register_row_uses_first_page_title_when_metadata_is_generic() -> None:
    row = extract_register_row(_paper_pdf("honeycomb", "pii_s0734_743x_97_00040_7"))

    assert row["paper_id"] == "pii_s0734_743x_97_00040_7"
    assert row["family"] == "honeycomb"
    assert row["structure_main_class"] == "honeycomb_2d"
    assert row["status"] == "identified"
    assert row["doi"] == ""
    assert row["title"] == "STATIC AND DYNAMIC PROPERTIES OF HIGH-DENSITY METAL HONEYCOMBS"
    assert row["structure_subtype_list"] == ""


def test_extract_register_row_classifies_hybrid_plate_rod_lattice_from_title() -> None:
    row = extract_register_row(_paper_pdf("lattice", "10_1016_j_ijimpeng_2025_105321"))

    assert row["family"] == "lattice"
    assert row["structure_main_class"] == "hybrid_lattice"
    assert row["status"] == "identified"
    assert row["doi"] == "10.1016/j.ijimpeng.2025.105321"
    assert row["structure_subtype_list"] == "plate_rod;octet"


def test_extract_register_row_classifies_truss_lattice_from_truss_unit_cells() -> None:
    row = extract_register_row(_paper_pdf("lattice", "10_1016_j_cirpj_2024_06_009"))

    assert row["family"] == "lattice"
    assert row["structure_main_class"] == "truss_lattice"
    assert row["status"] == "identified"
    assert row["structure_subtype_list"] == "octet"


def test_extract_register_row_classifies_bionic_honeycomb_spatial_lattice_as_bioinspired() -> None:
    row = extract_register_row(_paper_pdf("lattice", "10_1016_j_ijimpeng_2023_104713"))

    assert row["family"] == "lattice"
    assert row["structure_main_class"] == "bioinspired"
    assert row["status"] == "identified"
    assert row["structure_subtype_list"] == "bionic_honeycomb"


def test_build_first_pass_register_writes_csv_and_markdown() -> None:
    output_dir = ROOT / "tmp" / "pdf_register_extractor_test"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = output_dir / "paper_register_first_pass.csv"
    md_path = output_dir / "paper_register_first_pass.md"

    try:
        rows = build_first_pass_register(DEFAULT_LIBRARY_ROOT, csv_path, md_path)

        assert len(rows) == 17
        assert csv_path.exists()
        assert md_path.exists()
        assert csv_path.read_text(encoding="utf-8").splitlines()[0] == "paper_id,title,doi,family,structure_main_class,structure_subtype_list,status,file_path"
        assert sum(1 for row in rows if row["status"] == "needs_review") == 0
        assert any(row["structure_subtype_list"] for row in rows)
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)


def test_build_pdf_register_bundle_writes_canonical_register() -> None:
    output_dir = ROOT / "tmp" / "pdf_register_bundle_test"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    first_pass_csv = output_dir / "paper_register_first_pass.csv"
    first_pass_md = output_dir / "paper_register_first_pass.md"
    canonical_csv = output_dir / "paper_register.csv"
    canonical_md = output_dir / "paper_register.md"

    try:
        first_pass_rows, canonical_rows = build_pdf_register_bundle(
            DEFAULT_LIBRARY_ROOT,
            first_pass_csv,
            first_pass_md,
            canonical_csv,
            canonical_md,
        )

        assert len(first_pass_rows) == 17
        assert len(canonical_rows) == 17
        assert first_pass_csv.exists()
        assert first_pass_md.exists()
        assert canonical_csv.exists()
        assert canonical_md.exists()
        assert canonical_csv.read_text(encoding="utf-8").splitlines()[0] == "paper_id,family,structure_main_class,structure_subtype_list,title,authors_raw,year,doi,status,source_path,library_path,notes"
        assert next(row for row in canonical_rows if row["paper_id"] == "10_1016_j_ijimpeng_2023_104713")["structure_subtype_list"] == "bionic_honeycomb"
    finally:
        shutil.rmtree(output_dir, ignore_errors=True)
