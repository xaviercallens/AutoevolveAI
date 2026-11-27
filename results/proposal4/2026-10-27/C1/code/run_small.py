"""Driver: enclosure census + independent exact census + cross-check for N = 3..max_n (default 8). Sequential, one process."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCR = ROOT.parents[3] / ".scratchpad" / "C1"
PY = "/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python"

max_n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
min_n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
EXACT_MAX_N = 8  # independent all-graph Fraction census; N = 9 needs ~3 h of one core (see RESULT.md, Deviations)
for n in range(min_n, max_n + 1):
    g6 = SCR / f"geng_c{n}.g6"
    enc = SCR / f"enc{n}.json"
    if not enc.exists():
        subprocess.run([PY, "-I", str(HERE / "census_enclosure.py"), str(g6), str(n), "0", "1", str(enc)], check=True)
    subprocess.run([PY, "-I", str(HERE / "finish_candidates.py"), str(enc), str(ROOT / "data" / f"census_n{n}_enclosure_final.json")],
                   check=True, stdout=subprocess.DEVNULL)
    if n <= EXACT_MAX_N:
        subprocess.run([PY, "-I", str(HERE / "exact_census.py"), str(g6), str(n), str(ROOT / "data" / f"census_n{n}_exact.json"),
                        str(enc)], check=True)
