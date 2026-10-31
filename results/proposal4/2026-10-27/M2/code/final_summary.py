"""Final aggregate numbers (null tensors, ehull/icsd context, headline ex-null counts). Tier X context items are labelled.
Usage: python final_summary.py <jdft_json> <per_entry_jsonl> <out_json>"""
from __future__ import annotations

import collections
import json
import math
import sys


def main(src: str, per_entry: str, out: str) -> int:
    rs = [json.loads(line) for line in open(per_entry)]
    data = {d["jid"]: d for d in json.load(open(src))}
    O: dict[str, object] = {}
    null_ids = set()
    for r in rs:
        t = data[r["jid"]]["elastic_tensor"]
        if max(abs(v) for row in t for v in row) < 1e-6:
            null_ids.add(r["jid"])
    O["numerically_null_tensors_max_abs_lt_1e-6"] = len(null_ids)
    nn = [r for r in rs if r["jid"] not in null_ids]
    O["N_excluding_null"] = len(nn)
    O["exact_NOT_PD_excluding_null"] = sum(not r["pd_exact"] for r in nn)
    O["exact_NOT_PD_fraction_excluding_null"] = sum(not r["pd_exact"] for r in nn) / len(nn)
    O["ROBUST_NOT_PD_excluding_null"] = sum(r["interval"] == "ROBUST_NOT_PD" for r in nn)
    O["ROBUST_PD_excluding_null"] = sum(r["interval"] == "ROBUST_PD" for r in nn)
    O["UNDECIDED_excluding_null"] = sum(r["interval"] == "UNDECIDED_BY_BOUND" for r in nn)
    O["linear_pass_but_exact_NOT_PD_excluding_null"] = sum(r["linear_pass"] and not r["pd_exact"] for r in nn)
    O["linear_pass_but_ROBUST_NOT_PD_excluding_null"] = sum(r["linear_pass"] and r["interval"] == "ROBUST_NOT_PD" for r in nn)
    O["linear_pass_total_excluding_null"] = sum(r["linear_pass"] for r in nn)
    O["F1_disagree_excluding_null"] = sum(r["F1"] != r["pd_exact"] for r in nn)
    O["F2_disagree_excluding_null"] = sum(r["F2"] != r["pd_exact"] for r in nn)
    O["F0_disagree_excluding_null"] = sum(r["F0"] != r["pd_exact"] for r in nn)
    bins = collections.defaultdict(lambda: [0, 0])
    for r in nn:
        e = data[r["jid"]].get("ehull")
        if isinstance(e, (int, float)) and math.isfinite(e):
            b = "ehull<=0.025" if e <= 0.025 else ("0.025<ehull<=0.1" if e <= 0.1 else "ehull>0.1")
            bins[b][0] += 1
            bins[b][1] += int(not r["pd_exact"])
    O["TierX_ehull_bins_[n,not_pd]"] = dict(bins)
    ic = collections.defaultdict(lambda: [0, 0])
    for r in nn:
        k = "has_icsd" if data[r["jid"]].get("icsd") not in (None, "", "na", []) else "no_icsd"
        ic[k][0] += 1
        ic[k][1] += int(not r["pd_exact"])
    O["TierX_icsd_[n,not_pd]"] = dict(ic)
    O["nonfinite_tensors_nan_or_inf"] = sum(
        1 for d in data.values() if isinstance(d.get("elastic_tensor"), list)
        and any(not math.isfinite(v) for row in d["elastic_tensor"] for v in row if isinstance(v, (int, float))))
    json.dump(O, open(out, "w"), indent=1)
    print(json.dumps(O, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
