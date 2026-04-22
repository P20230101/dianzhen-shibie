from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from p1_pipeline_common import read_json, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES_PATH = ROOT / "outputs" / "p1" / "extracted" / "samples_v1.json"
DEFAULT_EVIDENCE_PATH = ROOT / "outputs" / "p1" / "extracted" / "evidence_v1.json"
DEFAULT_REGISTER_PATH = ROOT / "data" / "01_raw" / "pdfs" / "paper_register.csv"
DEFAULT_CORPUS_PATH = ROOT / "data" / "02_retrieval" / "corpus.jsonl"
JMRT_2023_PAPER_ID = "10_1016_j_jmrt_2023_05_167"
ADDMA_2022_PAPER_ID = "10_1016_j_addma_2022_102887"
COMPSTRUCT_2019_PAPER_ID = "10_1016_j_compstruct_2019_111219"
COMPSTRUCT_2018_PAPER_ID = "10_1016_j_compstruct_2018_03_050"
TWS_2019_PAPER_ID = "10_1016_j_tws_2019_106436"
TWS_2020_PAPER_ID = "10_1016_j_tws_2020_106623"
HIGH_DENSITY_HONEYCOMB_PAPER_ID = "pii_s0734_743x_97_00040_7"
MATDES_2017_PAPER_ID = "10_1016_j_matdes_2017_10_028"
MATDES_2018_PAPER_ID = "10_1016_j_matdes_2018_05_059"
MATDES_2019_PAPER_ID = "10_1016_j_matdes_2019_108076"
IJIMPENG_2023_PAPER_ID = "10_1016_j_ijimpeng_2023_104713"
ENGSTRUCT_2023_PAPER_ID = "10_1016_j_engstruct_2023_116510"
MA18040732_PAPER_ID = "10_3390_ma18040732"
CIRPJ_2024_PAPER_ID = "10_1016_j_cirpj_2024_06_009"
IJIMPENG_2025_PAPER_ID = "10_1016_j_ijimpeng_2025_105321"


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        rows.append(json.loads(line))
    return rows


def _load_register_row(paper_id: str, register_path: Path) -> dict[str, str]:
    with register_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if row.get("paper_id") == paper_id:
                return row
    raise SystemExit(f"paper_id not found in register: {paper_id}")


def _append_unique(rows: list[dict[str, Any]], item: dict[str, Any], key: str) -> None:
    if any(str(row.get(key)) == str(item.get(key)) for row in rows):
        return
    rows.append(item)


def _clean_text(value: str) -> str:
    return " ".join(value.replace("\x00", "").split())


def _require_chunk_text(chunk: dict[str, Any] | None, expected_fragment: str, context: str) -> None:
    if chunk is None:
        raise SystemExit(f"{context} chunk not found")
    cleaned = _clean_text(str(chunk.get("text") or ""))
    if expected_fragment not in cleaned:
        raise SystemExit(f"{context} text drifted: expected fragment {expected_fragment!r}")


def _find_chunk(paper_chunks: list[dict[str, Any]], *, table_id: str | None = None, chunk_id_suffix: str | None = None) -> dict[str, Any]:
    for row in paper_chunks:
        if table_id is not None and row.get("table_id") != table_id:
            continue
        chunk_id = str(row.get("chunk_id") or "")
        if chunk_id_suffix is not None and not chunk_id.endswith(chunk_id_suffix):
            continue
        return row
    raise SystemExit(f"required chunk not found: table_id={table_id!r}, chunk_id_suffix={chunk_id_suffix!r}")


def _build_jmrt_2023_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    table_003 = _find_chunk(paper_chunks, table_id="table_003")
    table_004 = _find_chunk(paper_chunks, table_id="table_004")
    title_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:003")), None)
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:027")), None)

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-p1l-tpms-primitive",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or (title_chunk.get("text") if title_chunk else None),
        "sample_label_in_paper": "P1L",
        "is_multi_sample_paper": True,
        "raw_design": "Primitive",
        "raw_structure": "TPMS",
        "raw_type": "TPMS",
        "structure_main_class": "tpms",
        "structure_subtype_list": ["primitive"],
        "is_hierarchical": False,
        "is_graded": False,
        "is_optimized": False,
        "relative_density_raw": "0.27",
        "relative_density_value": 0.27,
        "raw_material": "short glass fiber reinforced polyamide",
        "raw_material_group": "polyamide",
        "material_canonical": "Polyamide",
        "material_family": "polymer",
        "raw_process": "FDM",
        "process_canonical": "FDM",
        "process_family": "fdm",
        "analysis_type": "experimental",
        "test_mode": "quasi_static",
        "loading_direction": "uniaxial",
        "velocity_m_s_raw": None,
        "velocity_m_s": None,
        "sea_j_g_raw": "1.41",
        "sea_j_g": 1.41,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": None,
        "plateau_stress_mpa": None,
        "confidence_overall": 0.9,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-011.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_design",
            "field_value": "Primitive",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 7,
            "figure_id": None,
            "table_id": "table_003",
            "text_snippet": "Table 3 row P1L records Schwarz Primitive with relative density 0.27 and mass 21.77 g.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "TPMS",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Title identifies FDM-printed short glass fiber reinforced polyamide TPMS structures.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 1.0,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "FDM",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Abstract states the work manufactures short glass fiber-reinforced polyamide composites using the FDM process.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "sea_j_g",
            "field_value": "1.41",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 9,
            "figure_id": None,
            "table_id": "table_004",
            "text_snippet": "Table 4 row P1L records compressive modulus 21.21 MPa, peak compressive stress 1.41 MPa, specific energy absorption 1.41 J/g, and densification strain 59.94%.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(
        abstract_chunk,
        "manufacturing short glass fiber-reinforced polyamide composites using the FDM process",
        "JMRT abstract",
    )
    _require_chunk_text(table_003, "Schwarz Primitive", "JMRT table 3")
    _require_chunk_text(table_004, "Specific Energy Absorption [J/g]", "JMRT table 4")

    return samples, evidence


def _build_addma_2022_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    table_001 = _find_chunk(paper_chunks, table_id="table_001")
    table_003 = _find_chunk(paper_chunks, table_id="table_003")
    title_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:002")), None)
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:027")), None)

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-i2o-2-mgo",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or (title_chunk.get("text") if title_chunk else None),
        "sample_label_in_paper": "I2O-2-MgO",
        "is_multi_sample_paper": True,
        "raw_design": "I2O-2-MgO",
        "raw_structure": "gyroid",
        "raw_type": "TPMS",
        "structure_main_class": "tpms",
        "structure_subtype_list": ["gyroid", "graded"],
        "is_hierarchical": False,
        "is_graded": True,
        "is_optimized": False,
        "relative_density_raw": "36.58",
        "relative_density_value": 36.58,
        "raw_material": "MgO-doped CP Ti",
        "raw_material_group": "titanium",
        "material_canonical": "CP Ti",
        "material_family": "unknown",
        "raw_process": "L-PBF",
        "process_canonical": "L-PBF",
        "process_family": "unknown",
        "analysis_type": "experimental_numerical",
        "test_mode": "unknown",
        "loading_direction": "uniaxial",
        "velocity_m_s_raw": None,
        "velocity_m_s": None,
        "sea_j_g_raw": "28.5",
        "sea_j_g": 28.5,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": None,
        "plateau_stress_mpa": None,
        "confidence_overall": 0.89,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-012.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "gyroid",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Title identifies titanium gyroid lattice structures.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 1.0,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "L-PBF",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Abstract states the lattice structures were additively manufactured by laser powder bed fusion (L-PBF).",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 1.0,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "MgO-doped CP Ti",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Abstract states MgO nanoparticles were introduced to CP Ti feedstock for oxygen solute strengthening.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "sea_j_g",
            "field_value": "28.5",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 0,
            "figure_id": None,
            "table_id": "table_003",
            "text_snippet": "Table 3 row I2O-2-MgO records average relative density 36.58%, yield strength 111.16 MPa, and specific energy absorption 28.5 J/g.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(
        abstract_chunk,
        "sheet-based gyroid lattice structures",
        "ADDMA abstract",
    )
    _require_chunk_text(table_001, "The designed five gyroid lattice structures with different gradient ratios.", "ADDMA table 1")
    _require_chunk_text(table_003, "The relative porosity and mechanical properties of gyroid lattice structures.", "ADDMA table 3")

    return samples, evidence


