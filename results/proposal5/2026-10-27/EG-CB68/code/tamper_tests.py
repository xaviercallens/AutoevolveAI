#!/usr/bin/env python3
"""tamper_tests.py -- negative control N3: the checker must reject altered certificate streams.

usage: tamper_tests.py CERT(plain text, accepted) WORKDIR OUTJSON [--fast]   (--fast: test cb_check_fast instead of cb_check.py)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


FAST = "--fast" in sys.argv


def run_checker(checker: Path, stream: Path) -> dict:
    if FAST:
        with open(stream) as fh:
            cp = subprocess.run([str(checker.with_name("cb_check_fast"))], stdin=fh, capture_output=True, text=True)
    else:
        cp = subprocess.run([sys.executable, "-I", str(checker), str(stream)], capture_output=True, text=True)
    return {"exit": cp.returncode, "out": json.loads(cp.stdout.strip().splitlines()[-1])}


def main() -> int:
    cert, work, outj = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    checker = Path(__file__).with_name("cb_check.py")
    lines = cert.read_text().splitlines(keepends=True)
    first = {t: next(i for i, l in enumerate(lines) if l.startswith(t + " ")) for t in ("S", "8", "G", "E")}
    variants: dict[str, list[str]] = {}
    variants["truncated"] = lines[: len(lines) // 2]
    end = lines[-1].split()
    end[2] = str(int(end[2]) + 1)
    variants["counter_flipped"] = lines[:-1] + [" ".join(end) + "\n"]
    t = lines[first["8"]].split()
    t[5] = str(int(t[5]) + 64 if int(t[5]) < 64 else int(t[5]) - 1)
    variants["c8_witness_corrupted"] = lines[: first["8"]] + [" ".join(t) + "\n"] + lines[first["8"] + 1:]
    t = lines[first["G"]].split()
    t2 = t[:3] + t[3:][::-1][:-1]  # shortened, wrong length
    variants["c16_witness_wrong_length"] = lines[: first["G"]] + [" ".join(t2) + "\n"] + lines[first["G"] + 1:]
    t = lines[first["G"]].split()
    variants["c16_relabelled_as_structural"] = lines[: first["G"]] + [f"S {t[1]} {t[2]}\n"] + lines[first["G"] + 1:]
    variants["record_deleted"] = lines[: first["S"]] + lines[first["S"] + 1:]
    variants["trailing_data"] = lines + ["S 1 2\n"]
    variants["fake_completion_inserted"] = lines[: first["E"] + 1] + ["C\n"] + lines[first["E"] + 1:]
    res: dict[str, object] = {"base": run_checker(checker, cert)}
    for name, body in variants.items():
        p = work / f"tamper_{name}.txt"
        p.write_text("".join(body))
        r = run_checker(checker, p)
        res[name] = {"rejected": r["exit"] != 0 and not r["out"].get("accepted"), "error": r["out"].get("error")}
        p.unlink()
    res["all_tampered_rejected"] = all(v["rejected"] for k, v in res.items() if k != "base")
    res["base_accepted"] = bool(res["base"]["out"].get("accepted"))  # type: ignore[index]
    outj.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))
    return 0 if res["all_tampered_rejected"] and res["base_accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())
