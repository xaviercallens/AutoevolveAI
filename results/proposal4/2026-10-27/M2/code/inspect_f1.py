"""Characterise float-tolerance disagreements (F1) for the report. Usage: python inspect_f1.py <jdft_json> <per_entry_jsonl> <out_json>"""
from __future__ import annotations

import collections
import json
import sys


def main(src: str, per_entry: str, out: str) -> int:
    rs = [json.loads(line) for line in open(per_entry)]
    data = {d["jid"]: d for d in json.load(open(src))}
    f1 = [r for r in rs if r["F1"] != r["pd_exact"]]
    O: dict[str, object] = {"by_class": dict(collections.Counter(r["cls"] for r in f1))}
    tiny = 0
    zero_diag = 0
    ex = []
    for r in f1:
        t = data[r["jid"]]["elastic_tensor"]
        entries = [abs(v) for row in t for v in row if v != 0]
        if entries and min(entries) < 1e-6:
            tiny += 1
        if any(t[i][i] == 0 for i in range(6)):
            zero_diag += 1
        if len(ex) < 4:
            ex.append({"jid": r["jid"], "formula": data[r["jid"]]["formula"], "lmin": r["lmin"], "pivot_idx": r["pivot_idx"],
                       "interval": r["interval"], "tensor": t})
    O["with_entry_0<|v|<1e-6"] = tiny
    O["with_zero_diagonal_entry"] = zero_diag
    O["examples"] = ex
    json.dump(O, open(out, "w"), indent=1)
    print(json.dumps(O, indent=1)[:3500])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
