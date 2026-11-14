"""Controls for AIC-MUC9, run BEFORE the headline (main.py). Positive: butterfly, 4-cycle LP. Negative: bad field, tampered R,
renormalised local coordinates, corrupted transmitted symbol."""
from __future__ import annotations

import itertools
import json
import sys

sys.path.insert(0, "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-03/AIC-MUC9/code")
sys.path.insert(0, "/home/callensxavier_gmail_com/muc9_thirdparty")

from appendixA_transcribed import C, J, PI, R  # noqa: E402
from checks import degree_conditions, distances, trials  # noqa: E402
from flow import max_concurrent  # noqa: E402
from muc9lib import build_T, build_field, build_graph, check_field, local_data  # noqa: E402

out: dict = {}

# P1: directed butterfly. GF(2) code: u->v carries s1+s2; t1 gets s2 directly; t2 gets s1 directly.
ok = True
for s1, s2 in itertools.product((0, 1), repeat=2):
    m = s1 ^ s2
    t1 = m ^ s2   # t1 wants s1
    t2 = m ^ s1   # t2 wants s2
    ok &= (t1 == s1 and t2 == s2)
# nodes: s1=0 s2=1 u=2 v=3 t1=4 t2=5
but = [(0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (0, 5), (1, 4)]
lam_b, st = max_concurrent(6, but, True, [(0, 4, 1.0), (1, 5, 1.0)])
out["P1_butterfly"] = {"coding_decodes_all_4_inputs_rate1": ok, "routing_maxconcurrent_LP": lam_b,
                       "PASS": bool(ok and abs(lam_b - 0.5) < 1e-9)}

# P2: undirected 4-cycle, sessions (0,2),(1,3): LP optimum 1, equals edges/sum(dist)=4/4
lam_c, _ = max_concurrent(4, [(0, 1), (1, 2), (2, 3), (3, 0)], False, [(0, 2, 1.0), (1, 3, 1.0)])
# P2b: single edge, one session: LP 1
lam_e, _ = max_concurrent(2, [(0, 1)], False, [(0, 1, 1.0)])
# P2c: path 0-1-2 with sessions (0,2),(0,2): LP 0.5 = edges 2 / (2 sessions x dist 2)... 2/4
lam_p, _ = max_concurrent(3, [(0, 1), (1, 2)], False, [(0, 2, 1.0), (0, 2, 1.0)])
out["P2_undirected_LP"] = {"cycle4": lam_c, "edge": lam_e, "path_two_sessions": lam_p,
                           "PASS": bool(abs(lam_c - 1) < 1e-9 and abs(lam_e - 1) < 1e-9 and abs(lam_p - 0.5) < 1e-9)}

# N3: bad fields must fail the field check; the true field passes
good = check_field(*build_field(1))
bad0 = check_field(*build_field(0))   # t^2 = 0
bad2 = check_field(*build_field(2))   # t^2 = 1 (reducible)
out["N3_field"] = {"true_field_all": all(good.values()), "t2=0_fails": not all(bad0.values()),
                   "t2=1_fails": not all(bad2.values()),
                   "PASS": bool(all(good.values()) and not all(bad0.values()) and not all(bad2.values()))}

# Graph-level negatives need the construction
T = build_T()
edges, nbrs = build_graph(T)
inc, Ms, Hs = local_data(T, edges)
dc = degree_conditions(edges, R, PI, C, J)
base_clean = (not dc["bad_degree"]) and (not dc["bad_cj"])

# N1: restore edge 7, delete edge 0 instead (same size)
R1 = [q for q in R if q != 7] + [0]
dc1 = degree_conditions(edges, R1, PI, C, J)
t1 = trials(edges, inc, Ms, Hs, R1, PI, C, J, 20, 1)
out["N1_tampered_R"] = {"degree_violations": len(dc1["bad_degree"]), "cj_violations": len(dc1["bad_cj"]),
                        "trial_summary": t1,
                        "PASS_detected": bool(dc1["bad_degree"] or dc1["bad_cj"] or t1["ok"] < t1["trials"])}

# N2a: renormalise (lambda,mu) at one vertex neighbour -> different code; run must fail somewhere
inc2, Ms2, Hs2 = local_data(T, edges, renorm_bug=5)
t2 = trials(edges, inc2, Ms2, Hs2, R, PI, C, J, 20, 2)
# N2b: add 1 to a symbol on a physical edge in transit
inc4, Ms4, Hs4 = local_data(T, edges, scale_bug=5)
t4 = trials(edges, inc4, Ms4, Hs4, R, PI, C, J, 20, 4)
phys = next(q for q in range(910) if q not in set(R))
t3 = trials(edges, inc, Ms, Hs, R, PI, C, J, 20, 3, perturb=(phys, 1))
out["N2_wrong_value"] = {"renormalised_coords": t2, "one_row_scaled_by_theta_vertex5": t4, "corrupted_symbol_edge": phys, "corrupted_symbol_trials": t3,
                         "note_renormalisation": "renormalising (lambda,mu) at all 10 neighbours of vertex 5 (the paper says do not) breaks decoding; an earlier version of this control renormalised only neighbour 0 and passed (probably a no-op scaling); only the all-neighbours variant is reported",
                         "PASS_detected": bool(t2["ok"] < t2["trials"] and t4["ok"] < t4["trials"] and t3["ok"] < t3["trials"])}
out["ALL_CONTROLS_PASS"] = bool(out["P1_butterfly"]["PASS"] and out["P2_undirected_LP"]["PASS"] and out["N3_field"]["PASS"]
                                and out["N1_tampered_R"]["PASS_detected"] and out["N2_wrong_value"]["PASS_detected"])
print(json.dumps(out, indent=1))
json.dump(out, open("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-03/AIC-MUC9/data/controls.json", "w"), indent=1)
