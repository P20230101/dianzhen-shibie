from __future__ import annotations

from p1_pipeline_common import (
    EVIDENCE_PATH,
    PARSED_PATH,
    SEED_INPUT_PATH,
    SAMPLES_PATH,
    build_evidence_records,
    build_parsed_artifact,
    build_sample_record,
    read_json,
    write_json,
)


def main() -> int:
    if not SEED_INPUT_PATH.exists():
        raise SystemExit(f"missing seed input: {SEED_INPUT_PATH}")

    seed = read_json(SEED_INPUT_PATH)
    parsed = build_parsed_artifact(seed)
    sample = build_sample_record(seed)
    evidence = build_evidence_records(seed, sample)

    write_json(PARSED_PATH, parsed)
    write_json(SAMPLES_PATH, [sample])
    write_json(EVIDENCE_PATH, evidence)

    print(f"parsed written: {PARSED_PATH}")
    print(f"samples written: {SAMPLES_PATH}")
    print(f"evidence written: {EVIDENCE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
