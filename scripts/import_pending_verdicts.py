#!/usr/bin/env python3
"""Import every pending verifier-verdict file into the verified pool before the gate runs.

Runs as a nightly step ahead of the dream-predictor trainer, so new real verdicts reach the pool
without anyone remembering to import them. Each importer is idempotent by source tag, so a second
run writes nothing new.

Sources:
- Lean verdicts from the retrieval A/B (scripts/import_lean_verdicts_to_pool.py). Embeds on the
  GPU when it runs the first time, so it is skipped once its source tag is in the pool.
- Hard harvest files data/episodes/harvest_hard_*.jsonl (scripts/import_harvest_to_pool.py).
  The easy harvest is deliberately excluded: its rows are all passes and carry no signal.

Exit status is 0 when every source imported or was already present, 1 if any importer failed.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HARVEST_GLOB = "data/episodes/harvest_hard_*.jsonl"


def pending_harvest_files() -> list[Path]:
    return sorted(REPO.glob(HARVEST_GLOB))


def run_importer(script: str, *args: str) -> int:
    cmd = [sys.executable, str(REPO / "scripts" / script), *args]
    return subprocess.run(cmd, cwd=REPO, check=False).returncode


def main() -> int:
    status = 0
    print(f"lean verdicts: rc={run_importer('import_lean_verdicts_to_pool.py')}")
    for path in pending_harvest_files():
        rc = run_importer("import_harvest_to_pool.py", str(path.relative_to(REPO)))
        print(f"harvest {path.name}: rc={rc}")
        status = status or int(rc != 0)
    if not pending_harvest_files():
        print("no hard harvest files pending")
    return status


if __name__ == "__main__":
    sys.exit(main())
