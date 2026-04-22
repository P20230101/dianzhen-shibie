from __future__ import annotations

from p1_pipeline_common import SEED_INPUT_PATH, SEED_SNAPSHOT_PATH, build_seed_input, write_json


def main() -> int:
    seed = build_seed_input()
    write_json(SEED_INPUT_PATH, seed)
    write_json(SEED_SNAPSHOT_PATH, seed)
    print(f"seed written: {SEED_INPUT_PATH}")
    print(f"seed snapshot: {SEED_SNAPSHOT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
