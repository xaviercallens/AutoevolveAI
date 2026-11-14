"""C1b throughput measurement + N = 11 sample cross-check (Python C1 code vs census_fast on the same 10^7 graphs).
Usage: throughput_report.py <py_enc.json> <fast_enc.json> <py_log> <fast_time_log> <out.json>"""

from __future__ import annotations

import json
import re
import sys

A001349_11 = 1006700565


def main() -> None:
    py, fa = json.load(open(sys.argv[1])), json.load(open(sys.argv[2]))
    py_log, fast_log = open(sys.argv[3]).read(), open(sys.argv[4]).read()
    py_wall = float(re.search(r"done \d+ \d+ \d+ (\d+)s", py_log).group(1))
    m = re.search(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\): (\d+):([\d.]+)", fast_log)
    fast_wall = int(m.group(1)) * 60 + float(m.group(2))
    fast_user = float(re.search(r"User time \(seconds\): ([\d.]+)", fast_log).group(1))
    g = py["graphs"]
    out = {
        "sample": "nauty-geng -cq 11 0/100 (7,815,167 graphs) followed by the first 2,184,833 graphs of 1/100: 10,000,000 graphs",
        "graphs": g,
        "python_C1_code": {"wall_s": py_wall, "graphs_per_s_one_core": g / py_wall,
                           "projected_total_h_on_2_cores": A001349_11 / (2 * g / py_wall) / 3600},
        "census_fast": {"wall_s": fast_wall, "user_cpu_s": fast_user, "graphs_per_s_one_core_wall": g / fast_wall,
                        "graphs_per_s_one_core_cpu": g / fast_user,
                        "projected_total_h_on_2_cores": A001349_11 / (2 * g / fast_wall) / 3600},
        "cross_check": {"graphs_equal": py["graphs"] == fa["graphs"],
                        "excluded_equal": py["excluded_certified"] == fa["excluded_certified"],
                        "excluded": fa["excluded_certified"],
                        "candidate_sets_identical": sorted(c["graph6"] for c in py["candidates"])
                        == sorted(c["graph6"] for c in fa["candidates"]),
                        "candidates": sorted(c["graph6"] for c in fa["candidates"]),
                        "candidates_regular": [c["regular"] for c in fa["candidates"]],
                        "max_eps_python": py["max_eps"], "max_eps_fast": fa["max_eps"],
                        "min_gap_python": py["min_certified_gap_among_excluded"], "min_gap_fast": fa["min_certified_gap_among_excluded"],
                        "nearest_python": py["nonregular_nearest_to_N"][0]["graph6"], "nearest_fast": fa["nonregular_nearest_to_N"][0]["graph6"]},
        "kill_criterion": "projected total > 24 h on 2 cores => stop",
    }
    out["kill_triggered_for_fast_code"] = out["census_fast"]["projected_total_h_on_2_cores"] > 24
    json.dump(out, open(sys.argv[5], "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