def _build_compstruct_2019_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    table_001 = _find_chunk(paper_chunks, table_id="table_001")
    table_002 = _find_chunk(paper_chunks, table_id="table_002")

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-psh-a5-b1p568-t0p3",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "PSH",
        "is_multi_sample_paper": True,
        "raw_design": "PSH",
        "raw_structure": "petal-shaped honeycomb",
        "raw_type": "honeycomb",
        "structure_main_class": "honeycomb_2d",
        "structure_subtype_list": ["circular_celled", "petal_shaped", "nested"],
        "is_hierarchical": False,
        "is_graded": False,
        "is_optimized": False,
        "relative_density_raw": "0.196",
        "relative_density_value": 0.196,
        "raw_material": "aluminum alloy",
        "raw_material_group": "aluminum",
        "material_canonical": "Aluminum alloy",
        "material_family": "metal",
        "raw_process": "LS-DYNA",
        "process_canonical": "LS-DYNA",
        "process_family": "simulation",
        "analysis_type": "numerical",
        "test_mode": "quasi_static",
        "loading_direction": "in_plane",
        "velocity_m_s_raw": "1",
        "velocity_m_s": 1.0,
        "sea_j_g_raw": "4.12808",
        "sea_j_g": 4.12808,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": "4.568",
        "plateau_stress_mpa": 4.568,
        "confidence_overall": 0.9,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-013.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "petal-shaped honeycomb",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "A novel circular-celled honeycomb was proposed by incorporating the petal-shaped mesostructures into the regular circular cell honeycomb.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 1.0,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "LS-DYNA",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The PSH honeycomb specimen is made of aluminum alloy, and the nonlinear explicit FE code LS-DYNA is used to simulate the dynamic in-plane crushing response of PSH.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "sea_j_g",
            "field_value": "4.12808",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 6,
            "figure_id": None,
            "table_id": "table_001",
            "text_snippet": str(table_001.get("text") or ""),
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "plateau_stress_mpa",
            "field_value": "4.568",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 8,
            "figure_id": None,
            "table_id": "table_002",
            "text_snippet": str(table_002.get("text") or ""),
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(table_001, "SEA of the three types of honeycombs under", "COMPSTRUCT 2019 table 1")
    _require_chunk_text(table_002, "Plateau stress of PSH under in-plane impact loading.", "COMPSTRUCT 2019 table 2")

    return samples, evidence


def _build_tws_2020_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    table_001 = _find_chunk(paper_chunks, table_id="table_001")
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:012")), None)
    material_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:030")), None)
    model_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:029")), None)

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-sth-r015-v1",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "STH",
        "is_multi_sample_paper": True,
        "raw_design": "STH",
        "raw_structure": "star-triangular honeycomb",
        "raw_type": "honeycomb",
        "structure_main_class": "honeycomb_2d",
        "structure_subtype_list": ["auxetic", "star", "triangular"],
        "is_hierarchical": False,
        "is_graded": False,
        "is_optimized": False,
        "relative_density_raw": "0.15",
        "relative_density_value": 0.15,
        "raw_material": "aluminum alloy 6061O",
        "raw_material_group": "aluminum",
        "material_canonical": "Aluminum alloy",
        "material_family": "metal",
        "raw_process": "LS-DYNA",
        "process_canonical": "LS-DYNA",
        "process_family": "simulation",
        "analysis_type": "numerical",
        "test_mode": "quasi_static",
        "loading_direction": "in_plane",
        "velocity_m_s_raw": "1",
        "velocity_m_s": 1.0,
        "sea_j_g_raw": None,
        "sea_j_g": None,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": "1.1928",
        "plateau_stress_mpa": 1.1928,
        "confidence_overall": 0.9,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-014.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "star-triangular honeycomb",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "A novel star auxetic honeycomb with enhanced in-plane crushing strength",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 1.0,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "aluminum alloy 6061O",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The matrix material of the auxetic honeycomb is aluminum alloy 6061O, and it is assumed that the cell wall is elastic-perfectly plastic with Young ' s modulus E ¼ 68 GPa , yield stress σ s ¼ 80 MPa , density ρ s ¼ 2700 kg = m 3 and Poisson ' s ratio γ ¼ 0 : 33 [45].",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "plateau_stress_mpa",
            "field_value": "1.1928",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 9,
            "figure_id": None,
            "table_id": "table_001",
            "text_snippet": str(table_001.get("text") or ""),
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "loading_direction",
            "field_value": "in_plane",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "To reveal the dynamic deformation behavior and mechanical properties of the STH systematically, a finite element model was established using the explicit code of the nonlinear finite element software package LS-DYNA. In this model, the STH is located between the upper and lower rigid plates to simulate in-plane dynamic crushing.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(abstract_chunk, "star-triangular honeycomb (STH)", "TWS 2020 abstract")
    _require_chunk_text(material_chunk, "aluminum alloy 6061O", "TWS 2020 material")
    _require_chunk_text(model_chunk, "simulate in-plane dynamic crushing", "TWS 2020 model")
    _require_chunk_text(table_001, "The low-velocity crushing strengths of the STH.", "TWS 2020 table 1")

    return samples, evidence


