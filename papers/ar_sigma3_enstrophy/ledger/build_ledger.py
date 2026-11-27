"""Build the Elenchus claim ledger for the sigma = 3 enstrophy preprint (papers/ar_sigma3_enstrophy).

Modelled on results/discovery/ledger/build_ledger.py and papers/ar_keldysh_tmd/ledger/build_ledger.py. Every claim
gets a content-addressed evidence blob (evidence/<sha256>.json): verbatim #print axioms lines plus source hashes
(Tier A), verbatim or linearly transcribed primary-source excerpts (Tier L, sources/excerpts.json and the local
dataset card), the argument text (Tier C), result files with claim_licence false (Tier X).
Gate: python3 <elenchus>/tools/ledger.py ledger.json --evidence-dir evidence
Usage: python -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
W = PAPER.parents[1]
EV = HERE / "evidence"
H7 = W / "results/autoresearch/2026-10-25/H7"
C7 = H7 / "contribution"
DATA = PAPER / "data"
QF = Path("/mnt/disks/disk-socrateai-local-1/leanmaster/SocrateAI-Scientific-QuantumFluids")
QFL = Path("/mnt/disks/disk-socrateai-local-1/leanmaster/qf-lake/build/lib/lean")
RUSTY = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h7/crates/qf-shell-cascade")
HF = Path("/home/callensxavier_gmail_com/hf-data/sigma3_enstrophy")
EXC = json.loads((HERE / "sources/excerpts.json").read_text())
TOOLCHAIN = ("Lean v4.34.0-rc2 (elan toolchain leanprover--lean4---v4.34.0-rc2), QuantumFluids qf-lake Mathlib build "
             "(/mnt/disks/disk-socrateai-local-1/leanmaster/qf-lake), owner repo SocrateAI-Scientific-QuantumFluids "
             "commit 10f74daf1b39d2ac51a785452329fff0003cfc83; run directly with LEAN_PATH (run_lean.py)")
RUSTY_SHAS = {"code": "99f5df89e8d8380ea1a9f065ae87308e779224fc", "results": "e869e5fc4e38df24bc93ee2c22e19f2e68920041",
              "probes": "dfa9a0880450a7601e1ecdcb735b5897c6319ffd", "base_origin_main": "47ef5044c10b04c64d8c86f483f1aa47c400ab28"}
NS = "QuantumFluids.AutoresearchEnstrophy."
ALLOW = ["propext", "Classical.choice", "Quot.sound"]


def macros() -> dict[str, str]:
    """Read ../gen_numbers.tex (generated) so revised ledger numbers are not typed by hand; 'a\\times10^{b}' -> 'aeb'."""
    out: dict[str, str] = {}
    for line in (PAPER / "gen_numbers.tex").read_text().splitlines():
        m = re.match(r"\\newcommand\{\\(\w+)\}\{(.*)\}$", line)
        if m:
            out[m.group(1)] = re.sub(r"\\times10\^\{(-?\d+)\}", r"e\1", m.group(2))
    return out


M = macros()


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
    out = json.loads(compile_json.read_text())["stdout"].replace("\n ", " ")
    return [l.strip() for l in out.split("\n") if any(f"'{n}'" in l for n in names)]


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


OWNER_SRC = [QF / "lean_src/QuantumFluidsShell.lean", QF / "lean_src/ShellHamiltonian.lean",
             QFL / "QuantumFluidsShell.olean", QFL / "ShellHamiltonian.olean"]


def lean_ev(names: list[str], compile_json: Path, src: Path, ns: str = NS) -> dict:
    full = [ns + n for n in names]
    lines = axiom_lines(compile_json, full)
    if len(lines) != len(full):
        raise SystemExit(f"axiom lines missing for {names}: {lines}")
    for l in lines:
        if not l.endswith("[propext, Classical.choice, Quot.sound]"):
            raise SystemExit(f"axiom footprint outside allowlist: {l}")
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": lines, "allowlist": ALLOW,
            "compile_transcript": file_ref(compile_json), "sources": [file_ref(src)] + [file_ref(p) for p in OWNER_SRC],
            "producer": "H7 stage-1 agent (Claude); paper-stage recompile by another agent instance",
            "independent_audit": {"by": "a separate AI-agent instance (Claude), not a human", "report": file_ref(PAPER / "AUDIT.md"),
                                  "summary": "recompiled claimed and prior files (rc 0, allowlist footprint); own planted sorry and planted axiom both caught by #print axioms in exactly the dependent theorems; statement fidelity checked against #print of owner definitions; verdict ACCEPT_WITH_CORRECTIONS"},
            "human_verifier": None,
            "statement_adequacy": "not audited by a human; the model definitions are the QuantumFluids owner's (shellBc) plus a dispersive term"}


def cite(keys: list[str]) -> dict:
    return {"kind": "citation", "excerpts": {k: EXC[k] for k in keys}, "excerpt_file": file_ref(HERE / "sources/excerpts.json")}


def card(lines: tuple[int, int]) -> dict:
    p = HF / "README.md"
    t = p.read_text().splitlines()
    return {"source": "HuggingFace dataset card polymathic-ai/turbulent_radiative_layer_2D at revision 2ee7756575ff6f90981d0308cbcb6a2ab5995bdc",
            "file": file_ref(p), "lines": list(lines), "text": "\n".join(t[lines[0] - 1:lines[1]])}


def num(files: list[Path], **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True,
            "instrument": "rusty-SUNDIALS CVODE (BDF, analytic Jacobian, one-step mode) via crates/qf-shell-cascade sigma.rs / sigma3_study (branch physics/ar-sigma3-shell-2026-10-25, not pushed)",
            "rusty_commits": RUSTY_SHAS, "files": [file_ref(p) for p in files], **kw}


def main() -> int:
    flow = C7 / "Autoresearch_EnstrophyFlow.lean"
    prior = H7 / "Autoresearch_Enstrophy.lean"
    final, recheck = C7 / "compile_flow_final.json", C7 / "recheck_prior.json"
    claims = [
        rec("SE-A-0001", "A", "lean_axioms",
            "QuantumFluids owner theorems used here (SocrateAI-Scientific-QuantumFluids lean_src, compiled qf-lake build): dispersive_norm_le (if Hval = sum_{n<N+2} q_n |v_n|^2 + sum_{n<N+1} c_n Im(conj(v_n)^2 v_{n+1}) and |c_n| <= 1 then sum q_n |v_n|^2 <= Hval + sqrt(S) S), cubic_bound, sum_dT, hamiltonian_rate_zero, weights_ok, shellBc_energy_conservation. Axiom footprint re-printed at paper stage.",
            [], lean_ev(["dispersive_norm_le", "cubic_bound", "sum_dT", "hamiltonian_rate_zero", "weights_ok", "shellBc_energy_conservation"],
                        C7 / "compile_owner_axioms.json", C7 / "OwnerAxioms.lean", ns="QuantumFluids.ShellComplex.")),
        rec("SE-A-0002", "A", "lean_axioms",
            "Pointwise sigma = 3 bound: for every N, every v : N -> C and every real D, 2 D enstrophy N v <= ham3 D N v + (2 energy N v)^(3/2) (enstrophy_bound); for D > 0, enstrophy <= (ham3 + (2E)^(3/2))/(2D) (enstrophy_le); dropping the (2E)^(3/2) term is false at N = 0, D = 1, v = (1, -i, 0, ...) where 2D Omega = 5 > H3 = 4 (drop_cubic_term_fails).",
            ["SE-A-0001"], lean_ev(["weight_eq_one", "disp_weight", "sqrt_mul_self_eq_rpow", "enstrophy_bound", "enstrophy_le", "drop_cubic_term_fails"], recheck, prior)),
        rec("SE-A-0003", "A", "lean_axioms",
            "Rate identities along F = shellBc - i omega v (any real k, omega): the dispersion does no work (re_conj_mul_F); dT_F; quad_tel; rate_zero (dHam q g N v (F k omega v) = 0 under g_{n+1} 2k_n = g_n k_{n+1}, 2 q_{n+1} k_n + g_n (2 omega_n - omega_{n+1}) = 2 q_n k_n and v_{N+2} = 0); ham_rate_zero for q_n = 2^-n omega_n, g_n = 2^-n k_n; energy_rate_zero.",
            ["SE-A-0001"], lean_ev(["re_conj_mul_F", "dT_F", "quad_tel", "rate_zero", "ham_rate_zero", "energy_rate_zero"], final, flow)),
        rec("SE-A-0004", "A", "lean_axioms",
            "Chain rule and constancy: hasDerivAt_hamG; const_on_Icc; ham_conserved and energy_conserved: if every shell n < N+2 of u has derivative F k omega (u t) n at every t in [0,T] (two-sided HasDerivAt) and u t (N+2) = 0 on [0,T], then hamG with the dyadic weights and energy are constant on [0,T].",
            ["SE-A-0003"], lean_ev(["hasDerivAt_hamG", "const_on_Icc", "ham_conserved", "energy_conserved"], final, flow)),
        rec("SE-A-0005", "A", "lean_axioms",
            "Along such a solution of the sigma = 3 flow (k = kk, omega_m = D kk m ^ 3), for every t in [0,T]: 2 D enstrophy N (u t) <= ham3 D N (u 0) + (2 energy N (u 0))^(3/2) (enstrophy_bound_along_flow), and for D > 0 the divided form (enstrophy_le_along_flow). The zero trajectory satisfies the hypotheses (zero_trajectory_is_solution; consistency only). Existence of solutions is NOT proved; N is fixed.",
            ["SE-A-0002", "SE-A-0004"], lean_ev(["enstrophy_bound_along_flow", "enstrophy_le_along_flow", "zero_trajectory_is_solution", "enstrophy_bound"], final, flow)),
        rec("SE-A-0006", "A", "lean_axioms",
            "Sensitivity controls computed directly (N = 0, D = 1): rate at (1,1,0,...) with the dyadic weights is 0 (rate_v11_correct); with the 2^-n factor dropped on the dispersive weight it is 8 (rate_v11_wrong_weight); without truncation (v_2 = 1) it is nonzero (rate_v111_no_truncation).",
            [], lean_ev(["rate_v11_correct", "rate_v11_wrong_weight", "rate_v111_no_truncation"], final, flow)),
        rec("SE-A-0007", "A", "lean_axioms",
            "Planted controls in the separate file Autoresearch_EnstrophyFlowControls.lean (defines its own Fc, imports ShellHamiltonian, not the claimed module) are caught by #print axioms: ctl_sorry depends on sorryAx, ctl_axiom on the planted axiom ctl_flow_cheat; the file compiles with rc 0, so exit status is not the gate.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(C7 / "compile_flow_controls.json", ["QuantumFluids.AutoresearchEnstrophyFlowControls.ctl_sorry", "QuantumFluids.AutoresearchEnstrophyFlowControls.ctl_axiom"]),
                 "paper_stage_rerun_axiom_output": axiom_lines(C7 / "recompile_paper_stage_controls.json", ["QuantumFluids.AutoresearchEnstrophyFlowControls.ctl_sorry", "QuantumFluids.AutoresearchEnstrophyFlowControls.ctl_axiom"]),
                 "allowlist": ALLOW, "expected": "both controls OUTSIDE the allowlist",
                 "sources": [file_ref(C7 / "Autoresearch_EnstrophyFlowControls.lean"), file_ref(C7 / "compile_flow_controls.json"), file_ref(C7 / "recompile_paper_stage_controls.json")],
                 "statement_adequacy": "control rows; not audited by a human"}),
        rec("SE-L-0001", "L", "citation",
            "Waleffe (arXiv:math/0410380) eq. (12): the dyadic inviscid Burgers chain da_j/dt = 2^j (a_{j-1}^2 - 2 a_j a_{j+1}), da_{j0}/dt = -2^{j0+1} a_{j0} a_{j0+1}, to which the Katz-Pavlovic dyadic Euler model reduces; eqs. (19)-(20): the real chain with lambda > 1 conserves E = sum a_j^2; Theorem 1: with non-negative data and enough energy at high j, the H^alpha norm of the infinite chain blows up in finite time for every alpha > 0.",
            [], {**cite(["waleffe_abstract", "waleffe_eq12", "waleffe_eq19_20", "waleffe_thm1"]),
                 "citation_check_thm1": {"tool": "Elenchus tools/citation_check.py CLAIM SOURCE", "verdict": "ACCEPTED", "exit": 0,
                                         "source_text": file_ref(HERE / "sources/waleffe_thm1_source.txt"),
                                         "claim": file_ref(HERE / "sources/claim_thm1.json"),
                                         "output": file_ref(HERE / "sources/citation_check_output.txt"),
                                         "provenance": "alphaXiv page-7 extraction of arXiv:math/0410380v2 made by the H7 auditor, copied unchanged"}}),
        rec("SE-L-0002", "L", "citation",
            "Dataset card of polymathic-ai/turbulent_radiative_layer_2D (revision 2ee7756575ff6f90981d0308cbcb6a2ab5995bdc): license cc-by-4.0; part of The Well; compressible Euler with cooling -E/t_cool, gamma = 5/3, generated with Athena++; 101 timesteps of 384x128; periodic in x, zero-gradient in y; t_cool in {0.03, ..., 3.16}; associated paper Fielding, Ostriker, Bryan, Jermyn, ApJL 894 L24 (2020), doi:10.3847/2041-8213/ab8d2c.",
            [], {"kind": "citation", "card_license": card((4, 4)), "card_physics": card((37, 58)), "card_layout": card((71, 93)),
                 "card_citation": card((109, 121)), "the_well": EXC["the_well_listing"],
                 "download_record": file_ref(HF / "download_record.json")}),
        rec("SE-C-0001", "C", "argument",
            "Step-by-step human proof (paper Section 3, Steps 1-6) of energy conservation, conservation of H_3 for every dispersion law with the dyadic weights, the pointwise bound 2 D Omega <= H_3 + S^(3/2) and its propagation along solutions. Not machine-checked as a text; each step is paired with the Lean statement that is checked (SE-A-0002..0005).",
            ["SE-A-0002", "SE-A-0003", "SE-A-0004", "SE-A-0005"], {"kind": "argument", "paper_section": "Human mathematical demonstration", "text_file": file_ref(PAPER / "main.tex")}),
        rec("SE-C-0002", "C", "argument",
            "On real data with D = 0 the owner's truncated model is Waleffe's chain (12) with j0 = 0 after the time change v(t) = a(t/2): interior 2^{n-1}(v_{n-1}^2 - 2 v_n v_{n+1}) = (1/2) 2^n(...), boundary -v_0 v_1 = (1/2)(-2 v_0 v_1). Waleffe's blow-up concerns the infinite, non-dispersive real chain; nothing here concerns N -> infinity.",
            ["SE-L-0001"], {"kind": "argument", "text": "Compare shellBc (listing owner_shell.lean) with Waleffe (12); multiply by 1/2 and rescale time."}),
        rec("SE-C-0003", "C", "argument",
            "Since H_3 = 2 D Omega + C with |C| <= S^(3/2) (cubic_bound), the Lean bound gives Omega(t) <= Omega(0) + S(0)^(3/2)/D for D > 0: uniform in N and t only for families of initial data with N-uniform Omega(0) and S(0); the constant degenerates as D -> 0.",
            ["SE-A-0001", "SE-A-0005"], {"kind": "argument", "text": "H_3(0) <= 2 D Omega(0) + S(0)^(3/2); insert in 2 D Omega(t) <= H_3(0) + S(0)^(3/2)."}),
        rec("SE-C-0004", "C", "argument",
            "sigma = 2 (omega_n = D k_n^2): the same weights give q_n = D k_n, so H_2 controls sum k_n |v_n|^2, not Omega. For all mass in the top shell n (S = 1), 2 D Omega / (H_2 + S^(3/2)) = D 4^n/(D 2^n + 1), which grows like 2^n once D 2^n >> 1.",
            ["SE-A-0003"], {"kind": "argument", "text": "On a one-shell state the cubic part vanishes; 2 D Omega = D 4^n, H_2 = 2^-n D 4^n = D 2^n."}),
        rec("SE-X-0001", "X", "numeric",
            "CVODE conservation controls (sigma = 3, decaying data, T = 2, D = 0.05): positive control drift of S and H_3 shrinks by more than 100x from rtol 1e-6 to 1e-10 (n_max = 4 and 6); negative control (k_1 outgoing coupling x 1.01) drift does not converge with rtol: over S and H_3, n_max = 4 and 6 and rtol 1e-6..1e-10 it lies between " + M["NegAllMin"] + " and " + M["NegAllMax"] + " (S and n_max = 4 H_3 constant in rtol at the printed precision; n_max = 6 H_3 " + M["NegHsixMax"] + " -> " + M["NegHsixMin"] + "). Consistency evidence only.",
            ["SE-A-0004"], num([DATA / "summary.json", DATA / "sigma3_study.json"])),
        rec("SE-X-0002", "X", "numeric",
            "sigma = 3 sweep n_max = 2..7 (Lean N = 1..6), 2 phase seeds: sup over internal steps of 2 D Omega(t)/(H_3(0) + S(0)^(3/2)) <= 0.360 in all 12 runs, above the t = 0 value in 12/12; max drifts dS 2.1e-9, dH_3 4.0e-6.",
            ["SE-A-0005"], num([DATA / "summary.json", DATA / "sigma3_study.json", DATA / "fig_truncation_sweep.pdf"])),
        rec("SE-X-0003", "X", "numeric",
            "sigma = 2 control on top-shell data: ratio 0.667 ... 1004.4 for n_max = 2..10, local log2 steps 1.18, 1.10, 1.05, 1.03 (n_max 6 -> 10), equal to the t = 0 value to within a relative " + M["CtwoGapRel"] + "; sigma = 3 on the same data <= 0.995, sup above the t = 0 value by at most " + M["CthreeGapAbs"] + " (absolute). H_2 conserved on cascading sigma = 2 data (max rel dH_2 8.2e-10, 9.9e-11 at n_max = 4, 6) while the sigma = 2 analogue ratio reaches 1.57 and 2.43.",
            ["SE-C-0004"], num([DATA / "summary.json", DATA / "sigma2_probes.jsonl", DATA / "fig_truncation_sweep.pdf"])),
        rec("SE-X-0004", "X", "numeric",
            "The Well illustration: dyadic x-spectrum of 4 developed snapshots of turbulent_radiative_layer_tcool_0.32.hdf5 (Parseval rel. err <= 4.0e-16; sin(8x) control 100% in shell 3; white-noise log2 slope 1.01 vs data -2.13, -1.56, -1.79, -1.81); 24 data-initialised sigma = 3 runs (random phases, 2 seeds, n_max = 5, 6, 7): bound holds with max ratio 0.631, sup above t = 0 in 24/24, dS <= 2.4e-8, dH_3 <= 1.2e-6. Illustration only; the shell model is not a model of that flow.",
            ["SE-L-0002", "SE-A-0005"], num([DATA / "well_spectrum.json", DATA / "well_amps.txt", DATA / "summary.json", DATA / "download_record.json", RUSTY / "results/sigma3/scripts/well_spectrum.py", DATA / "fig_well_data.pdf"],
                                            interpreter_note="well_spectrum.py ran under /mnt/disks/disk-socrateai-local-1/venv-pta/bin/python -I (h5py); the AutoevolveAI .venv lacks h5py")),
        rec("SE-X-0005", "X", "numeric",
            "Paper-stage rerun by another AI agent instance (not an independent human check): Autoresearch_EnstrophyFlow.lean recompiled rc 0 in 18.5 s with #print axioms output identical to compile_flow_final.json (same sha256 4cd74689...8dd4); controls file rc 0 with identical output (sorryAx and ctl_flow_cheat caught). Afterwards a separate AI-agent instance ran an independent audit (AUDIT.md; not a human audit): recompile rc 0, own planted sorry/axiom caught, numerics and cargo test rerun.",
            [], num([C7 / "recompile_paper_stage_flow.json", C7 / "recompile_paper_stage_controls.json", C7 / "paper_stage_recompile.py", PAPER / "AUDIT.md"])),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    print(f"claims {len(claims)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
