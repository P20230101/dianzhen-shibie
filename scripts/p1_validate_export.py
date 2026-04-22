from __future__ import annotations

import json

from p1_pipeline_common import (
    EVIDENCE_PATH,
    EVIDENCE_SCHEMA_PATH,
    PARSED_PATH,
    REPORT_PATH,
    SAMPLE_SCHEMA_PATH,
    SAMPLES_PATH,
    validate_instance_file,
    write_json,
)


def main() -> int:
    issues: list[str] = []

    if not PARSED_PATH.exists():
        issues.append(f"missing parsed artifact: {PARSED_PATH}")
    if not SAMPLES_PATH.exists():
        issues.append(f"missing samples artifact: {SAMPLES_PATH}")
    if not EVIDENCE_PATH.exists():
        issues.append(f"missing evidence artifact: {EVIDENCE_PATH}")

    if not issues:
        issues.extend(validate_instance_file(SAMPLES_PATH, SAMPLE_SCHEMA_PATH, "samples"))
        issues.extend(validate_instance_file(EVIDENCE_PATH, EVIDENCE_SCHEMA_PATH, "evidence"))

    if issues:
        report = {
            "status": "failed",
            "issues": issues,
            "parsed_path": str(PARSED_PATH),
            "samples_path": str(SAMPLES_PATH),
            "evidence_path": str(EVIDENCE_PATH),
        }
        write_json(REPORT_PATH, report)
        raise SystemExit("\n".join(issues))

    report = {
        "status": "passed",
        "chain": [
            "seed",
            "parse",
            "extract",
            "validate",
            "export",
        ],
        "parsed_path": str(PARSED_PATH),
        "samples_path": str(SAMPLES_PATH),
        "evidence_path": str(EVIDENCE_PATH),
        "sample_count": len(json.loads(SAMPLES_PATH.read_text(encoding="utf-8"))),
        "evidence_count": len(json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))),
        "schema_checks": {
            "samples": "passed",
            "evidence": "passed",
        },
        "closure": "P1 first minimal chain is export-ready on feat/task-001-min-pipeline.",
    }
    write_json(REPORT_PATH, report)
    print(f"validation report: {REPORT_PATH}")
    print("samples schema: passed")
    print("evidence schema: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
