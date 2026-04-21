from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from p1_pipeline_common import EVIDENCE_PATH, SAMPLES_PATH, read_json, write_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REVIEW_NOTE = "Promoted after P1 validation to enable KG projection."


def _ensure_sequence(payload: Any, path: Path) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        raise SystemExit(f"expected a JSON array in {path}")
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(payload):
        if not isinstance(row, dict):
            raise SystemExit(f"expected object rows in {path} at index {index}")
        rows.append(row)
    return rows


def promote_samples(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    promoted: list[dict[str, Any]] = []
    for row in samples:
        updated = dict(row)
        if updated.get("review_status") == "rejected":
            raise SystemExit(f"cannot promote rejected sample: {updated.get('sample_id')}")
        updated["review_status"] = "accepted"
        updated["needs_manual_review"] = False
        review_notes = str(updated.get("review_notes") or "").strip()
        if review_notes:
            if DEFAULT_REVIEW_NOTE not in review_notes:
                updated["review_notes"] = f"{review_notes} {DEFAULT_REVIEW_NOTE}"
        else:
            updated["review_notes"] = DEFAULT_REVIEW_NOTE
        promoted.append(updated)
    return promoted


def promote_evidence(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    promoted: list[dict[str, Any]] = []
    for row in evidence:
        updated = dict(row)
        updated["verified_by_human"] = True
        promoted.append(updated)
    return promoted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Promote validated P1 sample and evidence outputs for KG projection")
    parser.add_argument("--samples", type=Path, default=SAMPLES_PATH)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE_PATH)
    args = parser.parse_args(argv)

    samples = _ensure_sequence(read_json(args.samples), args.samples)
    evidence = _ensure_sequence(read_json(args.evidence), args.evidence)

    promoted_samples = promote_samples(samples)
    promoted_evidence = promote_evidence(evidence)

    write_json(args.samples, promoted_samples)
    write_json(args.evidence, promoted_evidence)
    print(f"promoted samples written: {args.samples}")
    print(f"promoted evidence written: {args.evidence}")
    print(f"sample_count={len(promoted_samples)}, evidence_count={len(promoted_evidence)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
