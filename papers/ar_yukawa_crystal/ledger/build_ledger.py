"""Build the Elenchus claim ledger for the H2 planar-Yukawa preprint (papers/ar_yukawa_crystal).

Modelled on results/discovery/ledger/build_ledger.py. Every claim gets a content-addressed evidence blob
(evidence/<sha256>.json): compiled `#print axioms` output with source hashes (Tier A), primary-source excerpts with
line numbers (Tier L), argument text (Tier C), result files of the rusty-SUNDIALS exact-potential study (Tier X,
claim_licence false). Tier A rows keep audit = null: no person has audited statement adequacy.

Gate:  python3 <elenchus>/tools/ledger.py ledger.json --evidence-dir evidence --json
Usage: python -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[2]  # AutoevolveAI worktree
EV = HERE / "evidence"
H2 = W / "results/autoresearch/2026-10-25/H2"
FC = W / "formal_cert/Autoresearch"
DATA = HERE.parent / "data"
RUSTY = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h2/crates/qf-yukawa-crystal")
HF = Path("/home/callensxavier_gmail_com/hf-data/yukawa_crystal")
CKMRV = Path("/home/callensxavier_gmail_com/.claude/projects/-home-callensxavier-gmail-com-AutoevolveAI--claude-worktrees-openai-math-discovery/6ecda88c-9d6f-441a-9328-d4a192612987/tool-results/mcp-claude_ai_alphaXiv-get_paper_content-1791653555097.txt")
UPAPER = Path("/home/callensxavier_gmail_com/.claude/jobs/6ecda88c/tmp/upaper/preprints/Universal-optimality-of-the-triangular-lattice-September-23-2026/build/sections/01-uniform-gaussian-theorem.tex")
UPSTREAM = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
TOOLCHAIN = "Lean 4.34.1, Mathlib d13f23b7, openai/math pinned copy (scripts/certified_numerics/lean_pinned.py)"
ADEQ = ("statement adequacy audited by AI agents only (H2/verification.md for Autoresearch.Yukawa, on the prior-round "
        "bytes sha256 43e2df3ff9eca7ab6937904e8287311ebd6bae891e87324f501cff1dd0993bb4; the current file differs only in "
        "docstrings and its rebuilt axiom output is identical; "
        "contribution/verify for Autoresearch.YukawaMix); no human audit")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def file_ref(p: Path) -> dict:
    return {"path": str(p), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def axiom_lines(compile_json: Path, names: list[str]) -> list[str]:
    out = json.loads(compile_json.read_text())
    lines = [l.strip() for l in out["output"].splitlines()]
    got = [l for l in lines if any(f"'{n}'" in l for n in names)]
    if len(got) < len(names):
        raise SystemExit(f"axiom lines missing in {compile_json}: {names}")
    for l in got:
        if "[" + ", ".join(ALLOW) + "]" not in l:
            raise SystemExit(f"footprint outside the allowlist: {l}")
    return got


def lean_ev(compiles: list[Path], names: list[str], sources: list[Path]) -> dict:
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "allowlist": ALLOW,
            "axiom_output": {str(c): axiom_lines(c, [n for n in names if f"'{n}'" in c.read_text()]) for c in compiles},
            "compiles": [dict(file_ref(c), rc=json.loads(c.read_text())["rc"]) for c in compiles],
            "sources": [file_ref(s) for s in sources], "statement_adequacy": ADEQ}


CITE_CHECK = ("Elenchus tools/citation_check.py accepts only kind in (theorem, lemma, proposition, corollary) (KINDS, line 35); "
              "this row cites a definition, a convention, a remark or a footnote, so citation_check.py would refuse it on kind "
              "alone. The quotation was instead checked against the alphaXiv full text (extraction sha256 above) by the "
              "producer and again, independently, by the stage-4 auditor (papers/ar_yukawa_crystal/AUDIT.md section 6).")


def excerpt(path: Path, lines: tuple[int, int], source: str, durable: str, check: str = CITE_CHECK) -> dict:
    t = path.read_text().splitlines()
    return {"kind": "citation", "source": source, "durable_reference": durable, "extraction_sha256": sha(path.read_bytes()),
            "lines": list(lines), "text": "\n".join(t[lines[0] - 1:lines[1]]), "quote_check": check}


CK_SRC = ("Cohn, Kumar, Miller, Radchenko, Viazovska, Universal optimality of the E8 and Leech lattices and interpolation "
          "formulas, Ann. Math. 196 (2022) 983-1082, arXiv:1902.05438 (alphaXiv full text)")
CK_DUR = "arXiv:1902.05438 (doi:10.4007/annals.2022.196.3.3); line numbers refer to the alphaXiv extraction whose sha256 is given"


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def xbase(files: list[Path]) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True,
            "instrument": "rusty-SUNDIALS crates/qf-yukawa-crystal (CVODE BDF, analytic Jacobian), branch physics/ar-yukawa-2026-10-25, "
                          "code cc5a8aed81b3228bd9e9eb69f2c326f926903a34, results 7f2a45c32a9eb9722ca36c334329cb7a5a541951 (not pushed)",
            "files": [file_ref(p) for p in files]}


def main() -> None:
    D1 = W / "results/discovery/D1/compile_Axioms.json"
    CY = H2 / "contribution/compile_yukawa.json"
    CYC = H2 / "contribution/compile_yukawa_controls.json"
    CM = H2 / "contribution/compile_yukawamix.json"
    CMC = H2 / "contribution/compile_yukawamix_controls.json"
    CV = H2 / "contribution/verify/compile_verify_yukawamix.json"
    VER1 = H2 / "verification.md"
    YK, MX = FC / "Yukawa.lean", FC / "YukawaMix.lean"
    UPS = [UPSTREAM / "OAI/Analysis/Triangular/Energy/Universal.lean", UPSTREAM / "OAI/Analysis/Triangular/Energy/Basic.lean",
           UPSTREAM / "OAI/Analysis/Triangular/Energy/Definitions.lean"]
    P = "AutoresearchYukawa."
    M = "AutoresearchYukawaMix."
    summ = json.loads((DATA / "exact_summary.json").read_text())
    lat = summ["lattice"]
    relax = summ["relax"]
    n_relax = len(relax)
    n_below = sum(1 for r in relax if r.get("below_exact_floor"))
    n_zero = sum(1 for r in relax if r.get("exact_gap") == 0.0)
    box1 = [json.loads(l) for l in (DATA / "exact_refs.jsonl").read_text().splitlines()
            if l.strip() and json.loads(l)["kind"] == "box" and json.loads(l)["kappa"] == 1][0]["tri_box_minus_lattice"]
    mp = json.loads((DATA / "mpmath_control.json").read_text())
    max_rust = max(float(r["abs_diff_rust"]) for r in mp["rows"])
    sad = [json.loads(l) for l in (DATA / "exact_saddle.jsonl").read_text().splitlines() if l.strip()]
    oc = json.loads((DATA / "oc20_shard_check.json").read_text())
    claims = [
        rec("YK-A-0001", "A", "lean_axioms",
            "Upstream OAI.AtomicTriangular.universal_energy_minimum (openai/math, AI-generated, Comparator-accepted, not peer reviewed): "
            "for every g with AdmissiblePotential g and every C with LocallyFinite C and DensityOne C, latticeEnergy g <= energy g C "
            "and latticeEnergy g = energy g A. Certifies the statement about upstream's definitions only.",
            [], lean_ev([D1], ["OAI.AtomicTriangular.universal_energy_minimum"], UPS)),
        rec("YK-A-0002", "A", "lean_axioms",
            "TriangularRiesz.riesz_admissible (s > 0: t^(-s/2) is admissible) and TriangularRiesz.latticeEnergy_riesz_lt_top "
            "(s > 2: latticeEnergy (riesz s) < top). Prior published work doi:10.5281/zenodo.23285631.",
            [], lean_ev([D1], ["TriangularRiesz.riesz_admissible", "TriangularRiesz.latticeEnergy_riesz_lt_top"],
                        [W / "formal_cert/Triangular/Riesz.lean", W / "formal_cert/Triangular/RieszFinite.lean"])),
        rec("YK-A-0003", "A", "lean_axioms",
            "TriangularDensity.universal_any_density and triangular_optimal_any_density (D2, doi:10.5281/zenodo.23285631): for rho > 0 "
            "and admissible h, (sqrt rho)^-1 A is locally finite, has DensityRho rho, and minimises energy h among locally finite "
            "DensityRho-rho configurations.",
            ["YK-A-0001", "YK-A-0002"],
            lean_ev([D1], ["TriangularDensity.universal_any_density", "TriangularDensity.triangular_optimal_any_density"],
                    [W / "formal_cert/Triangular/AnyDensity.lean"])),
        rec("YK-A-0004", "A", "lean_axioms",
            "AutoresearchYukawa.admissible_mul (products of admissible potentials are admissible, pointwise Leibniz sign lemma mul_sign), "
            "admissible_congr (admissibility depends only on values on (0, inf)), phi_admissible (kappa > 0: exp(-kappa sqrt t) is admissible).",
            ["YK-A-0002"], dict(lean_ev([CY, CYC], [P + "mul_sign", P + "admissible_mul", P + "admissible_congr", P + "phi_admissible"], [YK]),
                                independent_verification=file_ref(VER1))),
        rec("YK-A-0005", "A", "lean_axioms",
            "AutoresearchYukawa.yukawa_admissible and triangular_yukawa_optimal: for kappa > 0, g kappa t = exp(-kappa sqrt t)/sqrt t is "
            "AdmissiblePotential, hence latticeEnergy (g kappa) <= energy (g kappa) C for every locally finite density-one C.",
            ["YK-A-0001", "YK-A-0004"], dict(lean_ev([CY, CYC], [P + "yukawa_admissible", P + "triangular_yukawa_optimal"], [YK]),
                                             independent_verification=file_ref(VER1))),
        rec("YK-A-0006", "A", "lean_axioms",
            "AutoresearchYukawa.latticeEnergy_yukawa_lt_top: for kappa > 0, latticeEnergy (g kappa) < top (via g <= (2/kappa^2) t^(-3/2)), "
            "so YK-A-0005 is not top <= top.",
            ["YK-A-0002"], dict(lean_ev([CY, CYC], [P + "latticeEnergy_yukawa_lt_top"], [YK]), independent_verification=file_ref(VER1))),
        rec("YK-A-0007", "A", "lean_axioms",
            "Negative control AutoresearchYukawa.c_not_admissible: exp(-kappa sqrt t) cos t is not admissible (negative at t = pi), "
            "so admissibility is not vacuously satisfied. The theorem does not apply to it; this does not show that triangular "
            "optimality fails for it.",
            [], lean_ev([CY], [P + "c_not_admissible"], [YK])),
        rec("YK-A-0008", "A", "lean_axioms",
            "AutoresearchYukawaMix.admissible_add, admissible_smul (c >= 0), admissible_zero, admissible_sum (finite nonnegative "
            "combinations): upstream's AdmissiblePotential is closed under these operations.",
            ["YK-A-0002"], lean_ev([CM, CV], [M + "admissible_add", M + "admissible_smul", M + "admissible_zero", M + "admissible_sum"], [MX])),
        rec("YK-A-0009", "A", "lean_axioms",
            "AutoresearchYukawaMix.g_rescale (pointwise, t > 0: g kappa (t/rho) = sqrt rho * g (kappa/sqrt rho) t), "
            "yukawa_optimal_any_density and latticeEnergy_yukawa_rho_lt_top: at every density rho > 0 the rescaled triangular lattice "
            "minimises the planar Yukawa energy among locally finite density-rho configurations, with finite minimum.",
            ["YK-A-0003", "YK-A-0005", "YK-A-0006"],
            lean_ev([CM, CV], [M + "g_rescale", M + "yukawa_optimal_any_density", M + "latticeEnergy_yukawa_rho_lt_top",
                               M + "latticeEnergy_lt_top_of_le_riesz3"], [MX])),
        rec("YK-A-0010", "A", "lean_axioms",
            "AutoresearchYukawaMix.yukawaMix_admissible, triangular_yukawaMix_optimal, latticeEnergy_yukawaMix_lt_top, "
            "yukawaMix_optimal_any_density, latticeEnergy_yukawaMix_rho_lt_top: every finite mixture sum_i w_i exp(-kappa_i r)/r with "
            "w_i >= 0, kappa_i > 0 is admissible, minimised by the triangular lattice at density one and (rescaled) at every density, "
            "with finite minimum.",
            ["YK-A-0001", "YK-A-0003", "YK-A-0005", "YK-A-0006", "YK-A-0008", "YK-A-0009"],
            lean_ev([CM, CMC, CV], [M + "yukawaMix_admissible", M + "triangular_yukawaMix_optimal", M + "latticeEnergy_yukawaMix_lt_top",
                                    M + "yukawaMix_optimal_any_density", M + "latticeEnergy_yukawaMix_rho_lt_top",
                                    "AutoresearchYukawaMixControls.pos_mix_rho3_finite", "VerifierH2Mix.v_three_length_finite"], [MX])),
        rec("YK-A-0011", "A", "lean_axioms",
            "Negative control AutoresearchYukawaMix.signedMix_not_admissible: g_1 - 2 g_2 is not admissible (value 2e^-1(e^(1/2) - 2) < 0 "
            "at t = 1/4). So the admissibility lemma yukawaMix_admissible needs the sign condition on the weights, and the "
            "optimality theorem does not apply to g_1 - 2 g_2. This does not show that triangular optimality fails for it.",
            [], lean_ev([CM, CV], [M + "signedMix_not_admissible"], [MX])),
        rec("YK-L-0001", "L", "citation",
            "CKMRV Definition 1.3: universal optimality is minimising p-energy for every completely monotonic function of squared "
            "distance; density is bookkeeping (rescaling by rho^(-1/d)).",
            [], excerpt(CKMRV, (418, 443), CK_SRC, CK_DUR)),
        rec("YK-L-0002", "L", "citation",
            "CKMRV Section 1: a lattice has p-energy sum_{x in Lambda minus 0} p(|x|) (no factor 1/2), assuming absolute convergence.",
            [], excerpt(CKMRV, (150, 177), CK_SRC, CK_DUR)),
        rec("YK-L-0004", "L", "citation",
            "CKMRV footnote 2: if p is completely monotonic on (0, inf) then so is r -> p(r^(1/2)); more generally if p and q' are "
            "completely monotonic then so is p o q (each term of the k-th derivative has sign (-1)^k).",
            [], excerpt(CKMRV, (506, 521), CK_SRC, CK_DUR)),
        rec("YK-L-0003", "L", "citation",
            "Upstream manuscript (OpenAI, Universal optimality of the triangular lattice, 2026-09-23), Section 1: the theorem permits "
            "singular potentials and divergent lattice sums, and identifies the minimum value, not all minimizers.",
            [], excerpt(UPAPER, (42, 47), "OpenAI, Universal optimality of the triangular lattice, OpenAI Math Release preprint, 2026-09-23",
                        "github.com/openai/math commit fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb, preprints/.../sections/01-uniform-gaussian-theorem.tex",
                        "A remark of the upstream manuscript, not a theorem, so outside citation_check.py's theorem-only intake (KINDS, "
                        "line 35); quoted from the pinned upstream source file whose sha256 is given above.")),
        rec("YK-L-0005", "L", "citation",
            "CKMRV Section 1 (arXiv:1902.05438 version, p. 8, remark after Theorem 1.4): uniqueness of the minimiser cannot hold among all configurations, "
            "because removing a single particle changes neither the density nor the energy (so a lattice with a vacancy has "
            "the same energy).",
            [], excerpt(CKMRV, (548, 549), CK_SRC, CK_DUR)),
        rec("YK-C-0001", "C", "argument",
            "Human demonstration (paper Section 3): t^(-1/2) and exp(-kappa sqrt t) are completely monotone on (0, inf); Leibniz gives "
            "closure under products; e^x >= x^2/2 gives g <= (2/kappa^2) t^(-3/2) and a convergent lattice sum; sums and nonnegative "
            "multiples preserve the sign pattern; rescaling t -> t/rho preserves it. A prose proof, not machine-checked; it mirrors "
            "the Lean proofs of YK-A-0004..0011 step by step.",
            [], {"kind": "argument", "text": "See main.tex Section 3 (Steps 1-9)."}),
        rec("YK-C-0002", "C", "argument",
            "Physics reading: g kappa (r^2) = exp(-kappa r)/r is the planar Yukawa (3D-screened Coulomb) pair interaction between "
            "particles confined to a plane, with kappa in units of the inverse density-one length; it is not the 2D Debye-Hueckel "
            "Green function K0(kappa r). Upstream latticeEnergy and diskEnergy count ordered pairs (no 1/2), so they are twice the "
            "per-particle energies of the numerics. The theorem is classical (T = 0), concerns the liminf disk-averaged energy, and "
            "fixes the minimum value, not the minimiser. Novelty is formal only: complete monotonicity of the Yukawa potential in r^2 "
            "and the convex-cone/product closure of completely monotone functions are classical.",
            ["YK-A-0005", "YK-L-0002", "YK-L-0003", "YK-L-0005"], {"kind": "argument", "text": "Gloss of Tier A statements; Tier A attaches to the formal statements only."}),
        rec("YK-C-0003", "C", "argument",
            "Hugging Face search (2026-10-25, public, unauthenticated) for dusty plasma, complex plasma, colloid, colloidal, yukawa and "
            "wigner crystal found no particle-position dataset of a dusty plasma or colloid (absence by search, not proof); OC20 "
            "(colabfit/OC20_IS2RES_val_id) supplies disordered initial conditions, not physics.",
            [], {"kind": "argument", "files": [file_ref(HF / "hub_search.json"), file_ref(HF / "inspect.json")]}),
        rec("YK-X-0001", "X", "numeric",
            f"Exact (untruncated) lattice energies per particle, (1/2) sum, density one: kappa=1 tri {lat['1']['tri_exact']} square "
            f"{lat['1']['square_exact']}; kappa=2 tri {lat['2']['tri_exact']} square {lat['2']['square_exact']}. Exact minus published "
            f"shifted-force (r_c = 8): {lat['1']['tri_exact_minus_sf']} (kappa=1 tri), {lat['2']['tri_exact_minus_sf']} (kappa=2 tri). "
            f"Square-minus-triangular gap changes by {lat['1']['gap_change']} (kappa=1) and {lat['2']['gap_change']} (kappa=2). "
            "Consistency evidence only.",
            ["YK-C-0002"], dict(xbase([DATA / "exact_refs.jsonl", DATA / "exact_summary.json"]), summary=lat)),
        rec("YK-X-0002", "X", "numeric",
            f"Positive controls: independent 40-digit mpmath direct sum and Ewald splitting agree with the Rust f64 values to at most "
            f"{max_rust:.2e} (threshold 1e-9); Rust direct vs Ewald and image-summed box vs lattice sum agree to the 1e-15/1e-16 level.",
            [], dict(xbase([DATA / "mpmath_control.json", DATA / "exact_refs.jsonl", RUSTY / "scripts/mpmath_lattice_control.py"]),
                     rows=mp["rows"])),
        rec("YK-X-0003", "X", "numeric",
            f"Negative controls: published shifted-force lattice energies fail the 1e-9 test against the exact ones by the erratum "
            f"amount; the square lattice in a 17x17 box under the exact potential has {sad[0]['hess_negative']} (kappa={sad[0]['kappa']}) "
            f"and {sad[1]['hess_negative']} (kappa={sad[1]['kappa']}) negative Hessian modes and relaxes to an energy above e_tri.",
            [], dict(xbase([DATA / "mpmath_control.json", DATA / "exact_saddle.jsonl"]), saddle=sad)),
        rec("YK-X-0004", "X", "numeric",
            f"Relaxed comparison: {n_relax} relaxed stages from 21 published seeds re-relaxed under the exact potential with CVODE; "
            f"{n_below} fall below the exact triangular energy beyond f64 resolution (below_exact_floor is exact_gap < 0 with "
            f"zero tolerance; {n_zero} stage(s) sit at exact_gap = 0.0, the perfect lattice, within f64 noise: the perfect "
            f"lattice in the kappa=1 box differs from the lattice sum by {box1:.1e}); no negative Hessian modes; gaps change by at most 5.3e-7 (kappa=1) and "
            "about 1e-10 (kappa=2). A subset (11 of 50 stages at kappa=1, 13 of 100 at kappa=2); annealing not re-run.",
            ["YK-C-0002"], dict(xbase([DATA / "exact_summary.json"] + sorted(DATA.glob("exact_relax_*.jsonl"))), relax=relax)),
        rec("YK-X-0005", "X", "numeric",
            f"OC20 shard provenance: local co_10.parquet sha256 {oc['local_sha256']} equals the Hub LFS sha256 at revision "
            f"{oc['current_revision']} of {oc['repo']} (license {oc['license']}); original download date not recorded; the local file mtime "
            f"{datetime.fromtimestamp(Path(oc['local_path']).stat().st_mtime, tz=timezone.utc):%Y-%m-%d %H:%M} UTC is a latest possible "
            "download date. The dataset card at that revision (data/oc20_card.json) gives the dataset DOI 10.60732/b4005525 and "
            "the journal DOI 10.1021/acscatal.0c04525.",
            [], dict(xbase([DATA / "oc20_shard_check.json", DATA / "oc20_card.json"]), check=oc)),
        rec("YK-X-0006", "X", "numeric",
            "Sampled sign checks (mpmath, 40 digits): (-1)^n g_1^(n) > 0 at orders 0..6 on 159 points of t in [0.05, 4] "
            "(figures/fig_signs.json); (-1)^n g^(n) >= 0 at orders 0..8 on t = k/20, k = 1..80, for g_1 + 0.5 g_3 and its rho = 3 "
            "rescaling (contribution/numeric_gate_mix.json); g_1 - 2 g_2 violates the pattern (value -0.2585 at t = 1/4). "
            "Exploration only.",
            [], dict(xbase([H2 / "contribution/numeric_gate_mix.json", H2 / "contribution/numeric_gate_mix.py",
                            HERE.parent / "figures/fig_signs.json", HERE.parent / "make_figures.py"]))),
    ]
    ledger = {"schema_version": 1, "claims": claims}
    (HERE / "ledger.json").write_text(json.dumps(ledger, indent=1, ensure_ascii=False))
    print(f"claims {len(claims)}; evidence blobs {len(list(EV.glob('*.json')))}")


if __name__ == "__main__":
    sys.exit(main())
