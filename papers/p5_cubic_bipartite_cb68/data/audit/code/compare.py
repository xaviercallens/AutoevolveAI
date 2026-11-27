#!/usr/bin/env python3
"""Compare auditor runs and certificate checks with the producer's recorded data."""
from __future__ import annotations

import json
import re

D = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal5/2026-10-27/EG-CB68"
O = "/tmp/egaudit/out"
K = ["states", "attempted", "structural", "c8", "c16", "completions"]


def j(p: str) -> dict:
    with open(p) as fh:
        return json.loads(fh.read())


def main() -> None:
    bad = 0
    # route 1
    for cap in range(30, 36):
        for o in (1, 2):
            pa = j(f"{D}/data/main/T_cap{cap}_o{o}_A.json")
            pb = j(f"{D}/data/main/T_cap{cap}_o{o}_B.json")
            pc = j(f"{D}/data/main/T_cap{cap}_o{o}_check.json")
            m = j(f"{O}/mine_T_cap{cap}_o{o}.json")
            ok = all(m[k] == pa[k] == pb[k] for k in K) and m["hash"] == pa["transcript_hash"] == pb["transcript_hash"]
            ok_chk = pc.get("accepted") and pc.get("flags") == [] and pc["cap"] == cap and pc["orbit"] == o \
                and pc["counters"]["c6"] == 0 and all(pc["counters"][k] == pa[k] for k in K)
            if cap <= 34:
                r = j(f"{O}/prod_T_cap{cap}_o{o}_A.json")
                ok = ok and all(r[k] == pa[k] for k in K) and r["transcript_hash"] == pa["transcript_hash"]
            aud = open(f"{O}/certs/T{cap}_o{o}.aud").read()
            fast = j(f"{O}/certs/T{cap}_o{o}.fast")
            mh = re.search(r"hash=(\w+)", aud)
            ok_aud = aud.startswith("ACCEPT") and mh and mh.group(1) == pa["transcript_hash"]
            ok_fast = fast.get("accepted") and fast["c6"] == 0 and fast["cap"] == cap and all(fast[k] == pa[k] for k in K)
            gz = open(f"{O}/certs/T{cap}_o{o}.gzsha").read().split()[0]
            pl = open(f"{O}/certs/T{cap}_o{o}.plainsha").read().split()[0]
            recorded = open(f"{D}/logs/main/cert_sha256.txt").read()
            ok_sha = gz in recorded and pl in recorded
            line = f"T cap{cap} o{o}: search={ok} prodcheckjson={ok_chk} aud_check={bool(ok_aud)} fast={ok_fast} sha={ok_sha} states={pa['states']}"
            print(line)
            bad += not (ok and ok_chk and ok_aud and ok_fast and ok_sha)
    # route 2
    for cap in range(29, 35):
        pa = j(f"{D}/data/main/R_cap{cap}_A.json")
        pb = j(f"{D}/data/main/R_cap{cap}_B.json")
        m = j(f"{O}/mine_R_cap{cap}.json")
        ok = all(m[k] == pa[k] == pb[k] for k in K) and m["hash"] == pa["transcript_hash"] == pb["transcript_hash"]
        extra = ""
        if cap <= 32:
            r = j(f"{O}/prod_R_cap{cap}_A.json")
            ok = ok and all(r[k] == pa[k] for k in K) and r["transcript_hash"] == pa["transcript_hash"]
            extra = f" prod_rebuilt_cpu={r['cpu_seconds']}"
        print(f"R cap{cap}: match={ok} states={m['states']} completions={m['completions']} hash={m['hash']} mine_cpu={m['cpu']}{extra} prod_cpu={pa['cpu_seconds']}")
        bad += not ok
    print("BAD", bad)


if __name__ == "__main__":
    main()