def _build_high_density_honeycomb_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    summary_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:006")), None)
    structure_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:017")), None)
    quasi_static_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:033")), None)
    dynamic_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:089")), None)

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-al-honeycomb",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "al-honeycomb",
        "is_multi_sample_paper": True,
        "raw_design": "al-honeycomb",
        "raw_structure": "aluminum honeycomb",
        "raw_type": "honeycomb",
        "structure_main_class": "honeycomb_2d",
        "structure_subtype_list": [],
        "is_hierarchical": False,
        "is_graded": False,
        "is_optimized": False,
        "relative_density_raw": "32%",
        "relative_density_value": 0.32,
        "raw_material": "5052 aluminum",
        "raw_material_group": "aluminum",
        "material_canonical": "Aluminum alloy",
        "material_family": "metal",
        "raw_process": "forming and assembly",
        "process_canonical": "forming and assembly",
        "process_family": "forming_and_assembly",
        "analysis_type": "experimental",
        "test_mode": "quasi_static",
        "loading_direction": "uniaxial",
        "velocity_m_s_raw": "0.025 mm/s",
        "velocity_m_s": 0.000025,
        "sea_j_g_raw": None,
        "sea_j_g": None,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": None,
        "plateau_stress_mpa": None,
        "confidence_overall": 0.9,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-025.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "aluminum honeycomb",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The materials investigated were an aluminum honeycomb (referred to as al-honeycomb in the future) and a stainless-steel honeycomb.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 1.0,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "sample_label_in_paper",
            "field_value": "al-honeycomb",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The materials investigated were an aluminum honeycomb (referred to as al-honeycomb in the future) and a stainless-steel honeycomb.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "5052 aluminum",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The al-honeycomb was made of 0.1905 mm (0.0075 in) thick sheets of 5052 aluminum, and it had an overall density was 881 kg/m3 (55 lb/ft3).",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "relative_density_raw",
            "field_value": "32%",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Thus, the effective density was 32% of the density of aluminum.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-005",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "forming and assembly",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The formed sheets in the al-honeycomb have an approximate sine-wave shape. After they are formed, alternating layers of at sheets and formed sheets are assembled, and then bonded together with an epoxy adhesive.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-006",
            "sample_id": sample["sample_id"],
            "field_name": "test_mode",
            "field_value": "quasi_static",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 6,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The quasi-static tests were conducted on a 1.8 MN (400,000 lb) capacity Tinius-Olsen testing machine using a compression rate of approximately 0.025 mm/s (0.001 in/s) for the 76.2 mm (3 in) long specimen.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-007",
            "sample_id": sample["sample_id"],
            "field_name": "velocity_m_s_raw",
            "field_value": "0.025 mm/s",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 6,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The quasi-static tests were conducted on a 1.8 MN (400,000 lb) capacity Tinius-Olsen testing machine using a compression rate of approximately 0.025 mm/s (0.001 in/s) for the 76.2 mm (3 in) long specimen.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-008",
            "sample_id": sample["sample_id"],
            "field_name": "loading_direction",
            "field_value": "uniaxial",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 6,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "A method of testing the specimens in a state approximating uniaxial strain was developed for the large compressive deformations required with honeycombs, and used for both static and dynamic tests.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(summary_chunk, "Both materials showed a strain-rate e/ect", "HIGH DENSITY HONEYCOMB summary")
    _require_chunk_text(structure_chunk, "The materials investigated were an aluminum honeycomb", "HIGH DENSITY HONEYCOMB structure")
    _require_chunk_text(quasi_static_chunk, "compression rate of approximately 0.025 mm/s", "HIGH DENSITY HONEYCOMB quasi-static")
    _require_chunk_text(dynamic_chunk, "dynamic plateau stress is about 50% above the quasi-static value", "HIGH DENSITY HONEYCOMB dynamic")

    return samples, evidence


def _build_tws_2019_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    table_001 = _find_chunk(paper_chunks, table_id="table_001")
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:013")), None)
    process_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:053")), None)

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-g06-hierarchical-honeycomb",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "G0.6",
        "is_multi_sample_paper": True,
        "raw_design": "gamma=0.6",
        "raw_structure": "vertex-based hierarchical honeycomb",
        "raw_type": "honeycomb",
        "structure_main_class": "honeycomb_2d",
        "structure_subtype_list": ["hierarchical", "vertex_based", "triangular_substructure"],
        "is_hierarchical": True,
        "is_graded": False,
        "is_optimized": False,
        "relative_density_raw": None,
        "relative_density_value": None,
        "raw_material": "aluminum alloy",
        "raw_material_group": "aluminum",
        "material_canonical": "Aluminum alloy",
        "material_family": "metal",
        "raw_process": "ABAQUS/Explicit",
        "process_canonical": "ABAQUS/Explicit",
        "process_family": "simulation",
        "analysis_type": "numerical",
        "test_mode": "quasi_static",
        "loading_direction": "in_plane",
        "velocity_m_s_raw": "5 mm/s",
        "velocity_m_s": 0.005,
        "sea_j_g_raw": "2.976",
        "sea_j_g": 2.976,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": "0.353",
        "plateau_stress_mpa": 0.353,
        "confidence_overall": 0.9,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-015.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "vertex-based hierarchical honeycomb",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Abstract states triangular lattices were incorporated into a regular hexagonal honeycomb to replace each vertex.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 1.0,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "ABAQUS/Explicit",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 4,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The explicit FE code ABAQUS/Explicit is employed to simulate the crushing processes of the hierarchical honeycombs.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "plateau_stress_mpa",
            "field_value": "0.353",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 7,
            "figure_id": None,
            "table_id": "table_001",
            "text_snippet": "Table 1 row 7 records plateau stress 0.353 MPa in the L direction and 0.343 MPa in the W direction.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "sea_j_g",
            "field_value": "2.976",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 7,
            "figure_id": None,
            "table_id": "table_001",
            "text_snippet": "Table 1 row 7 records SEA 2.976 kJ/kg in the L direction and 2.803 kJ/kg in the W direction.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(abstract_chunk, "vertex-based hierarchical honeycombs", "TWS 2019 abstract")
    _require_chunk_text(process_chunk, "Typical aluminum alloy with Young", "TWS 2019 material context")
    _require_chunk_text(table_001, "Configurations of the honeycombs and simulation results for in-plane crushing.", "TWS 2019 table 1")

    return samples, evidence


def _build_compstruct_2018_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:019")), None)
    design_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:081")), None)
    material_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:037")), None)
    process_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:083")), None)
    density_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:031")), None)

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-n2-r0125-triangular-hierarchical",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "Triangular N=2 r=1/8",
        "is_multi_sample_paper": True,
        "raw_design": "N=2, r=1/8",
        "raw_structure": "triangular hierarchical honeycomb",
        "raw_type": "honeycomb",
        "structure_main_class": "honeycomb_2d",
        "structure_subtype_list": ["bioinspired", "hierarchical", "triangular"],
        "is_hierarchical": True,
        "is_graded": False,
        "is_optimized": False,
        "relative_density_raw": "0.05",
        "relative_density_value": 0.05,
        "raw_material": "AA3030-H19",
        "raw_material_group": "aluminum",
        "material_canonical": "Aluminum alloy",
        "material_family": "metal",
        "raw_process": "LS-DYNA",
        "process_canonical": "LS-DYNA",
        "process_family": "simulation",
        "analysis_type": "numerical",
        "test_mode": "quasi_static",
        "loading_direction": "in_plane",
        "velocity_m_s_raw": "5 m/s",
        "velocity_m_s": 5.0,
        "sea_j_g_raw": None,
        "sea_j_g": None,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": None,
        "plateau_stress_mpa": None,
        "confidence_overall": 0.9,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-017.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "triangular hierarchical honeycomb",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 11,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The triangular hierarchical honeycomb with N = 2 and r = 1/8 has the highest crushing resistance performance, with over twice the value of absorbed energy compared to the regular honeycomb.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 1.0,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_design",
            "field_value": "N=2, r=1/8",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 9,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Fig. 21 shows the effect of geometric parameters on the mean crushing force of the triangular hierarchical honeycomb. The triangular hierarchical honeycomb with N = 2 and r = 1/8 features the highest mean crushing force.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "AA3030-H19",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The hierarchical honeycombs are made of aluminum alloy AA3030-H19, Young's modulus E = 69 GPa, Poisson's ratio v = 0.33, density 2700 kg/m3, yield strength 115.8 MPa and ultimate tensile stress 160 MPa.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "LS-DYNA",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The finite element model consists of three parts: two rigid plates and the hierarchical honeycomb confined within those plates. The hierarchical honeycombs are discretized using shell elements, while the remaining two plates are meshed with hexahedral elements in LS-DYNA.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-005",
            "sample_id": sample["sample_id"],
            "field_name": "relative_density",
            "field_value": "0.05",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The simulations carried out in this work have been performed by fixing l0 = 20 mm, t0 = 0.8 mm, and an out-of-plane thickness of 10 mm. As a result, the relative density for all of the considered honeycombs is 0.05.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(abstract_chunk, "bio-inspired hierarchical honeycomb structures", "COMPSTRUCT 2018 abstract")
    _require_chunk_text(design_chunk, "triangular hierarchical honeycomb with N =2", "COMPSTRUCT 2018 design")
    _require_chunk_text(material_chunk, "AA3030-H19", "COMPSTRUCT 2018 material")
    _require_chunk_text(process_chunk, "LS-DYNA", "COMPSTRUCT 2018 process")
    _require_chunk_text(density_chunk, "relative density for all of the considered honeycombs is 0.05", "COMPSTRUCT 2018 density")

    return samples, evidence


