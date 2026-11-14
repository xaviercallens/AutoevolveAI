import glob, json
from collections import defaultdict
from bistab import *
from table1 import T1_TEXT

lab, reps = enumerate_all()
net27 = {tuple(sorted(parse_edge(t) for t in l.split()[1:])) for l in T1_TEXT.splitlines()}
pos_idx = {i for i, r in enumerate(reps) if r in net27 or swap_set(r) in net27}
agg = defaultdict(lambda: dict(samples=0, cand=0, ver=0, unver=0, ex=None))
files = sorted(glob.glob("../data/p6_search_seed1*_part*.json"))
for fn in files:
    for k, v in json.load(open(fn)).items():
        a_ = agg[int(k)]
        a_["samples"] += v["n_samples"]; a_["cand"] += v["n_candidate_hits"]
        a_["ver"] += v["verified"]; a_["unver"] += v["unverified"]
        if v["verified_examples"] and a_["ex"] is None:
            a_["ex"] = v["verified_examples"][0]
assert len(agg) == 681, len(agg)
pos_found = [i for i in pos_idx if agg[i]["ver"] > 0]
neg_hits = [i for i in agg if i not in pos_idx and agg[i]["ver"] > 0]
neg_cand = [i for i in agg if i not in pos_idx and agg[i]["cand"] > 0]
tot = sum(a_["samples"] for a_ in agg.values())
summ = dict(files=len(files), networks=len(agg), samples_total=tot, samples_per_network=tot // 681,
            positives_total=len(pos_idx), positives_with_verified_exact_two_sink_hit=len(pos_found),
            positives_missed=[i for i in pos_idx if i not in pos_found],
            negatives=681 - len(pos_idx), negatives_with_exact_verified_two_sinks=neg_hits,
            negatives_with_unverified_candidates=neg_cand,
            positive_hit_rates={i: agg[i]["cand"] / agg[i]["samples"] for i in sorted(pos_idx)})
json.dump(summ, open("../data/p7_search_summary.json", "w"), indent=1)
print({k: v for k, v in summ.items() if k != "positive_hit_rates"})
print("min/max candidate hit-rate among positives:", min(summ["positive_hit_rates"].values()), max(summ["positive_hit_rates"].values()))
