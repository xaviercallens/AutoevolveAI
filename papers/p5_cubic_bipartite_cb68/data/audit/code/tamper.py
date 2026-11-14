#!/usr/bin/env python3
"""Auditor tamper tests for EG-CB68 checkers. Builds tampered copies of an honest cap-29 orbit-1 certificate
and runs cb_check.py, cb_check_fast and aud_check on each. Expected: every tampered stream rejected,
except the header-parameter tampers, which test whether a checker trusts the header."""
from __future__ import annotations

import subprocess
import sys

SRC = "/home/callensxavier_gmail_com/EG-CB68_scratch/P1_cap29_o1.cert"
W = "/tmp/egaudit/tamper"
PY = "/tmp/egaudit/prod/cb_check.py"
FAST = "/tmp/egaudit/prod/cb_check_fast"
AUD = "/tmp/egaudit/mine/aud_check"


def load() -> list[str]:
    with open(SRC) as fh:
        return fh.read().splitlines(keepends=True)


def first(lines: list[str], pred) -> int:
    for i, s in enumerate(lines):
        if pred(s):
            return i
    raise ValueError("no match")


def variants(L: list[str]) -> dict[str, list[str]]:
    v: dict[str, list[str]] = {}
    i8 = first(L, lambda s: s.startswith("8 "))
    iG = first(L, lambda s: s.startswith("G "))
    iS = first(L, lambda s: s.startswith("S "))
    iE = first(L, lambda s: s.startswith("E "))
    # witness ending at a non-introduced point (label 40 > cap)
    t = L[i8].split(); t[-1] = "40"; x = L.copy(); x[i8] = " ".join(t) + "\n"; v["w_end_fresh"] = x
    # non-simple walk: path a B b B a ... (repeat first point at position 4)
    t = L[i8].split(); t[3 + 4] = t[3]; x = L.copy(); x[i8] = " ".join(t) + "\n"; v["w_not_simple"] = x
    # G witness truncated to length 12 (13 vertices), endpoint kept
    t = L[iG].split(); path = t[3:]; newp = path[:12] + [path[-1]]
    x = L.copy(); x[iG] = " ".join(t[:3] + newp) + "\n"; v["G_len12"] = x
    # G record re-tagged as 8 (wrong length for tag)
    x = L.copy(); x[iG] = "8" + L[iG][1:]; v["G_as_8"] = x
    # delete an S line
    x = L.copy(); del x[iS]; v["del_S"] = x
    # duplicate an S line
    x = L.copy(); x.insert(iS, L[iS]); v["dup_S"] = x
    # swap two consecutive 8 records
    x = L.copy(); x[i8], x[i8 + 1] = x[i8 + 1], x[i8]; v["swap_records"] = x
    # false structural: turn the first 8 rejection into S
    t = L[i8].split(); x = L.copy(); x[i8] = f"S {t[1]} {t[2]}\n"; v["false_S"] = x
    # drop a whole expansion subtree: replace 'E q r' ... matching 'U' by an S record
    depth = 0; j = iE
    while True:
        s = L[j]
        if s.startswith("E "): depth += 1
        elif s == "U\n":
            depth -= 1
            if depth == 0: break
        j += 1
    t = L[iE].split(); x = L[:iE] + [f"S {t[1]} {t[2]}\n"] + L[j + 1:]; v["drop_subtree_as_S"] = x
    # header tampers (parameters taken from the stream)
    x = L.copy(); x[0] = "R 29 1 c6\n"; v["hdr_add_c6"] = x
    x = L.copy(); x[0] = "R 30 1\n"; v["hdr_cap30"] = x
    x = L.copy(); x[0] = "R 29 2\n"; v["hdr_orbit2"] = x
    return v


def run(path: str) -> dict[str, int]:
    r = {}
    with open(path) as fh:
        r["py"] = subprocess.run([sys.executable, "-I", PY, path], capture_output=True).returncode
        fh.seek(0)
        r["fast"] = subprocess.run([FAST], stdin=fh, capture_output=True).returncode
        fh.seek(0)
        r["aud"] = subprocess.run([AUD, "29", "1"], stdin=fh, capture_output=True).returncode
    return r


def main() -> None:
    import os
    os.makedirs(W, exist_ok=True)
    L = load()
    base = run(SRC)
    print("honest", base)
    for name, lines in variants(L).items():
        p = f"{W}/{name}.cert"
        with open(p, "w") as fh:
            fh.writelines(lines)
        print(name, run(p))


if __name__ == "__main__":
    main()