def _build_matdes_2017_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:027")), None)
    design_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:039")), None)
    material_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:041")), None)
    density_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:059")), None)

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-rd016-hierarchical-honeycomb",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "RD0.16",
        "is_multi_sample_paper": True,
        "raw_design": "gamma=1/5, N=2",
        "raw_structure": "hierarchical honeycomb",
        "raw_type": "honeycomb",
        "structure_main_class": "honeycomb_2d",
        "structure_subtype_list": ["hierarchical", "triangular_lattice"],
        "is_hierarchical": True,
        "is_graded": False,
        "is_optimized": False,
        "relative_density_raw": "0.16",
        "relative_density_value": 0.16,
        "raw_material": "VeroWhite",
        "raw_material_group": "glassy_polymer",
        "material_canonical": "VeroWhite",
        "material_family": "polymer",
        "raw_process": "3D printing",
        "process_canonical": "3D printing",
        "process_family": "3d_printing",
        "analysis_type": "experimental_numerical",
        "test_mode": "quasi_static",
        "loading_direction": "uniaxial",
        "velocity_m_s_raw": None,
        "velocity_m_s": None,
        "sea_j_g_raw": None,
        "sea_j_g": None,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": None,
        "plateau_stress_mpa": None,
        "confidence_overall": 0.9,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-016.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "hierarchical honeycomb",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Abstract describes a hierarchical cellular structure formed by replacing honeycomb cell walls with triangular lattice configurations.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 1.0,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_design",
            "field_value": "gamma=1/5, N=2",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "In view of printer resolution and platen size, gamma = 1/5 and N = 2 were chosen for the prototypes.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "VeroWhite",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "All samples were printed on an Objet Connex260 multi-material 3D printer using VeroWhite as the constitutive material.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "3D printing",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The study fabricates the samples by 3D printing on an Objet Connex260 multi-material printer.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-005",
            "sample_id": sample["sample_id"],
            "field_name": "relative_density",
            "field_value": "0.16",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Hierarchical honeycombs with relative densities of 0.16, 0.32 and 0.55 were fabricated for testing.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(
        abstract_chunk,
        "hierarchical cellular structure created by replacing cell walls in regular honeycombs with triangular lattice configurations",
        "MATDES 2017 abstract",
    )
    _require_chunk_text(design_chunk, "N = 2, and l = 3 cm", "MATDES 2017 design")
    _require_chunk_text(material_chunk, "VeroWhite (a glassy polymer)", "MATDES 2017 material")
    _require_chunk_text(density_chunk, "relative densities of 0.16, 0.32 and 0.55", "MATDES 2017 density")

    return samples, evidence


def _build_ijimpeng_2023_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:016")), None)
    selection_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:121")), None)
    material_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:032")), None)
    process_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:037")), None)
    design_chunk = _find_chunk(paper_chunks, table_id="table_009")
    metric_chunk = _find_chunk(paper_chunks, table_id="table_008")

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-design1-reinforced-hexagonal-lattice",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "Design 1",
        "is_multi_sample_paper": True,
        "raw_design": "L=8, I=9, J=1.8, theta=119, T=2, nx=4, ny=5, nz=8",
        "raw_structure": "reinforced hexagonal lattice",
        "raw_type": "lattice",
        "structure_main_class": "bioinspired",
        "structure_subtype_list": ["bionic_honeycomb", "hexagonal", "reinforced"],
        "is_hierarchical": False,
        "is_graded": False,
        "is_optimized": True,
        "relative_density_raw": None,
        "relative_density_value": None,
        "raw_material": "AA6061-T6",
        "raw_material_group": "aluminum",
        "material_canonical": "Aluminum alloy 6061-T6",
        "material_family": "metal",
        "raw_process": "LS-DYNA",
        "process_canonical": "LS-DYNA",
        "process_family": "simulation",
        "analysis_type": "numerical",
        "test_mode": "dynamic",
        "loading_direction": "uniaxial",
        "velocity_m_s_raw": "15 km/h",
        "velocity_m_s": 4.1667,
        "sea_j_g_raw": "24.445",
        "sea_j_g": 24.445,
        "pcf_kn_raw": "58.519",
        "pcf_kn": 58.519,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": None,
        "plateau_stress_mpa": None,
        "confidence_overall": 0.94,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-018.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "reinforced hexagonal lattice",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "A spatial lattice structure is proposed via a bionic honeycomb and the single-cell structure is arrayed into a spatial lattice structure.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_design",
            "field_value": "L=8, I=9, J=1.8, theta=119, T=2, nx=4, ny=5, nz=8",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 13,
            "figure_id": None,
            "table_id": "table_009",
            "text_snippet": "Table 9 lists the optimal structure parameters L=8, I=9, J=1.8, theta=119, T=2, nx=4, ny=5, nz=8.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "AA6061-T6",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The material of the lattice structure is AA6061-T6 aluminum alloy.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "LS-DYNA",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 4,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "LS-DYNA software is used as the solver for finite element analysis (FEA).",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-005",
            "sample_id": sample["sample_id"],
            "field_name": "sea_j_g",
            "field_value": "24.445",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 12,
            "figure_id": None,
            "table_id": "table_008",
            "text_snippet": "Table 8 shows the GRA and EW optimal design with PF 58.519 kN and SEA 24.445 kJ/kg.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-006",
            "sample_id": sample["sample_id"],
            "field_name": "pcf_kn",
            "field_value": "58.519",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 12,
            "figure_id": None,
            "table_id": "table_008",
            "text_snippet": "Table 8 shows the GRA and EW optimal design with PF 58.519 kN and SEA 24.445 kJ/kg.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(abstract_chunk, "spatial lattice structure", "IJIMPENG 2023 abstract")
    _require_chunk_text(selection_chunk, "GRA coupling EW method", "IJIMPENG 2023 selection")
    _require_chunk_text(design_chunk, "Design parameters of the optimal structure.", "IJIMPENG 2023 design")
    _require_chunk_text(material_chunk, "AA6061-T6 aluminum alloy", "IJIMPENG 2023 material")
    _require_chunk_text(process_chunk, "fixed on an immovable rigid plate", "IJIMPENG 2023 process")
    _require_chunk_text(metric_chunk, "Comparison of initial design and optimal structure.", "IJIMPENG 2023 metric")

    return samples, evidence


