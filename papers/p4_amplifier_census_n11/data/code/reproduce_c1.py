"""C1b positive control: exact finish (finish_candidates.py, C1 code) of the census_fast outputs for N = 3..10 (written by
validate_fast.py into .scratchpad/C1b/val_fast_n{N}.json, full geng files), compared with OEIS A001349 / A005177 and with C1.
Usage: reproduce_c1.py <out.json>"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WT = HERE.parents[4]
SCR = WT / ".scratchpad" / "C1b"
C1DATA = HERE.parents[1] / "C1" / "data"
PY = "/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python"
A001349 = {3: 2, 4: 6, 5: 21, 6: 112, 7: 853, 8: 11117, 9: 261080, 10: 11716571}
A005177 = {3: 1, 4: 2, 5: 2, 6: 5, 7: 4, 8: 17, 9: 22, 10: 167}


def main() -> None:
    rows = {}
    ok_all = True
    for n in range(3, 11):
        fin = SCR / f"repro_fin_n{n}.json"
        subprocess.run(["taskset", "-c", "2", PY, "-I", str(HERE / "finish_candidates.py"), str(SCR / f"val_fast_n{n}.json"), str(fin)],
                       check=True, stdout=subprocess.DEVNULL)
        f = json.load(open(fin))
        c1 = json.load(open(C1DATA / f"census_n{n}_enclosure_final.json"))
        r = {"graphs": f["graphs"], "A001349": A001349[n], "count_gt": f["count_gt"], "count_eq": f["count_eq"],
             "count_eq_nonregular": f["count_eq_nonregular"], "A005177": A005177[n], "count_lt_total": f["count_lt_total"],
             "C1_count_gt": c1["count_gt"], "C1_count_eq": c1["count_eq"], "C1_count_lt_total": c1["count_lt_total"],
             "candidates_exact_identical_to_C1": sorted((x["graph6"], x["N_eff"]) for x in f["candidates_exact"])
             == sorted((x["graph6"], x["N_eff"]) for x in c1["candidates_exact"])}
        r["ok"] = (r["graphs"] == r["A001349"] and r["count_gt"] == 0 and r["count_eq"] == r["A005177"] and r["count_eq_nonregular"] == 0
                   and r["count_gt"] == r["C1_count_gt"] and r["count_eq"] == r["C1_count_eq"]
                   and r["count_lt_total"] == r["C1_count_lt_total"] and r["candidates_exact_identical_to_C1"])
        ok_all = ok_all and r["ok"]
        rows[str(n)] = r
        print(n, r, flush=True)
    json.dump({"per_N": rows, "all_ok": ok_all}, open(sys.argv[1], "w"), indent=1)
    print("ALL_OK" if ok_all else "FAILED")


if __name__ == "__main__":
    main()
