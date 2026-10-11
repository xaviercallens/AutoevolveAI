"""Build the Elenchus claim ledger for the planar universal-optimality publication.

Every claim gets a content-addressed evidence blob (evidence/<sha256>.json) holding the artefact it rests on:
compiled axiom output and source hashes (Tier A), primary-source excerpts with line numbers (Tier L), the
argument text (Tier C), result files of the CVODE study (Tier X, claim_licence false). Gate:
python3 <elenchus>/tools/ledger.py ledger.json --evidence-dir evidence
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W = HERE.parents[2]  # AutoevolveAI worktree
EV = HERE / "evidence"
CKMRV = Path("/home/callensxavier_gmail_com/.claude/projects/-home-callensxavier-gmail-com-AutoevolveAI--claude-worktrees-openai-math-discovery/6ecda88c-9d6f-441a-9328-d4a192612987/tool-results/mcp-claude_ai_alphaXiv-get_paper_content-1791653555097.txt")
UPSTREAM = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/openai_math_pinned/lean/ComparatorChallenges/TriangularEnergy.lean")
YUK = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-yukawa/crates/qf-yukawa-crystal")


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


def axioms_lines(names: list[str]) -> list[str]:
    out = json.loads((W / "results/discovery/D1/compile_Axioms.json").read_text())
    text = json.dumps(out)
    text = text.encode().decode("unicode_escape")
    lines = [l.strip() for l in text.replace("\n ", " ").split("\n")]
    return [l for l in lines if any(f"'{n}'" in l or f"{n}'" in l for n in names)]


def excerpt(lines: tuple[int, int]) -> dict:
    t = CKMRV.read_text().splitlines()
    return {"source": "Cohn, Kumar, Miller, Radchenko, Viazovska, Universal optimality of the E8 and Leech lattices and interpolation formulas, Ann. Math. 196 (2022) 983-1082, arXiv:1902.05438 (alphaXiv full text)",
            "file": file_ref(CKMRV), "lines": list(lines), "text": "\n".join(t[lines[0] - 1:lines[1]])}


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def lean_ev(names: list[str], files: list[str]) -> dict:
    return {"kind": "lean_axioms", "toolchain": "Lean 4.34.1, Mathlib d13f23b7, openai/math adc7f124 (files unchanged at fd4aeeb2)",
            "axiom_output": axioms_lines(names), "allowlist": ["propext", "Classical.choice", "Quot.sound"],
            "sources": [file_ref(W / f) for f in files], "upstream_challenge": file_ref(UPSTREAM),
            "statement_adequacy": "audited by AI agents only (results/discovery/statement_fidelity.md, D1/D2/D3 verification.md); no human audit"}


def main() -> None:
    T = "formal_cert/Triangular/"
    claims = [
        rec("UO-A-0001", "A", "lean_axioms",
            "OAI.AtomicTriangular.universal_energy_minimum (openai/math): for every g with AdmissiblePotential g and every C with LocallyFinite C and DensityOne C, latticeEnergy g <= energy g C and latticeEnergy g = energy g A. Kernel footprint within the allowlist. Certifies the statement about THOSE upstream definitions; that they express the Cohn-Kumar universal-optimality question is a statement-adequacy matter (AI-audited only).",
            [], lean_ev(["OAI.AtomicTriangular.universal_energy_minimum"], [])),
        rec("UO-A-0002", "A", "lean_axioms",
            "TriangularRiesz.riesz_admissible and triangular_riesz_optimal: for s > 0, AdmissiblePotential (fun t => t^(-(s/2))), hence latticeEnergy (riesz s) <= energy (riesz s) C for every locally finite density-one C.",
            ["UO-A-0001"], lean_ev(["TriangularRiesz.riesz_admissible", "TriangularRiesz.triangular_riesz_optimal"], [T + "Riesz.lean"])),
        rec("UO-A-0003", "A", "lean_axioms",
            "TriangularRiesz.latticeEnergy_riesz_lt_top: for s > 2, latticeEnergy (riesz s) < top.",
            [], lean_ev(["TriangularRiesz.latticeEnergy_riesz_lt_top"], [T + "RieszFinite.lean"])),
        rec("UO-A-0004", "A", "lean_axioms",
            "TriangularDensity.triangular_optimal_any_density (with scaled_density, attained) and unscaled_false: for rho > 0 and admissible h, (sqrt rho)^-1 A is locally finite with DensityRho rho and its energy is <= that of every locally finite DensityRho-rho configuration; the unrescaled claim is false at rho = 1/4 for riesz 4.",
            ["UO-A-0001", "UO-A-0003"], lean_ev(["TriangularDensity.triangular_optimal_any_density", "TriangularDensity.unscaled_false"], [T + "AnyDensity.lean"])),
        rec("UO-A-0005", "A", "lean_axioms",
            "TriangularUniversalOptimality.triangular_universally_optimal: for rho > 0, UniversallyOptimal rho ((sqrt rho)^-1 A), where UniversallyOptimal is defined in UniversalOptimality.lean with upstream's lower (liminf) energy.",
            ["UO-A-0004"], lean_ev(["TriangularUniversalOptimality.triangular_universally_optimal"], [T + "UniversalOptimality.lean"])),
        rec("UO-A-0006", "A", "lean_axioms",
            "TriangularUniversalOptimality.universal_optimum_not_unique: there is C with UniversallyOptimal 1 C and no isometry f of the plane with f '' A = C (witness A minus the origin; vacancy_energy: its energy equals latticeEnergy g for every admissible g).",
            ["UO-A-0001"], lean_ev(["TriangularUniversalOptimality.universal_optimum_not_unique", "TriangularUniversalOptimality.vacancy_energy"], [T + "UniversalOptimality.lean"])),
        rec("UO-L-0001", "L", "citation",
            "CKMRV Definition 1.3: a configuration of density rho is universally optimal if it minimises p-energy for every completely monotonic function of squared distance; density is bookkeeping (rescaling).",
            [], excerpt((418, 443))),
        rec("UO-L-0002", "L", "citation",
            "CKMRV Theorem 1.4 and the remark after it: E8 and Leech are universally optimal and unique among periodic configurations; uniqueness cannot hold among all configurations because removing a single particle changes neither density nor energy.",
            [], excerpt((524, 559))),
        rec("UO-L-0003", "L", "citation",
            "History per CKMRV: Ventevogel-Nijboer proved universal optimality of Z in dimension 1 (Cohn-Kumar gave another proof); before CKMRV no universal optimum in dimension > 1 was proved; universal optimality of A2 in full generality is called an important open problem.",
            [], excerpt((362, 484))),
        rec("UO-L-0004", "L", "citation",
            "CKMRV footnote 2: if p and q' are completely monotonic then p o q is completely monotonic (Faa di Bruno sign argument).",
            [], excerpt((506, 521))),
        rec("UO-C-0001", "C", "argument",
            "Yukawa V(r) = exp(-kappa r)/r, as g(t) = exp(-kappa sqrt t)/sqrt t, is completely monotone in t: t^(-1/2) is completely monotone; exp(-kappa sqrt t) is p o q with p(u) = exp(-kappa u) completely monotone and q = sqrt with q' = t^(-1/2)/2 completely monotone (UO-L-0004); products of completely monotone functions are completely monotone (Leibniz rule). Not kernel-checked.",
            ["UO-L-0004"], {"kind": "argument", "text": "See statement; the product step uses (fg)^(n) = sum binom(n,k) f^(k) g^(n-k), every term of sign (-1)^n."}),
        rec("UO-C-0002", "C", "argument",
            "Interpretation of UO-A-0006: in the lower-energy formulation over all locally finite configurations, 'mutually repelling particles always arrange into a triangular lattice' is false as a uniqueness statement; only the minimum value is pinned down there. Uniqueness among periodic configurations (CKMRV's form) is open in dimension 2 and not addressed. UniversallyOptimal is strictly weaker than CKMRV Def 1.3 (no requirement that the energy exist as a limit).",
            ["UO-A-0006", "UO-L-0001", "UO-L-0002"], {"kind": "argument", "text": "Gloss of a Tier A statement; Tier A attaches to the formal statement, never to its gloss."}),
    ]
    summary = YUK / "results/summary.json"
    if summary.exists():
        s = json.loads(summary.read_text())
        files = [file_ref(p) for p in sorted((YUK / "results").glob("*.jsonl"))] + [file_ref(YUK / "results/preregistration.json"), file_ref(summary)]
        base = {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "instrument": "rusty-SUNDIALS CVODE (BDF, analytic Jacobian) via crates/qf-yukawa-crystal", "files": files}
        k2 = s.get("main_kappa2", {})
        claims.append(rec("UO-X-0001", "X", "numeric",
                          f"CVODE N-body study, Yukawa kappa = 2, N = 288 periodic: P1 (no relaxed configuration below e_tri by more than 1e-9 relative) pass = {k2.get('P1_no_undercut', {}).get('pass')}; P2 per-family perfect-lattice counts after annealing = {k2.get('P2_annealed_reaches_lattice', {}).get('per_family_perfect')}; P3 defected T=0 quenches = {k2.get('P3_quench_glassy', {}).get('defected_over_runs')}. Consistency evidence only; claim_licence false.",
                          ["UO-C-0001"], dict(base, summary=k2)))
        k1 = s.get("main_kappa1", {})
        if k1:
            claims.append(rec("UO-X-0002", "X", "numeric",
                              f"Truncation cross-check kappa = 1 (truncation ~4e-5): P1 pass = {k1.get('P1_no_undercut', {}).get('pass')}; P2 = {k1.get('P2_annealed_reaches_lattice', {}).get('per_family_perfect')}. Consistency evidence only.",
                              ["UO-C-0001"], dict(base, summary=k1)))
        claims.append(rec("UO-X-0003", "X", "numeric",
                          "Controls: perfect and noisy triangular lattices return to the lattice (gap ~1e-14, Hessian two zero modes, smallest other eigenvalue ~0.024); square lattice is a saddle (negative Hessian eigenvalues) and relaxes below its energy; references e_square > e_tri.",
                          [], dict(base, controls=s.get("controls"), references=s.get("references"))))
        if "disk" in s:
            claims.append(rec("UO-X-0004", "X", "numeric",
                              f"Open (harmonic bowl) vs closed (soft wall) disk, N = 300, kappa = 2: {s['disk']}. Finite-size edge-effect description; not a test of the Lean open/closed-disk counting convention.",
                              [], dict(base, disk=s["disk"])))
    ledger = {"schema_version": 1, "claims": claims}
    (HERE / "ledger.json").write_text(json.dumps(ledger, indent=1, ensure_ascii=False))
    print(f"claims {len(claims)}; evidence blobs {len(list(EV.glob('*.json')))}")


if __name__ == "__main__":
    sys.exit(main())