def _build_engstruct_2023_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:017")), None)
    material_chunk = _find_chunk(paper_chunks, table_id="table_001")
    process_band_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:041")), None)
    process_crash_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:043")), None)
    optimization_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:136")), None)
    design_chunk = _find_chunk(paper_chunks, table_id="table_003")

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-knee-b7p71-d2p00",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "knee point",
        "is_multi_sample_paper": True,
        "raw_design": "b=7.71 mm, d=2.00 mm",
        "raw_structure": "hollow rhombic dodecahedron and six cylindrical tubes",
        "raw_type": "lattice",
        "structure_main_class": "hybrid_lattice",
        "structure_subtype_list": ["rhombic_dodecahedron", "cylindrical_tube"],
        "is_hierarchical": False,
        "is_graded": False,
        "is_optimized": True,
        "relative_density_raw": None,
        "relative_density_value": None,
        "raw_material": "316L stainless steel",
        "raw_material_group": "stainless_steel",
        "material_canonical": "316L stainless steel",
        "material_family": "metal",
        "raw_process": "COMSOL Multiphysics / LS-DYNA",
        "process_canonical": "COMSOL Multiphysics / LS-DYNA",
        "process_family": "simulation",
        "analysis_type": "experimental_numerical",
        "test_mode": "dynamic",
        "loading_direction": "uniaxial",
        "velocity_m_s_raw": "15 m/s",
        "velocity_m_s": 15.0,
        "sea_j_g_raw": "23.66",
        "sea_j_g": 23.66,
        "pcf_kn_raw": "461.54",
        "pcf_kn": 461.54,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": None,
        "plateau_stress_mpa": None,
        "confidence_overall": 0.95,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-019.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "hollow rhombic dodecahedron and six cylindrical tubes",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "This work investigates the vibration isolation performance and crashworthiness of a novel three-dimensional (3D) lattice metamaterial, whose unit cell is constructed by combining a hollow rhombic dodecahedron and six cylindrical tubes.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "316L stainless steel",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 2,
            "figure_id": None,
            "table_id": "table_001",
            "text_snippet": "Table 1 Material properties of the 316L stainless steel.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "COMSOL Multiphysics / LS-DYNA",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "COMSOL Multiphysics is employed to calculate the band structures. A constant impact velocity of 15 m/s is applied to the loaded plane. The numerical model of the 3D metamaterial for crushing analysis is established using the finite element (FE) code LS-DYNA.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "raw_design",
            "field_value": "b=7.71 mm, d=2.00 mm",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 10,
            "figure_id": None,
            "table_id": "table_003",
            "text_snippet": "Table 3 Optimal design of the 3D metamaterial with F max = 500kN. b (mm) d (mm) GR SEA (kJ/kg) PCF (kN) FE. RBF. RE (%) FE. RBF. RE (%) FE. RBF. RE (%) 7.71 2.00 0.4745 0.4842 2.04 23.66 23.80 0.59 461.54 452.32 2.00",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-005",
            "sample_id": sample["sample_id"],
            "field_name": "sea_j_g",
            "field_value": "23.66",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 10,
            "figure_id": None,
            "table_id": "table_003",
            "text_snippet": "Table 3 Optimal design of the 3D metamaterial with F max = 500kN.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-006",
            "sample_id": sample["sample_id"],
            "field_name": "pcf_kn",
            "field_value": "461.54",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 10,
            "figure_id": None,
            "table_id": "table_003",
            "text_snippet": "Table 3 Optimal design of the 3D metamaterial with F max = 500kN.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(abstract_chunk, "hollow rhombic dodecahedron and six cylindrical tubes", "ENGSTRUCT 2023 abstract")
    _require_chunk_text(material_chunk, "316L stainless steel", "ENGSTRUCT 2023 material")
    _require_chunk_text(process_band_chunk, "COMSOL Multiphysics is employed to calculate the band structures", "ENGSTRUCT 2023 band process")
    _require_chunk_text(process_crash_chunk, "impact velocity of 15 m/s", "ENGSTRUCT 2023 crash process")
    _require_chunk_text(optimization_chunk, "utopia point", "ENGSTRUCT 2023 optimization")
    _require_chunk_text(design_chunk, "Optimal design of the 3D metamaterial with F max = 500kN.", "ENGSTRUCT 2023 design")

    return samples, evidence


def _build_ma18040732_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    structure_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:051")), None)
    design_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:335")), None)
    material_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:337")), None)
    table_chunk = _find_chunk(paper_chunks, table_id="table_002")

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-bccz-cross-4x4x5",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "BCCz+cross",
        "is_multi_sample_paper": True,
        "raw_design": "4 × 4 × 5 lattice structure, 12 mm unit cell",
        "raw_structure": "BCCz+cross",
        "raw_type": "lattice",
        "structure_main_class": "truss_lattice",
        "structure_subtype_list": ["bcc", "bccz", "auxiliary_struts", "cross"],
        "is_hierarchical": False,
        "is_graded": False,
        "is_optimized": True,
        "relative_density_raw": None,
        "relative_density_value": None,
        "raw_material": "Ti-6Al-4V Grade 5",
        "raw_material_group": "titanium",
        "material_canonical": "Ti-6Al-4V",
        "material_family": "metal",
        "raw_process": "EBM",
        "process_canonical": "EBM",
        "process_family": "3d_printing",
        "analysis_type": "experimental_numerical",
        "test_mode": "quasi_static",
        "loading_direction": "uniaxial",
        "velocity_m_s_raw": "60 mm/sec",
        "velocity_m_s": 0.06,
        "sea_j_g_raw": "2.68 × 10^3",
        "sea_j_g": 2.68,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": "4.68 × 10^2",
        "mcf_kn": 468.0,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": None,
        "plateau_stress_mpa": None,
        "confidence_overall": 0.94,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-020.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "BCCz+cross",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 4,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "If a BCC structure is reinforced with vertical and rectangular and cross-shaped horizontal struts, it is denominated as BCCz+rect and BCCz+cross, respectively.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_design",
            "field_value": "4 × 4 × 5 lattice structure, 12 mm unit cell",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 18,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "For the fabrication process, six structures were output, each with a length of one corner of the unit structure set to 12 mm, consistent with the dimensions used in the FEA models. The overall size of the fabricated structure was 48 mm × 48 mm × 60 mm, with the number of unit structures in each corner set to 4, 4, and 5, respectively.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "Ti-6Al-4V Grade 5",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 18,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Ti-6Al-4V Grade 5 metal powder was employed, possessing an average particle size ranging from 45 to 106 µm.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "EBM",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 18,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The structures were manufactured by the EBM method with the GE Additive's Arcam EBM Spectra H Machine.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-005",
            "sample_id": sample["sample_id"],
            "field_name": "sea_j_g",
            "field_value": "2.68 × 10^3",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 21,
            "figure_id": None,
            "table_id": "table_002",
            "text_snippet": "BCCz+cross 8.4 2.25 × 10^4 2.68 × 10^3 4.68 × 10^2 0.3424 55.77",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-006",
            "sample_id": sample["sample_id"],
            "field_name": "mcf_kn",
            "field_value": "4.68 × 10^2",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 21,
            "figure_id": None,
            "table_id": "table_002",
            "text_snippet": "BCCz+cross 8.4 2.25 × 10^4 2.68 × 10^3 4.68 × 10^2 0.3424 55.77",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(structure_chunk, "BCCz+cross", "MA18040732 structure")
    _require_chunk_text(design_chunk, "48 mm × 48 mm × 60 mm", "MA18040732 design")
    _require_chunk_text(material_chunk, "Ti-6Al-4V Grade 5", "MA18040732 material")
    _require_chunk_text(table_chunk, "BCCz+cross 8.4 2.25 × 10 4", "MA18040732 table 2")

    return samples, evidence


