from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_pdf_sample_bundle import main as build_bundle_main  # type: ignore  # noqa: E402
from retrieval_kg_common import read_json  # type: ignore  # noqa: E402


FIXTURES_DIR = ROOT / "tests" / "fixtures" / "pdf_sample_bundle"
BASE_SAMPLES = FIXTURES_DIR / "base_samples.json"
BASE_EVIDENCE = FIXTURES_DIR / "base_evidence.json"


def test_build_pdf_sample_bundle_appends_one_paper_row(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_jmrt_2023_05_167",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_rejects_drifted_corpus(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"
    corpus_path = tmp_path / "corpus.jsonl"

    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    mutated_lines: list[str] = []
    for line in (ROOT / "data" / "02_retrieval" / "corpus.jsonl").read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        if row.get("paper_id") == "10_1016_j_jmrt_2023_05_167" and str(row.get("chunk_id", "")).endswith(":text:027"):
            row["text"] = str(row.get("text") or "").replace("FDM process", "FFF process", 1)
        mutated_lines.append(json.dumps(row, ensure_ascii=False))
    corpus_path.write_text("\n".join(mutated_lines) + "\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="drifted|required chunk not found"):
        build_bundle_main([
            "--paper-id",
            "10_1016_j_jmrt_2023_05_167",
            "--samples",
            str(samples_path),
            "--evidence",
            str(evidence_path),
            "--corpus",
            str(corpus_path),
        ])


def test_build_pdf_sample_bundle_supports_addma_gyroid_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_addma_2022_102887",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_addma.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_addma.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_compstruct_2019_psh_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_compstruct_2019_111219",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_compstruct_2019.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_compstruct_2019.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_tws_2020_star_auxetic_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_tws_2020_106623",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_tws_2020.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_tws_2020.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_tws_2019_hierarchical_honeycomb_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_tws_2019_106436",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_tws_2019.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_tws_2019.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_matdes_2017_hierarchical_honeycomb_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_matdes_2017_10_028",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_tws_2017.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_tws_2017.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_compstruct_2018_bioinspired_hierarchical_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_compstruct_2018_03_050",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_compstruct_2018.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_compstruct_2018.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_ijimpeng_2023_spatial_lattice_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_ijimpeng_2023_104713",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_ijimpeng_2023.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_ijimpeng_2023.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_engstruct_2023_metamaterial_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_engstruct_2023_116510",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_engstruct_2023.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_engstruct_2023.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_ma18040732_bccz_cross_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_3390_ma18040732",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_ma18040732.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_ma18040732.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_cirpj_2024_octet_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_cirpj_2024_06_009",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_cirpj_2024.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_cirpj_2024.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_ijimpeng_2025_hprl_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_ijimpeng_2025_105321",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_ijimpeng_2025.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_ijimpeng_2025.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_matdes_2019_bcc_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    exit_code = build_bundle_main([
        "--paper-id",
        "10_1016_j_matdes_2019_108076",
        "--samples",
        str(samples_path),
        "--evidence",
        str(evidence_path),
    ])

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_matdes_2019.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_matdes_2019.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)


def test_build_pdf_sample_bundle_supports_matdes_2018_octagonal_paper(tmp_path: Path) -> None:
    samples_path = tmp_path / "samples_v1.json"
    evidence_path = tmp_path / "evidence_v1.json"

    base_samples = read_json(BASE_SAMPLES)
    base_evidence = read_json(BASE_EVIDENCE)
    samples_path.write_text(BASE_SAMPLES.read_text(encoding="utf-8"), encoding="utf-8")
    evidence_path.write_text(BASE_EVIDENCE.read_text(encoding="utf-8"), encoding="utf-8")

    try:
        exit_code = build_bundle_main([
            "--paper-id",
            "10_1016_j_matdes_2018_05_059",
            "--samples",
            str(samples_path),
            "--evidence",
            str(evidence_path),
        ])
    except SystemExit as exc:
        exit_code = exc.code if isinstance(exc.code, int) else 1

    samples = read_json(samples_path)
    evidence = read_json(evidence_path)
    expected_sample = read_json(FIXTURES_DIR / "expected_sample_matdes_2018.json")
    expected_evidence = read_json(FIXTURES_DIR / "expected_evidence_matdes_2018.json")

    assert exit_code == 0
    assert expected_sample in samples
    assert all(item in evidence for item in expected_evidence)
    assert len(samples) == len(base_samples) + 1
    assert len(evidence) == len(base_evidence) + len(expected_evidence)
