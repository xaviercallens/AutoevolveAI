"""C1b validation of census_fast.c against the C1 Python decision code, BEFORE any N = 11 use.

Usage: validate_fast.py <census_fast binary> <out.json>

For N = 3..10 (graph6 files of C1 in .scratchpad/C1, sha256 checked against C1's geng_sha256.txt):
  (a) summary level, every graph: census_fast on the whole file vs C1's own enclosure output .scratchpad/C1/enc{N}.json
      (same geng file): identical graph count, identical excluded count, identical candidate set (graph6 strings).
      Same count + same candidate set => identical verdict on every graph (every non-candidate is excluded).
  (b) per-graph level: census_fast --verbose vs py_pergraph.py (C1 functions, guarded copy) on all graphs for N = 3..9
      and on a 10^6-graph stride sample at N = 10 (every 11th line from line 0): identical graph6 order, identical verdict,
      and the two certified intervals [2 N^ - ub, ub] must intersect (both contain the true N_eff).
One busy child process at a time, pinned to core 2.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WT = HERE.parents[4]
SCR_C1 = WT / ".scratchpad" / "C1"
SCR = WT / ".scratchpad" / "C1b"
PY = "/home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python"
CORE = "2"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run_fast(binary: str, n: int, g6: Path, out: Path, verbose: Path | None) -> dict:
    cmd = ["taskset", "-c", CORE, binary, str(n), str(out)]
    if verbose is not None:
        cmd += ["--verbose", str(verbose)]
    with open(g6, "rb") as fin:
        subprocess.run(cmd, stdin=fin, check=True, stderr=subprocess.DEVNULL)
    return json.load(open(out))


def compare_tsv(a: Path, b: Path) -> dict:
    n = mismatch_g6 = mismatch_verdict = no_overlap = 0
    max_dneff = 0.0
    examples: list[str] = []
    with open(a) as fa, open(b) as fb:
        for la, lb in zip(fa, fb, strict=True):
            n += 1
            ga, va, na, ua = la.split("\t")[:4]
            gb, vb, nb_, ub = lb.split("\t")[:4]
            if ga != gb:
                mismatch_g6 += 1
                continue
            if va != vb:
                mismatch_verdict += 1
                if len(examples) < 5:
                    examples.append(f"{ga} fast={va} py={vb}")
            na_f, ua_f, nb_f, ub_f = float(na), float(ua), float(nb_), float(ub)
            lo = max(2 * na_f - ua_f, 2 * nb_f - ub_f)
            hi = min(ua_f, ub_f)
            if lo > hi + 1e-12:
                no_overlap += 1
            max_dneff = max(max_dneff, abs(na_f - nb_f))
    return {"graphs_compared": n, "graph6_mismatch": mismatch_g6, "verdict_mismatch": mismatch_verdict,
            "intervals_not_intersecting": no_overlap, "max_abs_diff_neff_hat": max_dneff, "examples": examples}


def main() -> None:
    binary, out_path = sys.argv[1], sys.argv[2]
    recorded = {}
    for line in open(SCR_C1 / "geng_sha256.txt"):
        h, name = line.split()
        recorded[name] = h
    report: dict = {"binary": binary, "binary_sha256": sha256(Path(binary)), "per_N": {}}
    all_ok = True
    for n in range(3, 11):
        t0 = time.time()
        g6 = SCR_C1 / f"geng_c{n}.g6"
        h = sha256(g6)
        entry: dict = {"geng_file": str(g6.relative_to(WT)), "sha256": h, "sha256_matches_C1": h == recorded.get(g6.name)}
        fast = run_fast(binary, n, g6, SCR / f"val_fast_n{n}.json", None)
        c1 = json.load(open(SCR_C1 / f"enc{n}.json"))
        fast_c = sorted(c["graph6"] for c in fast["candidates"])
        c1_c = sorted(c["graph6"] for c in c1["candidates"])
        entry["summary"] = {"graphs_fast": fast["graphs"], "graphs_C1": c1["graphs"], "excluded_fast": fast["excluded_certified"],
                            "excluded_C1": c1["excluded_certified"], "candidates_fast": len(fast_c), "candidates_C1": len(c1_c),
                            "candidate_sets_identical": fast_c == c1_c, "bad_lines": fast["bad_lines"],
                            "guard_fail": fast["guard_fail"], "chol_fail": fast["chol_fail"], "regular_fast": fast["regular"],
                            "max_eps_fast": fast["max_eps"], "max_eps_C1": c1["max_eps"],
                            "min_gap_fast": fast["min_certified_gap_among_excluded"],
                            "min_gap_C1": c1["min_certified_gap_among_excluded"]}
        s = entry["summary"]
        ok = (entry["sha256_matches_C1"] and s["graphs_fast"] == s["graphs_C1"] and s["excluded_fast"] == s["excluded_C1"]
              and s["candidate_sets_identical"] and s["bad_lines"] == 0)
        # per-graph comparison
        if n <= 9:
            src = g6
            label = "all graphs"
        else:
            src = SCR / "val_n10_stride11_1e6.g6"
            with open(g6) as fi, open(src, "w") as fo:
                k = 0
                for i, line in enumerate(fi):
                    if i % 11 == 0:
                        fo.write(line)
                        k += 1
                        if k == 1_000_000:
                            break
            label = "every 11th line from line 0, first 10^6"
        vf = SCR / f"val_fast_n{n}.tsv"
        vp = SCR / f"val_py_n{n}.tsv"
        run_fast(binary, n, src, SCR / f"val_fast_n{n}_v.json", vf)
        subprocess.run(["taskset", "-c", CORE, PY, "-I", str(HERE / "py_pergraph.py"), str(src), str(n), str(vp)], check=True,
                       stdout=subprocess.DEVNULL)
        cmp = compare_tsv(vf, vp)
        cmp["sample"] = label
        entry["per_graph"] = cmp
        ok = ok and cmp["graph6_mismatch"] == 0 and cmp["verdict_mismatch"] == 0 and cmp["intervals_not_intersecting"] == 0
        entry["ok"] = ok
        entry["seconds"] = round(time.time() - t0, 1)
        all_ok = all_ok and ok
        report["per_N"][str(n)] = entry
        print(n, json.dumps(entry), flush=True)
        for p in (vf, vp):
            p.unlink()
    report["all_ok"] = all_ok
    json.dump(report, open(out_path, "w"), indent=1)
    print("ALL_OK" if all_ok else "VALIDATION_FAILED", flush=True)


if __name__ == "__main__":
    main()