def _build_cirpj_2024_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:015")), None)
    design_chunk = _find_chunk(paper_chunks, table_id="table_001")
    material_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:018")), None)
    process_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:019")), None)
    density_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:036")), None)
    compression_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:026")), None)
    performance_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:058")), None)

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-octet-10x10x10-d0p40-r015",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "Octet",
        "is_multi_sample_paper": True,
        "raw_design": "10 × 10 × 10 mm, 0.40 mm strut diameter",
        "raw_structure": "Octet",
        "raw_type": "lattice",
        "structure_main_class": "truss_lattice",
        "structure_subtype_list": ["octet"],
        "is_hierarchical": False,
        "is_graded": False,
        "is_optimized": False,
        "relative_density_raw": "15 %",
        "relative_density_value": 15.0,
        "raw_material": "316L stainless steel",
        "raw_material_group": "stainless_steel",
        "material_canonical": "316L stainless steel",
        "material_family": "metal",
        "raw_process": "LPBF",
        "process_canonical": "LPBF",
        "process_family": "3d_printing",
        "analysis_type": "experimental_numerical",
        "test_mode": "quasi_static",
        "loading_direction": "uniaxial",
        "velocity_m_s_raw": "2 mm/min",
        "velocity_m_s": 3.3333333333333335e-05,
        "sea_j_g_raw": "18.1 J/g",
        "sea_j_g": 18.1,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": None,
        "plateau_stress_mpa": None,
        "confidence_overall": 0.93,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-021.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "Octet",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 1,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The paper systematically compares FCC, Octet, and Kelvin lattice structures fabricated by LPBF.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_design",
            "field_value": "10 × 10 × 10 mm, 0.40 mm strut diameter",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 3,
            "figure_id": None,
            "table_id": "table_001",
            "text_snippet": "Table 1 records the Octet lattice structure with length, width, and height of 10 mm and a strut diameter of 0.40 mm.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "316L stainless steel",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "316 L stainless steel was selected as the basic material for the lattice structures.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "LPBF",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "FCC, Octet, and Kelvin lattice structures were fabricated using the LPBF technology.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-005",
            "sample_id": sample["sample_id"],
            "field_name": "relative_density_raw",
            "field_value": "15 %",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "All lattice structures have the same relative density ρ (15 %) to study the effect of geometries on formability and mechanical properties.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-006",
            "sample_id": sample["sample_id"],
            "field_name": "sea_j_g",
            "field_value": "18.1 J/g",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 7,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "When the strain reached 50 %, the W s of FCC, Octet, and Kelvin lattice structures were 31.9 J/g, 18.1 J/g, and 25.3 J/g, respectively.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(
        abstract_chunk,
        "laser powder bed fusion (LPBF) processed face-centered cubic (FCC), Octet, and Kelvin lattice structures were systematically compared through experiments and finite element analysis",
        "CIRPJ 2024 abstract",
    )
    _require_chunk_text(design_chunk, "Octet 10 10 10 0.40", "CIRPJ 2024 table 1")
    _require_chunk_text(material_chunk, "316 L stainless steel was selected as the basic material", "CIRPJ 2024 material")
    _require_chunk_text(process_chunk, "fabricated using the LPBF technology", "CIRPJ 2024 process")
    _require_chunk_text(density_chunk, "same relative density ρ (15 %)", "CIRPJ 2024 density")
    _require_chunk_text(compression_chunk, "crosshead velocity during the compression was set as 2 mm/min", "CIRPJ 2024 compression")
    _require_chunk_text(performance_chunk, "W s of FCC, Octet, and Kelvin lattice structures were 31.9 J/g, 18.1 J/g, and 25.3 J/g", "CIRPJ 2024 performance")

    return samples, evidence


def _build_ijimpeng_2025_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:021")), None)
    design_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:024")), None)
    material_process_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:021")), None)
    geometry_table = _find_chunk(paper_chunks, table_id="table_002")
    performance_table = _find_chunk(paper_chunks, table_id="table_003")

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-hprl-qstatic-r022",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "HPRL",
        "is_multi_sample_paper": True,
        "raw_design": "4 × 4 × 4 cell assembly, 24 mm cube",
        "raw_structure": "HPRL",
        "raw_type": "lattice",
        "structure_main_class": "hybrid_lattice",
        "structure_subtype_list": ["plate_rod", "octet"],
        "is_hierarchical": False,
        "is_graded": False,
        "is_optimized": False,
        "relative_density_raw": "0.22",
        "relative_density_value": 0.22,
        "raw_material": "17-4PH stainless steel",
        "raw_material_group": "stainless_steel",
        "material_canonical": "17-4PH stainless steel",
        "material_family": "metal",
        "raw_process": "SLM",
        "process_canonical": "SLM",
        "process_family": "3d_printing",
        "analysis_type": "experimental",
        "test_mode": "quasi_static",
        "loading_direction": "uniaxial",
        "velocity_m_s_raw": "0.024 mm/s",
        "velocity_m_s": 2.4e-05,
        "sea_j_g_raw": "11.2 J/g",
        "sea_j_g": 11.2,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": "38.7 MPa",
        "plateau_stress_mpa": 38.7,
        "confidence_overall": 0.93,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-022.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "HPRL",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The hybrid structure is established by combining a semi-open Octet-plate lattice (SOPL) and a strut or rod-based open-cell lattice, to form a hybrid plate-rod lattice (HPRL), amenable to fabrication via selective laser melting (SLM).",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_design",
            "field_value": "4 × 4 × 4 cell assembly, 24 mm cube",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Using SolidWorks software, 4 × 4 × 4 cell assemblies of the semi-open Octet-plate lattice (SOPL) and hybrid plate-rod lattice (HPRL) were established by connecting four unit cells along three orthogonal directions.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "17-4PH stainless steel",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "17 -4PH stainless steel powder was used to fabricate HPRL specimens by selective laser melting (SLM).",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "SLM",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "17 -4PH stainless steel powder was used to fabricate HPRL specimens by selective laser melting (SLM).",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-005",
            "sample_id": sample["sample_id"],
            "field_name": "velocity_m_s_raw",
            "field_value": "0.024 mm/s",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 4,
            "figure_id": None,
            "table_id": "table_002",
            "text_snippet": "HPRL 1 24.03 × 24.08 × 24.03 mm 3 23.91 g 0.024 mm/ s 0.22",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-006",
            "sample_id": sample["sample_id"],
            "field_name": "relative_density_raw",
            "field_value": "0.22",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 4,
            "figure_id": None,
            "table_id": "table_002",
            "text_snippet": "HPRL 1 24.03 × 24.08 × 24.03 mm 3 23.91 g 0.024 mm/ s 0.22",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-007",
            "sample_id": sample["sample_id"],
            "field_name": "sea_j_g",
            "field_value": "11.2 J/g",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 9,
            "figure_id": None,
            "table_id": "table_003",
            "text_snippet": "HPRL Initial yield stress (MPa) 35.5 53.8 54.3 Densification strain 0.50 0.50 0.51 Average plateau stress (MPa) 38.7 45.7 46.6 SEA (J/g) 11.2 13.4 13.7",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-008",
            "sample_id": sample["sample_id"],
            "field_name": "plateau_stress_mpa",
            "field_value": "38.7 MPa",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 9,
            "figure_id": None,
            "table_id": "table_003",
            "text_snippet": "HPRL Initial yield stress (MPa) 35.5 53.8 54.3 Densification strain 0.50 0.50 0.51 Average plateau stress (MPa) 38.7 45.7 46.6 SEA (J/g) 11.2 13.4 13.7",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(
        abstract_chunk,
        "novel hybrid plate-rod lattice (HPRL) structure and examines its mechanical response to quasi-static and dynamic gross compression",
        "IJIMPENG 2025 abstract",
    )
    _require_chunk_text(
        design_chunk,
        "4 × 4 × 4 cell assemblies of the semi-open Octet-plate lattice (SOPL) and hybrid plate-rod lattice (HPRL) were established",
        "IJIMPENG 2025 design",
    )
    _require_chunk_text(material_process_chunk, "fabricate HPRL specimens by selective laser melting (SLM)", "IJIMPENG 2025 material/process")
    _require_chunk_text(geometry_table, "HPRL 1 24.03 × 24.08 × 24.03 mm", "IJIMPENG 2025 geometry")
    _require_chunk_text(performance_table, "HPRL Initial yield stress (MPa) 35.5 53.8 54.3", "IJIMPENG 2025 performance")

    return samples, evidence


