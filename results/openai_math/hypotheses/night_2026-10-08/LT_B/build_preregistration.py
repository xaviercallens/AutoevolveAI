#!/usr/bin/env python3
"""Writes LT_B/preregistration.json (sha256 of every code path taken at write time).  Run once, before any lane result."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery")
LANE = REPO / "results/openai_math/hypotheses/night_2026-10-08/LT_B"


def sha(p: str) -> str:
    return hashlib.sha256((REPO / p).read_bytes()).hexdigest()


LT = "scripts/openai_math/lt_matrix/"

cells_p1 = [("control_gamma1.5_m3", 1.5, "random"), ("g1.0_random", 1.0, "random"), ("g1.0_embed", 1.0, "embed"), ("g1.0_twist", 1.0, "twist"),
            ("g1.25_random", 1.25, "random"), ("g1.25_embed", 1.25, "embed"), ("g1.25_twist", 1.25, "twist")]
seed_table = []
for c, (name, g, fam) in enumerate(cells_p1):
    base = 2000 + 100 * c
    seed_table.append({"cell": name, "gamma": g, "family": fam, "m": 3, "seed_block": [base, base + 99],
                       "calls": [{"seed0": base + 2 * j, "restarts": 2, "out": f"part1/{name}_call{j}.json"} for j in range(4)]})

P = {
    "lane": "LT_B", "date": "2026-10-08", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "stage": "preregistration; written after code + smoke tests, before any lane result (part 1 campaign rows: none; part 2 production cells: none)",
    "hypotheses": {
        "H-LT1_m3": "sup R over m = 3 matrix potentials <= L1(gamma) for gamma in {1.0, 1.25}; control cell gamma = 1.5 (sup = 3/16, proved for operator-valued potentials) is not exceeded. Verdict categories and rule are those of results/openai_math/hypotheses/lt_matrix/preregistration.json (VOID / VIOLATION_CERTIFIED / UNDECIDED / NO_VIOLATION_FOUND), unchanged.",
        "H-LT3": "The embedded scalar extremiser theta0 (B* = diag(sqrt(r+1) sech(r x), 0..0), r = 1/(gamma-1/2)) is a local maximum of log R in matrix directions: the Hessian of log R at theta0, restricted to the Euclidean orthogonal complement of {translation, dilation}, has no eigenvalue above threshold.",
    },
    "part2_design": {
        "parametrisation": "theta = (Re c, Im c, log kappa, x0) of ONE Blobs blob (K=1), P = 8 Chebyshev-in-tanh orders; n = 2 m^2 (P+1) + 2 (m=1: 20, m=2: 74, m=3: 164). Perturbation C ranges over ALL coordinates including kappa and x0, so translation (e_x0) and dilation (e_logk + sqrt(r+1) e_c000) are tangent vectors.",
        "objective": "Hessian by torch autograd of a smooth surrogate (second_variation.Surrogate) whose value/gradient/Hessian at theta0 equal those of log R: numerator = Rayleigh quotients of first-order perturbed bound states, denominator = int (W11 + |W_j1|^2/W11)^(gamma+1/2). The surrogate omits lesser eigenvalues of W (O(eps^2)), whose denominator contribution O(eps^(2gamma+1)) is non-negative, so the surrogate can only overestimate R (conservative for a kill test). The finite-eps confirmation uses the TRUE eigen-based R, which includes that term; a positive direction whose confirmation fails only because of that term is UNDECIDED, never a pass. Why a surrogate: eigh/eigvalsh double backward divides by zero gaps at the degenerate zero channels.",
        "restricted_hessian": "Z = orthonormal basis of the Euclidean complement of {translation, dilation}; Hr = Z^T H Z; full spectrum is reported.",
        "grids_frozen_from_smoke": {
            "note": "Dirichlet box half-width L, sine modes M, Gauss nodes Q; escalation applies only if a gate fails at the frozen grid, and is then disclosed",
            "0.75": {"L": 14, "M": 360, "Q": 1600, "escalation_if_gates_fail": {"M": 440}},
            "1.0": {"L": 14, "M": 200, "Q": 1600, "escalation_if_gates_fail": {"M": 240}},
            "1.25": {"L": 14, "M": 160, "Q": 1600, "escalation_if_gates_fail": {"M": 200}},
            "1.4": {"L": 14, "M": 160, "Q": 1600, "escalation_if_gates_fail": {"M": 200}},
            "3.0_negative_control_only": {"L": 40, "M": 240, "Q": 2000},
        },
        "cells": "gamma in {0.75, 1.0, 1.25, 1.4} x m in {1, 2, 3} (m = 1 is control a), plus gamma = 3 x m in {1, 2} (control c). Priority order if compute runs out: m=1 all gamma, m=2 all gamma, m=3 gamma 1.25, 1.0, 1.4, 0.75; cells not run are reported BLOCKED, never estimated.",
        "thresholds": {"tol_abs": 1e-8, "tol_rel": 1e-6, "positive_threshold": "lambda > max(tol_rel * spectral_norm(Hr), tol_abs)", "tol_flat_quad": 1e-8, "tol_gradient": 1e-6,
                       "eps_list": [1e-3, 2e-3, 4e-3], "confirm_noise_floor_delta_logR": 1e-12},
        "expected_zero_modes_lower_bound": "2 (m-1) m (P+1) [rows >= 2 of C: stationary by the scalar Euler-Lagrange equation, or only O(eps^(2gamma+1)) effects] + (P+1) [x-dependent phase, Im c_00p] + 2 (m-1) [right rotations]; m=1, P=8: 9 (observed 10 in an L=24 smoke at gamma=1); extra soft modes are a reportable finding, not noise.",
        "note_on_finite_difference_of_dilation": "FD second differences along the dilation LINE theta0 + eps*e are about -2e-7..-6e-7 and independent of the grid: this is O(eps^2) bias from the curvature of the symmetry orbit versus a straight line, NOT non-flatness. Control (b) is judged on the autograd quadratic form u^T H u.",
    },
    "decision_rule_H_LT3": {
        "per_cell_gates_in_order": [
            "VOID_FD_DISAGREES: autograd quadratic form vs central FD (eps = 1e-3) of the TRUE eigen-based log R along 3 random row-0-only directions (W exactly rank one there, so the surrogate is exact), and vs FD of the surrogate along 3 top eigenvectors + the same 3 directions, differ by more than 1e-4 * max(1, |q|)",
            "VOID_NOT_CRITICAL: gradient norm of log R at theta0 > 1e-6 (gamma < 3/2 cells)",
            "VOID_FLAT_DIRECTION_NOT_FLAT: max |u^T H u| over translation, dilation > 1e-8 (control b)",
        ],
        "then": {
            "NONPOSITIVE_SECOND_VARIATION": "no restricted eigenvalue above positive_threshold (supports H-LT3 for that cell)",
            "POSITIVE_CONFIRMED_KILLS_H_LT3": "some eigenvalue above threshold AND, on the refined grid (2M, 2Q), log R(theta0 +- eps v) - log R(theta0) > 1e-12 for both signs at eps = 1e-3 and 2e-3 (kills H-LT3 for that cell; the explicit potential then goes to the H-LT1 refinement route: refined grid + independent finite-difference certification)",
            "UNDECIDED_POSITIVE_UNCONFIRMED": "eigenvalue above threshold but finite-eps confirmation fails (abstains; never counted as a pass)",
        },
        "lane_level_controls_all_required": {
            "a": "m = 1 at the same gamma and grid: verdict NONPOSITIVE_SECOND_VARIATION (all restricted eigenvalues <= threshold)",
            "b": "per cell, above",
            "c": "gamma = 3, m = 1 and m = 2, flag --negative-control: theta0 is NOT critical there (smoke: gradient 0.43); pass iff at least one restricted eigenvalue is above threshold AND confirmed at finite eps (NEGATIVE_CONTROL_PASS). If it fails, ALL H-LT3 numbers of the lane are VOID",
            "d": "autograd vs FD agreement (VOID_FD_DISAGREES gate)",
        },
        "spectrum": "the full restricted spectrum, counts of positive / zero / negative modes and the largest eigenvalue are stored in each cell JSON and reported.",
    },
    "part1_design": {
        "cells": "m = 3, K = 2, P = 8: gamma in {1.0, 1.25} x family in {random, embed, twist}, plus control cell gamma = 1.5 (family random; run FIRST; if any restart's refined-grid excess over 3/16 exceeds 1e-5 the control FAILS and every part-1 cell is VOID)",
        "driver": "campaign.py unchanged (frozen sha256 below), grid default L=24, M=160, launched with env OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 and --threads 2; each call = --restarts 2 --budget-s 450 --seed0 <table> --out <distinct file>; 4 calls per cell = 8 restarts per cell (minimum), more calls with the next unused seeds of the same block if time allows. Deviation from the brief's 'one cell per call': campaign.py checks the budget only before each restart, so a 450 s budget can run to about 630 s plus refinement, over the 9-minute cap; calls are therefore 2 restarts each and a cell is the union of its calls.",
        "seed_table_never_reused": seed_table,
        "cell_verdict": "union of restarts over the cell's calls under the frozen verdict rule of lt_matrix/preregistration.json; a cell with fewer than 8 completed restarts is INCOMPLETE and reported as such",
        "controls": "frozen controls.json (sha256 in lt_matrix/preregistration.json) is reused, not re-run; the gamma = 1.5 cell is the lane's own positive control",
    },
    "budget": {"cpu": "one python process, 2 threads (second_variation.py sets OMP/MKL/OPENBLAS threads to 2 before numpy/torch import; campaign.py is frozen and launched with those env vars)",
               "per_bash_call": "< 9 min; long cells run resumably per (gamma, m) file; no cell JSON is hand-edited",
               "gpu": "not used"},
    "code_sha256": {
        LT + "second_variation.py": sha(LT + "second_variation.py"),
        "tests/openai_math/test_lt_second_variation.py": sha("tests/openai_math/test_lt_second_variation.py"),
        LT + "instrument.py": sha(LT + "instrument.py"), LT + "campaign.py": sha(LT + "campaign.py"), LT + "controls.py": sha(LT + "controls.py"),
        "results/openai_math/hypotheses/lt_matrix/preregistration.json": sha("results/openai_math/hypotheses/lt_matrix/preregistration.json"),
    },
    "frozen_files_unchanged": "instrument.py, controls.py, campaign.py are imported/launched as is; no copies, so no deviations.md entry is needed",
    "smoke_values_seen_before_registration": [
        "tests: tests/openai_math/test_lt_second_variation.py + test_lt_matrix.py: 15 passed in 94.95 s (pytest output, after the last test edit; the script was not edited afterwards)",
        "m=2, gamma=1, tiny grid (P=3, M=60, Q=400, L=24): verdict VOID_FD_DISAGREES, lambda_max 1.23, translation/dilation quad 0.042. CAUSE FOUND LATER: bug in the surrogate (abs()**2 has zero gradient at 0 and dropped the |b|^2/a term from the Hessian for m>=2). Fixed before hashing. A pre-fix m=3 smoke (gamma=1.25, L=14, M=160, P=8, smoke/smoke_g125_m3.json: VOID_FD_DISAGREES, 36 spurious positive eigenvalues up to 1.98) is INVALID for the same reason and is kept only as evidence of the bug.",
        "m=1, gamma=1, P=8, L=24, M=160, Q=1200: excess over L1 -6.5e-7, gradient 1.7e-4, translation/dilation quad 3.6e-5 (fails control b: Galerkin truncation); M=320, Q=2400: excess -6.6e-14, gradient 5.1e-9, quad 2.2e-11, lambda_max 1.25e-8 (below threshold ~1e-6), verdict NONPOSITIVE_SECOND_VARIATION",
        "grid convergence of ||grad log R|| at theta0 (m=1, P=8): L=24: gamma 0.75 M 160/200/240 -> 3.6e-3/1.0e-3/3.1e-4; gamma 1.0 M 160/200/240 -> 1.7e-4/1.8e-5/1.4e-6; gamma 1.4 M 160/200/240 -> 4.0e-7/2.1e-9/7.4e-12. L=12 floor about 1e-8 (box effect). L=16: gamma 0.75 M 200/280 -> 5.6e-5/1.7e-6. L=14: gamma 0.75 M 320/360 -> 2.2e-8/1.8e-9; gamma 1.0 M160 1.4e-7; gamma 1.25 M160 1.7e-10; gamma 1.4 M160 2.2e-10. The frozen grids above were chosen from these.",
        "m=2, gamma=1, P=4, L=14, M=160, Q=1600 (after the fix): NONPOSITIVE_SECOND_VARIATION, lambda_max 1.13e-8, gradient 5.8e-9, translation/dilation quad 2.2e-9 (marginal against 1e-8, hence M=200 for gamma=1), 28 zero modes, 12 negative, 0 positive beyond threshold; FD gates passed",
        "m=1, gamma=3, P=8, L=40, M=240, Q=2000 (negative control): gradient 0.433 (not critical), excess over the one-bound-state L1(3) +4.67%, 3 bound states, 9 positive restricted eigenvalues (max 0.523), 5 confirmed positive at finite eps; the verdict string VOID_FLAT_DIRECTION_NOT_FLAT in that file came from the old gate order and is replaced by the --negative-control rule",
        "m=2 and m=3 production-grid timings, and gamma=3 with m=2: not seen. The pre-fix m=3 smoke took 195.6 s on a loaded machine (load average about 19).",
    ],
    "open_design_questions": [
        "The Euclidean metric on theta fixes the restricted subspace and the eigenvalue magnitudes (not their signs); a metric weighted by the Fisher information of W was not considered.",
        "Directions in rows >= 2 of C are second-order flat and change R only at O(eps^(2gamma+1)) (negative) or O(eps^4) via off-diagonal W coupling: the Hessian cannot decide local maximality there; a finite-eps scan to eps = 0.1 on random null-space directions is reported as an exploratory secondary table, not a verdict.",
        "K = 1 blob and P = 8 truncation: perturbations needing a second soliton (rotpair) belong to the H-LT1 campaign, not covered here.",
        "m=3 at gamma = 0.75 (Galerkin matrix 1080 x 1080) may not finish inside the night; it is last in priority and may be BLOCKED.",
        "Positive eigenvalues between 1e-8 and 1e-6 (relative 1e-6) are treated as noise by fiat; finite-eps confirmation cannot resolve them (delta log R about 1e-14).",
        "The exploratory far-eps null-space scan is not implemented in second_variation.py; it would need a new script and a deviations note before use.",
    ],
    "assets_used": ["Elenchus Maieutics method (fixed budget, immutable evaluator, mechanical verdicts)", "Mensura-style abstaining verdict (UNDECIDED)", "frozen lt_matrix instruments"],
    "files_to_commit": [
        LT + "second_variation.py", "tests/openai_math/test_lt_second_variation.py",
        "results/openai_math/hypotheses/night_2026-10-08/LT_B/preregistration.json",
        "results/openai_math/hypotheses/night_2026-10-08/LT_B/build_preregistration.py",
        "results/openai_math/hypotheses/night_2026-10-08/LT_B/smoke/",
    ],
}
(LANE / "preregistration.json").write_text(json.dumps(P, indent=2) + "\n")
print("wrote", LANE / "preregistration.json")
