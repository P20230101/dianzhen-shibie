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
MATDES_2017_PAPER_ID = "10_1016_j_matdes_2017_10_028"
IJIMPENG_2023_PAPER_ID = "10_1016_j_ijimpeng_2023_104713"
ENGSTRUCT_2023_PAPER_ID = "10_1016_j_engstruct_2023_116510"


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
    if paper_id == MATDES_2017_PAPER_ID:
        return _build_matdes_2017_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == IJIMPENG_2023_PAPER_ID:
        return _build_ijimpeng_2023_bundle(paper_id, register_row, paper_chunks, samples, evidence)
    if paper_id == ENGSTRUCT_2023_PAPER_ID:
        return _build_engstruct_2023_bundle(paper_id, register_row, paper_chunks, samples, evidence)
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