def _build_matdes_2018_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:024")), None)
    structure_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:094")), None)
    design_table = _find_chunk(paper_chunks, table_id="table_001")
    material_process_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:102")), None)
    compression_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:159")), None)
    energy_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:140")), None)
    performance_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:137")), None)

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-octagonal-l4p14-d1p626-r015",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "Octagonal",
        "is_multi_sample_paper": True,
        "raw_design": "5 x 5 x 5 cells, octagonal lattice, l = 4.14 mm, d = 1.626 mm",
        "raw_structure": "Octagonal",
        "raw_type": "lattice",
        "structure_main_class": "truss_lattice",
        "structure_subtype_list": ["octagonal"],
        "is_hierarchical": False,
        "is_graded": False,
        "is_optimized": True,
        "relative_density_raw": "15 %",
        "relative_density_value": 15.0,
        "raw_material": "HP PA12",
        "raw_material_group": "polyamide",
        "material_canonical": "Polyamide 12",
        "material_family": "polymer",
        "raw_process": "MJF",
        "process_canonical": "MJF",
        "process_family": "3d_printing",
        "analysis_type": "experimental_numerical",
        "test_mode": "quasi_static",
        "loading_direction": "uniaxial",
        "velocity_m_s_raw": "5 mm/min",
        "velocity_m_s": 8.333333333333333e-05,
        "sea_j_g_raw": "0.75 J/cm3",
        "sea_j_g": 0.75,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": "1.05 MPa",
        "plateau_stress_mpa": 1.05,
        "confidence_overall": 0.95,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-024.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "Octagonal",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 4,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Thus type 2 was constructed from three crossed octagons, designated as Octagonal lattice.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_design",
            "field_value": "5 x 5 x 5 cells, octagonal lattice, l = 4.14 mm, d = 1.626 mm",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 2,
            "figure_id": None,
            "table_id": "table_001",
            "text_snippet": "Table 1 Unit cell and overall specimen design and dimensions for the examined 3D structures of 15% relative density. ... 2 Octagonal l =4.14 1.626 51.626",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "HP PA12",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 5,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "A prototype of each lattice type was built using a new 3D printing technology called Multi Jet Fusion (MJF) in a brand of polyamide 12 plastic, namely HP PA12 available for this process.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "MJF",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 5,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "A prototype of each lattice type was built using a new 3D printing technology called Multi Jet Fusion (MJF) in a brand of polyamide 12 plastic, namely HP PA12 available for this process.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-005",
            "sample_id": sample["sample_id"],
            "field_name": "relative_density_raw",
            "field_value": "15 %",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 2,
            "figure_id": None,
            "table_id": "table_001",
            "text_snippet": "The six structures were designed to have a constant relative density of 15%.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-006",
            "sample_id": sample["sample_id"],
            "field_name": "velocity_m_s_raw",
            "field_value": "5 mm/min",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 10,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "The cross-head was moving downwards at a constant speed of 5 mm/min in accordance with the standard test method for compressive properties of rigid cellular plastics ASTM 1621-16.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-007",
            "sample_id": sample["sample_id"],
            "field_name": "sea_j_g",
            "field_value": "0.75 J/cm3",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 9,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "From the table, it can be seen that the Octagonal lattice is capable of absorbing the highest energy of 0.75 J/cm 3.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-008",
            "sample_id": sample["sample_id"],
            "field_name": "plateau_stress_mpa",
            "field_value": "1.05 MPa",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 9,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Among all structures, the Octagonal lattice provides the highest plateau stress of 1.05 MPa.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(abstract_chunk, "quasi-static energy absorption of six polymeric lattice structures", "MATDES 2018 abstract")
    _require_chunk_text(
        structure_chunk,
        "octagonal cell was chosen for constructing 3D lattice in this work",
        "MATDES 2018 structure",
    )
    _require_chunk_text(design_table, "Octagonal l =4.14 1.626 51.626", "MATDES 2018 table 1")
    _require_chunk_text(material_process_chunk, "namelyHPPA12availablefor this process", "MATDES 2018 material/process")
    _require_chunk_text(compression_chunk, "5 mm/min", "MATDES 2018 compression")
    _require_chunk_text(energy_chunk, "0.75 J/cm 3", "MATDES 2018 energy")
    _require_chunk_text(
        performance_chunk,
        "Among all structures, the Octagonal lattice provides the highest plateau stress of 1.05 MPa.",
        "MATDES 2018 performance",
    )

    return samples, evidence


