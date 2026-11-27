"""Write RESULT.md from code/RESULT.template.md and result.json + driver logs (no hand-typed numbers)."""
from __future__ import annotations

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ranges(xs: list[int]) -> str:
    out, i = [], 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[j] + 1:
            j += 1
        out.append(f"{xs[i]}" if i == j else f"{xs[i]}-{xs[j]}")
        i = j + 1
    return ", ".join(out) if out else "none"


def frontier_attempts() -> dict:
    """Per n >= 36: number of driver attempts, successes, and CPU, from all driver logs."""
    st: dict = {}
    for p in sorted(glob.glob(os.path.join(ROOT, "logs", "*.log"))):
        for m in re.finditer(r"^n=(\d+) attempt=\d+ .*?budget=([0-9.]+) rc=(\d+) END .* cpu=([0-9.]+)$|^n=(\d+) attempt=\d+ seed=\d+ rc=(\d+) END .* cpu=([0-9.]+)$",
                             open(p).read(), re.M):
            if m.group(1):
                n, rc, cpu = int(m.group(1)), int(m.group(3)), float(m.group(4))
            else:
                n, rc, cpu = int(m.group(5)), int(m.group(6)), float(m.group(7))
            if n < 36:
                continue
            d = st.setdefault(n, {"attempts": 0, "successes": 0, "cpu_s": 0.0})
            d["attempts"] += 1
            d["successes"] += int(rc == 0)
            d["cpu_s"] += cpu
    return st


def main() -> None:
    r = json.load(open(os.path.join(ROOT, "result.json")))
    nmax = r["contiguous_closed_range"][1]
    lines = ["| n | status | v = [n]? | max v | D | file |", "|---|---|---|---|---|---|"]
    for row in r["table"]:
        if row["status"] == "OPEN":
            lines.append(f"| {row['n']} | OPEN (no certificate) | | | | |")
        else:
            lines.append(f"| {row['n']} | {row['status']} | {'yes' if row['v_is_[n]'] else 'no'} | {row['max_v']} | {row['D']} | certificates/{row['file']} |")
    fa = frontier_attempts()
    stopped_by_budget = any("STOP total CPU budget reached" in open(p).read()
                            for p in glob.glob(os.path.join(ROOT, "logs", "*.log")))
    stop = ("**Stop reason: the total CPU budget was reached** (driver STOP line in the swap5 log; cap 107000 s cumulative "
            "including the ledger offset)." if stopped_by_budget else
            "**Stop reason: the agent stopped the search before the 30 core-hour budget was used** (see summary).")
    stop += " Frontier attempts per n (driver logs, n >= 36): " + "; ".join(
        f"n={n}: {d['successes']}/{d['attempts']} attempts succeeded, {d['cpu_s']:.0f} CPU-s" for n, d in sorted(fa.items())) + "."
    t = open(os.path.join(ROOT, "code", "RESULT.template.md")).read()
    t = (t.replace("@@STATUS@@", r["status"]).replace("@@CERTLIST@@", ranges(r["certified_n_ge_18"]))
         .replace("@@NMAX@@", str(nmax)).replace("@@NOPEN@@", str(nmax + 1))
         .replace("@@TABLE@@", "\n".join(lines)).replace("@@CPU@@", str(r["cpu_hours_total"]))
         .replace("@@STOP@@", stop))
    assert "@@" not in t
    open(os.path.join(ROOT, "RESULT.md"), "w").write(t)
    print(nmax, r["status"], ranges(r["certified_n_ge_18"]), r["cpu_hours_total"], stopped_by_budget)


if __name__ == "__main__":
    main()
