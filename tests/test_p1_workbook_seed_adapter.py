from __future__ import annotations

from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from p1_pipeline_common import build_seed_input_from_workbook  # type: ignore  # noqa: E402


WORKBOOK_PATH = ROOT / "Lattice crashworthiness data.xlsx"


def test_build_seed_input_from_workbook_row_104_maps_expected_fields() -> None:
    seed = build_seed_input_from_workbook(WORKBOOK_PATH, row_number=104)

    assert seed["paper_id"] == "10-1016-j-compositesb-2019-107565"
    assert seed["sample_id"] == "10-1016-j-compositesb-2019-107565-row-104-tpms-primitive-104"
    assert seed["doi"] == "10.1016/j.compositesb.2019.107565"
    assert seed["title"] == "Crushing behavior and optimization of sheet-based 3D periodic cellular structures"
    assert seed["sample_label_in_paper"] == "row-104"
    assert seed["is_multi_sample_paper"] is True
    assert seed["raw_design"] == "Primitive"
    assert seed["raw_structure"] == "Beam"
    assert seed["raw_type"] == "TPMS"
    assert seed["raw_material"] == "316L"
    assert seed["raw_material_group"] == "Stainless"
    assert seed["raw_process"] == "SLM"
    assert seed["analysis_type"] == "experimental"
    assert seed["test_mode"] == "quasi_static"
    assert seed["loading_direction"] == "uniaxial"
    assert seed["velocity_m_s"] == pytest.approx(3.3333e-05)
    assert seed["sea_j_g"] == pytest.approx(12.776)
    assert seed["pcf_kn"] == pytest.approx(12.594)
    assert seed["mcf_kn"] == pytest.approx(7.666)
    assert seed["relative_density_value"] is None