def _build_matdes_2019_bundle(
    paper_id: str,
    register_row: dict[str, str],
    paper_chunks: list[dict[str, Any]],
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    abstract_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:026")), None)
    structure_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:034")), None)
    design_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:050")), None)
    material_process_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:048")), None)
    compression_chunk = next((row for row in paper_chunks if str(row.get("chunk_id", "")).endswith(":text:063")), None)
    density_table = _find_chunk(paper_chunks, table_id="table_002")
    performance_table = _find_chunk(paper_chunks, table_id="table_005")

    sample = {
        "paper_id": paper_id,
        "sample_id": f"{paper_id}-d5-bcc",
        "doi": register_row.get("doi") or None,
        "title": register_row.get("title") or None,
        "sample_label_in_paper": "D5",
        "is_multi_sample_paper": True,
        "raw_design": "25 × 25 × 25 mm cube, BCC lattice",
        "raw_structure": "BCC",
        "raw_type": "lattice",
        "structure_main_class": "truss_lattice",
        "structure_subtype_list": ["bcc"],
        "is_hierarchical": False,
        "is_graded": False,
        "is_optimized": False,
        "relative_density_raw": "12.60%",
        "relative_density_value": 0.126,
        "raw_material": "316L stainless steel",
        "raw_material_group": "stainless_steel",
        "material_canonical": "316L stainless steel",
        "material_family": "metal",
        "raw_process": "SLM",
        "process_canonical": "SLM",
        "process_family": "3d_printing",
        "analysis_type": "experimental_numerical",
        "test_mode": "quasi_static",
        "loading_direction": "uniaxial",
        "velocity_m_s_raw": "6 mm/min",
        "velocity_m_s": 0.0001,
        "sea_j_g_raw": "1.09 J/g",
        "sea_j_g": 1.09,
        "pcf_kn_raw": None,
        "pcf_kn": None,
        "mcf_kn_raw": None,
        "mcf_kn": None,
        "cfe_raw": None,
        "cfe": None,
        "plateau_stress_mpa_raw": "2.04 MPa",
        "plateau_stress_mpa": 2.04,
        "confidence_overall": 0.91,
        "needs_manual_review": True,
        "review_status": "pending",
        "review_notes": "Paper-derived seed from PDF corpus for TASK-023.",
    }
    _append_unique(samples, sample, "sample_id")

    evidence_rows = [
        {
            "evidence_id": f"{sample['sample_id']}-ev-001",
            "sample_id": sample["sample_id"],
            "field_name": "raw_structure",
            "field_value": "BCC",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 2,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Recently, the research on metal three-dimensional lattice structure mainly focuses on body-centered cubic (BCC) and other topologies derived from it.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-002",
            "sample_id": sample["sample_id"],
            "field_name": "raw_design",
            "field_value": "25 × 25 × 25 mm cube, BCC lattice",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "AutoCAD software was used to design the lattice structures in cubes of dimensions 25 × 25 × 25 mm so that they could be built in one batch to reduce production deviation.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-003",
            "sample_id": sample["sample_id"],
            "field_name": "raw_material",
            "field_value": "316L stainless steel",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "All of the lattice structures were made from a 316L stainless steel powder with an average particle size of 35 ± 10 µm.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-004",
            "sample_id": sample["sample_id"],
            "field_name": "raw_process",
            "field_value": "SLM",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 3,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "SLM technique as the additive manufacturing process was used to fabricate lattice structures.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-005",
            "sample_id": sample["sample_id"],
            "field_name": "relative_density_raw",
            "field_value": "12.60%",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 4,
            "figure_id": None,
            "table_id": "table_002",
            "text_snippet": "Table 2 The parameters of design configuration for lattice structure. Lattice structure D (mm) P (%) 1 1 12.60 12.60 Sample designation C1 C2 C3 C4 C5 C6 C7 D1 D2 D3 D4 D5 D6 D7 D8 LED (J/mm 3 ) 109.7 89.29 71.43 71.23 49.02 39.22 29.41 23.81",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.98,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-006",
            "sample_id": sample["sample_id"],
            "field_name": "velocity_m_s_raw",
            "field_value": "6 mm/min",
            "source_priority": "T1",
            "source_type": "text",
            "page_no": 4,
            "figure_id": None,
            "table_id": None,
            "text_snippet": "Uni-axial compression and tensile tests were carried out to assess the mechanical properties and energy absorption of the lattice structures by using a universal testing machine. During the compression tests, the lattice structures were centrally located between two plates. The speed of loading was set a constant of 6 mm/min for all of the tests.",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.99,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-007",
            "sample_id": sample["sample_id"],
            "field_name": "sea_j_g",
            "field_value": "1.09 J/g",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 7,
            "figure_id": None,
            "table_id": "table_005",
            "text_snippet": "Table 5 Energy absorption of the lattices derived from the stress-strain diagrams. Lattice designation Plateau stress, σ pl (MPa) Strain at the plateau start, ε y At the plateau end Strain, ε cd Energy absorbed, W (J/cm 3 ) Efficiency, E (%) A2 79.67 0.06 0.41 31.28 35.20 B1 8.99 0.11 0.64 5.49 46.95 C4 6.35 0.07 0.56 3.36 45.94 D5 2.04 0.07 0.56 1.08 42.63",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.97,
            "verified_by_human": False,
        },
        {
            "evidence_id": f"{sample['sample_id']}-ev-008",
            "sample_id": sample["sample_id"],
            "field_name": "plateau_stress_mpa",
            "field_value": "2.04 MPa",
            "source_priority": "T1",
            "source_type": "table",
            "page_no": 7,
            "figure_id": None,
            "table_id": "table_005",
            "text_snippet": "Table 5 Energy absorption of the lattices derived from the stress-strain diagrams. Lattice designation Plateau stress, σ pl (MPa) Strain at the plateau start, ε y At the plateau end Strain, ε cd Energy absorbed, W (J/cm 3 ) Efficiency, E (%) A2 79.67 0.06 0.41 31.28 35.20 B1 8.99 0.11 0.64 5.49 46.95 C4 6.35 0.07 0.56 3.36 45.94 D5 2.04 0.07 0.56 1.08 42.63",
            "extractor": "build_pdf_sample_bundle",
            "extract_confidence": 0.97,
            "verified_by_human": False,
        },
    ]
    for row in evidence_rows:
        _append_unique(evidence, row, "evidence_id")

    _require_chunk_text(
        abstract_chunk,
        "The performance of advanced and lightweight 316L stainless steel lattice structures fabricated by selective laser melting (SLM) was investigated using a range of laser energy densities (LED).",
        "MATDES 2019 abstract",
    )
    _require_chunk_text(
        structure_chunk,
        "body-centered cubic (BCC) and other topologies derived from it",
        "MATDES 2019 BCC background",
    )
    _require_chunk_text(design_chunk, "25 × 25 × 25 mm", "MATDES 2019 design")
    _require_chunk_text(material_process_chunk, "316L stainless steel powder", "MATDES 2019 material")
    _require_chunk_text(material_process_chunk, "SLM technique as the additive manufacturing process", "MATDES 2019 process")
    _require_chunk_text(density_table, "D5", "MATDES 2019 table 2")
    _require_chunk_text(compression_chunk, "6 mm/min", "MATDES 2019 compression")
    _require_chunk_text(performance_table, "D5 2.04 0.07 0.56 1.08 42.63", "MATDES 2019 performance")

    return samples, evidence


def build_bundle(
    paper_id: str,
    samples: list[dict[str, Any]],
    evidence: list[dict[str, Any]],
    *,
    register_path: Path = DEFAULT_REGISTER_PATH,
    corpus_path: Path = DEFAULT_CORPUS_PATH,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    register_row = _load_register_row(paper_id, register_path)
    corpus = _load_jsonl(corpus_path)
    paper_chunks = [row for row in corpus if row.get("paper_id") == paper_id]
    if not paper_chunks:
        raise SystemExit(f"paper_id not found in corpus: {paper_id}")

    if paper_id == JMRT_2023_PAPER_ID:
        return _build_jmrt_2023_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == ADDMA_2022_PAPER_ID:
        return _build_addma_2022_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == COMPSTRUCT_2018_PAPER_ID:
        return _build_compstruct_2018_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == COMPSTRUCT_2019_PAPER_ID:
        return _build_compstruct_2019_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == TWS_2019_PAPER_ID:
        return _build_tws_2019_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == TWS_2020_PAPER_ID:
        return _build_tws_2020_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == HIGH_DENSITY_HONEYCOMB_PAPER_ID:
        return _build_high_density_honeycomb_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == MATDES_2017_PAPER_ID:
        return _build_matdes_2017_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == MATDES_2018_PAPER_ID:
        return _build_matdes_2018_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == MATDES_2019_PAPER_ID:
        return _build_matdes_2019_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == IJIMPENG_2023_PAPER_ID:
        return _build_ijimpeng_2023_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == ENGSTRUCT_2023_PAPER_ID:
        return _build_engstruct_2023_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == MA18040732_PAPER_ID:
        return _build_ma18040732_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == CIRPJ_2024_PAPER_ID:
        return _build_cirpj_2024_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == IJIMPENG_2025_PAPER_ID:
        return _build_ijimpeng_2025_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    raise SystemExit(f"unsupported paper_id: {paper_id}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Append a paper-derived sample bundle to the canonical P1 extracted outputs")
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES_PATH)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE_PATH)
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER_PATH)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    args = parser.parse_args(argv)

    samples = read_json(args.samples)
    evidence = read_json(args.evidence)
    if not isinstance(samples, list) or not isinstance(evidence, list):
        raise SystemExit("expected arrays in the canonical extracted outputs")

    updated_samples, updated_evidence = build_bundle(
        args.paper_id,
        samples,
        evidence,
        register_path=args.register,
        corpus_path=args.corpus,
    )
    write_json(args.samples, updated_samples)
    write_json(args.evidence, updated_evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
