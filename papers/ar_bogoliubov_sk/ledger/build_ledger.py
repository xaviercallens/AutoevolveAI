"""Build the Elenchus claim ledger for the H8 preprint (papers/ar_bogoliubov_sk).

Modelled on results/discovery/ledger/build_ledger.py. Every claim gets a content-addressed evidence blob
(evidence/<sha256>.json): verbatim #print axioms lines plus source and transcript hashes (Tier A), verbatim
primary-source excerpts with line numbers from the alphaXiv text extractions copied into sources/ (Tier L), the argument
text (Tier C), result files with claim_licence false (Tier X). Tier A rows keep audit null: no human has audited
statement adequacy.
Run: .venv/bin/python -I ledger/build_ledger.py   then
     python3 -I <elenchus>/tools/ledger.py ledger/ledger.json --evidence-dir ledger/evidence
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
W = PAPER.parents[1]
EV = HERE / "evidence"
SRC = HERE / "sources"
DATA = PAPER / "data"
C8 = W / "results/autoresearch/2026-10-25/H8/contribution"
H8 = C8.parent
LEAN = C8 / "Autoresearch_SkBoundShape.lean"
CTL = C8 / "Autoresearch_SkBoundShapeControls.lean"
OWNER = Path("/mnt/disks/disk-socrateai-local-1/leanmaster/SocrateAI-Scientific-QuantumFluids/lean_src/DualLength.lean")
RUSTY = Path("/home/callensxavier_gmail_com/rusty-SUNDIALS-wt-ar-h8/crates/qf-gpe2d")
RUSTY_SHA = "ae918316a82f7ac7102d53f646eb20c5a2c838a5"
TOOLRES = Path("/home/callensxavier_gmail_com/.claude/projects/-home-callensxavier-gmail-com-AutoevolveAI--claude-worktrees-openai-math-discovery/6ecda88c-9d6f-441a-9328-d4a192612987/tool-results")
EXTRACTS = {
    "godfrin": ("mcp-claude_ai_alphaXiv-get_paper_content-1792935241260.txt", "arXiv:2012.09067v1",
                "Godfrin, Beauvois, Sultan, Krotscheck, Dawidowski, Fak, Ollivier, The dispersion relation of Landau elementary excitations and the thermodynamic properties of superfluid 4He"),
    "beauvois": ("mcp-claude_ai_alphaXiv-get_paper_content-1792935289338.txt", "arXiv:1802.08120v3",
                 "Beauvois, Dawidowski, Fak, Godfrin, Krotscheck, Ollivier, Sultan, Microscopic dynamics of superfluid 4He: a comprehensive study by inelastic neutron scattering"),
}
TOOLCHAIN = ("Lean v4.34.0-rc2, Mathlib 85e3a25e006c35636f0e53b0e9296caca2685bc0 (qf-lake), imports QuantumFluids DualLength "
             "(SocrateAI-Scientific-QuantumFluids commit 10f74daf1b39d2ac51a785452329fff0003cfc83)")
NS = "QuantumFluids.AutoresearchSkBoundShape."


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


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def axiom_lines(j: Path, names: list[str]) -> list[str]:
    out = json.loads(j.read_text())["stdout"].replace("\n ", " ")
    return [l.strip() for l in out.split("\n") if any(f"'{NS}{n}'" in l for n in names)]


def lean_ev(names: list[str]) -> dict:
    prod = axiom_lines(C8 / "compile_main.json", names)
    re_ = axiom_lines(C8 / "paper_recompile_main.json", names)
    if len(prod) != len(names) or len(re_) != len(names):
        raise SystemExit(f"axiom lines missing for {names}")
    for l in prod + re_:
        if not l.endswith("[propext, Classical.choice, Quot.sound]"):
            raise SystemExit(f"axiom outside allowlist: {l}")
    ctl = json.loads((C8 / "paper_recompile_controls.json").read_text())["stdout"]
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output_producer": prod,
            "axiom_output_paper_recompile": re_, "allowlist": ["propext", "Classical.choice", "Quot.sound"],
            "sources": [file_ref(LEAN), file_ref(OWNER)],
            "compile_transcripts": [file_ref(C8 / "compile_main.json"), file_ref(C8 / "paper_recompile_main.json")],
            "planted_controls": {"file": file_ref(CTL), "transcript": file_ref(C8 / "paper_recompile_controls.json"),
                                 "output": ctl},
            "recompile_note": "paper-stage recompile by a separate AI agent instance with the producer's runner; not a human audit",
            "statement_adequacy": "reviewed by AI agents only (H8/verification.md for round 1; contribution/FORMAL.md); no human audit"}


def excerpt(key: str, lines: tuple[int, int]) -> dict:
    fname, aid, title = EXTRACTS[key]
    p = SRC / fname
    t = p.read_text().splitlines()
    return {"source": f"{title}, {aid} (alphaXiv full-text extraction)", "durable_reference": aid,
            "extraction_file": file_ref(p), "lines": list(lines), "text": "\n".join(t[lines[0] - 1:lines[1]])}


def num(files: list[Path], **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True,
            "instrument": f"rusty-SUNDIALS crates/qf-gpe2d at {RUSTY_SHA} (branch physics/ar-bogoliubov-2026-10-25, not pushed) and Python scripts in results/bogoliubov_sk",
            "files": [file_ref(p) for p in files], **kw}


def main() -> int:
    SRC.mkdir(exist_ok=True)
    for fname, _, _ in EXTRACTS.values():
        if not (SRC / fname).exists():
            shutil.copyfile(TOOLRES / fname, SRC / fname)
    shammass = SRC / "shammass_1207.3440_excerpt.txt"
    s = json.loads((DATA / "linear_response_summary.json").read_text())
    he = json.loads((DATA / "helium_tier_l.json").read_text())
    R = RUSTY / "results/bogoliubov_sk"

    claims = [
        rec("BS-A-0001", "A", "lean_axioms",
            "For 0 < hc, 0 < k, 0 < ks: 0 < bogoliubovSq hc ks k; epsBog^2 = epsFree^2 + (hc k)^2; 0 < sBog; sBog^2 = k^2/(ks^2+k^2); sBog^2 <= k/(2ks); sBog <= sqrt(k/(2ks)); sBog^2 = k/(2ks) iff k = ks. Statements about the model formulas only.",
            [], lean_ev(["bogoliubovSq_pos", "epsBog_sq", "sBog_pos", "sBog_sq", "sBog_sq_le", "sBog_le_sqrt", "sBog_sq_eq_iff"])),
        rec("BS-A-0002", "A", "lean_axioms",
            "feynman_sBog_exact: (hc k^2/(ks sBog))^2 = bogoliubovSq hc ks k, and sBog_sq_le_via_project (the envelope through the owner's feynman_ge_iff and ell_ge). Holds BY CONSTRUCTION since sBog is defined as epsFree/epsBog; not an independent many-body derivation.",
            ["BS-A-0001"], lean_ev(["feynman_sBog_exact", "sBog_sq_le_via_project"])),
        rec("BS-A-0003", "A", "lean_axioms",
            "sBog_eq_closed: sBog = k/sqrt(ks^2+k^2); sBog_sq_lt_sq and sBog_strictMonoOn: sBog hc ks is strictly increasing on (0, inf).",
            ["BS-A-0001"], lean_ev(["sBog_eq_closed", "sBog_sq_lt_sq", "sBog_strictMonoOn"])),
        rec("BS-A-0004", "A", "lean_axioms",
            "Phonon regime, two-sided: k/(ks+k) < sBog < k/ks.",
            ["BS-A-0003"], lean_ev(["sBog_lt_phonon", "phonon_lower_lt_sBog"])),
        rec("BS-A-0005", "A", "lean_axioms",
            "sBog < 1; 1 - sBog <= ks^2/k^2; sBog tends to 1 at infinity; epsBog = epsFree/sBog (the last by construction).",
            ["BS-A-0001"], lean_ev(["sBog_lt_one", "one_sub_sBog_le", "sBog_tendsto_one", "epsBog_eq_epsFree_div_sBog"])),
        rec("BS-A-0006", "A", "lean_axioms",
            "diffraction_test_model: if sqrt(k/(2ks)) < S then S != sBog hc ks k; peak_sqrt_iff_sq: for S > 0, sqrt(k/(2ks)) < S iff k/(2ks) < S^2.",
            ["BS-A-0001"], lean_ev(["diffraction_test_model", "peak_sqrt_iff_sq"])),
        rec("BS-A-0007", "A", "lean_axioms",
            "diffraction_test_dispersion: for S > 0, IF epsSq <= (hc k^2/(ks S))^2 (Feynman's inequality, an explicit hypothesis hfeyn, not proved) and sqrt(k/(2ks)) < S, then epsSq != bogoliubovSq hc ks k. Tier A covers the implication only.",
            ["BS-A-0006"], lean_ev(["diffraction_test_dispersion"])),
        rec("BS-A-0008", "A", "lean_axioms",
            "Kernel-checked controls of the test: 1 != sBog hc ks ks (fires on S = 1 at k = ks); not (sqrt(k/(2ks)) < sBog) (never fires on sBog); sqrt(k/(2ks)) < 1 for k < 2ks; k/ks < 1 for k < ks; non-vacuity sBog 1 1 1 ^ 2 = 1/(2*1).",
            ["BS-A-0001"], lean_ev(["diffraction_fires_free_at_selfdual", "diffraction_silent_on_sBog", "free_S_one_violates",
                                    "free_S_one_violates_phonon", "nonvacuous_selfdual"])),
        rec("BS-L-0001", "L", "citation",
            "Godfrin et al. (arXiv:2012.09067v1) Sec. II A: ultrasound measurements at very low temperatures yield c = 238.3 +- 0.1 m/s at saturated vapor pressure; molar mass of 4He 4.0026032 g/mol.",
            [], {"kind": "citation", "excerpts": [excerpt("godfrin", (348, 355)), excerpt("godfrin", (492, 497))]}),
        rec("BS-L-0002", "L", "citation",
            "Godfrin et al. (arXiv:2012.09067v1) Table VI: dispersion relation of 4He at SVP and T < 100 mK, k from 0 to 3.6 1/A in steps of 0.05, ultrasound data below 0.15 1/A; transcribed rows include (1.90, 0.7427) and (1.95, 0.7459).",
            [], {"kind": "citation", "excerpts": [excerpt("godfrin", (4538, 4616))],
                 "transcription": file_ref(R / "helium_tier_l.py")}),
        rec("BS-L-0003", "L", "citation",
            "Beauvois et al. (arXiv:1802.08120v3) Table I: at P = 0, roton gap 0.7416(10) meV at Q_R = 1.9260(2) 1/A, mu_R = 0.1240(4).",
            [], {"kind": "citation", "excerpts": [excerpt("beauvois", (2313, 2334))]}),
        rec("BS-L-0004", "L", "citation",
            "Shammass et al. (arXiv:1207.3440): the experimental static structure factor values in their Fig. 3 have been multiplied by a factor of 1.5 in order to agree with the 2D GPE simulation for low k.",
            [], {"kind": "citation", "source": "Shammass, Rinott, Berkovitz, Schley, Steinhauer, The phonon dispersion relation of a Bose-Einstein condensate, arXiv:1207.3440 (alphaXiv full text, 2026-10-25)",
                 "durable_reference": "arXiv:1207.3440", "excerpt_file": file_ref(shammass), "text": shammass.read_text()}),
        rec("BS-C-0001", "C", "argument",
            "Feynman's inequality at T = 0: if eps(k) is the lowest energy reached from the ground state by rho_k, then S(k,omega) = 0 for hbar omega < eps(k), and with the f-sum rule eps(k) S(k) <= eps0(k). Standard argument, not machine-checked; used only as an explicit hypothesis.",
            [], {"kind": "argument", "text": "Paper Section 2, Step 10. Zeroth moment = S(k); first moment = eps0(k) (f-sum); S(k,omega) >= 0 supported on hbar omega >= eps(k)."}),
        rec("BS-C-0002", "C", "argument",
            "Physical gloss: with ks = 2mc/hbar and hc = hbar c, bogoliubovSq is eps0(eps0 + 2gn) for the T = 0 weakly interacting Bose gas, and sBog = eps0/eps_B = (u_k - v_k)^2 is its Bogoliubov static structure factor. Not machine-checked; Tier A attaches to the formulas, never to this gloss.",
            ["BS-A-0001"], {"kind": "argument", "text": "hbar^2 k^2/2m = hbar c k^2 (hbar/2mc); 2gn eps0 = 2mc^2 hbar^2k^2/2m = (hbar c k)^2. Checked by the round-1 verifier (H8/verification.md)."}),
        rec("BS-C-0003", "C", "argument",
            "Linearised GP: omega^2 = eps0(eps0 + 2gn); after a phase kick of size eps the density cos-component is A(t) = (n k^2 eps/omega) sin(omega t), so S_amp = A_max/(2 n eps) = eps0/omega (Bijl-Feynman identification, not a quantum S(k)).",
            [], {"kind": "argument", "text": "Continuity d(delta n)/dt = -n laplacian(phase) gives the amplitude; paper Section 4."}),
        rec("BS-C-0004", "C", "argument",
            "Interpretation: reusing the start-of-step nonlinear phase makes a non-symmetric composition whose linearised eigenfrequency error is O(dt^2) while the invariant ellipse is distorted at O(dt); hence second-order frequency but first-order amplitude convergence.",
            [], {"kind": "argument", "text": "Not proved. A heuristic reading of the composition, offered independently of the numbers; BS-X-0003 is consistent with it but, being Tier X, cannot support it (gate run 1 blocked the earlier depends_on BS-X-0003 as a tier inversion, see gate_output_run1.txt)."}),
        rec("BS-X-0001", "X", "numeric",
            "GP linear response (g = 1, 32x32, 25 wavevectors): max |omega - eps_B|/eps_B = 4.09e-5 (phase kick), 4.06e-5 (density kick); S_amp vs S_freq 1.64e-4; Strang order 2.000; isotropy 1.78e-7; ground-state residual 4.31e-14; S_freq/sqrt(k/2ks) - 1 <= -1.381e-3 on the sweep.",
            ["BS-C-0003"], num([DATA / "linear_response_summary.json", DATA / "linear_response.json", RUSTY / "src/linear_response.rs"],
                               gates={k: v for k, v in s["gates"].items() if k.startswith(("pos_", "gs_", "bound_g1"))})),
        rec("BS-X-0002", "X", "numeric",
            "Negative controls: g = 0 gives omega = k^2/2 to 7.79e-13 and is >= 0.3355 (relative) from the g = 1 eps_B for k < ks; S = 1 fires at every sweep k < 2ks and is silent for k > 2ks.",
            [], num([DATA / "linear_response_summary.json"],
                    gates={k: v for k, v in s["gates"].items() if k.startswith(("neg_g0", "bound_g0"))})),
        rec("BS-X-0003", "X", "numeric",
            "The pinned Python reference data (tests/python_cross_check.rs) are reproduced by a composition that reuses the start-of-step nonlinear phase (max deviation 2.48e-16 from the pinned 4x4 data; textbook Strang deviates by 0.155). The upstream Python source was not inspected; the crate's own step/evolve use the same reused-phase composition. In linear response this composition's amplitude converges at first order (order 1.013; errors 2.65e-2 to 1.63e-3) and S_amp mismatch reaches 0.2497.",
            [], num([PAPER / "data/which_strang.out", R / "which_strang.py", RUSTY / "tests/python_cross_check.rs", DATA / "linear_response_summary.json"],
                    reference=s["dt_convergence_reference"])),
        rec("BS-X-0004", "X", "numeric",
            "Rust lr_series vs independent 1D numpy implementation: omega agrees to 1.9e-14..1.6e-12 relative, amplitude to <= 2.4e-9.",
            [], num([DATA / "crosscheck_rust_numpy.json", R / "numpy_crosscheck.py", R / "crosscheck_compare.py"])),
        rec("BS-X-0005", "X", "numeric",
            f"4He evaluation: ks = {he['k_s_inv_A']:.4f} 1/A; threshold sqrt(Q_R/2ks) = {he['threshold_at_Q_R_1.9260']:.4f}; under Feynman's inequality the upper bound eps0/(eps - err) (conservative where Table VI gives an error bar; k = 0.05 and 0.10 have none, so eps itself is used there, with large margins) stays below the threshold for all {he['n_silent']} tabulated k in [0.05, 0.90] 1/A (also under the strict variant); undecided for {he['n_undecided']} points from 0.95 1/A up, including the roton (S_up = {he['threshold_at_roton']['S_up_feynman']:.2f} at the tabulated k = {he['threshold_at_roton']['k']:.2f} 1/A, whose threshold is {he['threshold_at_roton']['sqrt_k_over_2ks']:.4f}). No claim that the roton S exceeds the threshold.",
            ["BS-L-0001", "BS-L-0002", "BS-L-0003", "BS-C-0001", "BS-A-0007"], num([DATA / "helium_tier_l.json", R / "helium_tier_l.py"])),
        rec("BS-X-0006", "X", "numeric",
            f"4He measured eps/eps_B = {he['threshold_at_roton']['eps_over_epsB']:.3f} at k = 1.95 1/A (minimum {min(r['eps_over_epsB'] for r in he['rows']):.3f} at 3.6 1/A); Bogoliubov S_B with the 4He c never fires; S = 1 fires at every tabulated k < 2ks.",
            ["BS-L-0001", "BS-L-0002"], num([DATA / "helium_tier_l.json"], controls=he["controls"])),
        rec("BS-X-0007", "X", "numeric",
            "qf-gpe2d cargo test 15/15 pass (9 unit, 5 linear-response, 1 Python cross-check); cargo fmt --check and clippy --all-targets exit 0.",
            [], num([R / "cargo_test.log", R / "cargo_fmt.log", R / "cargo_clippy.log", RUSTY / "tests/linear_response.rs"])),
        rec("BS-X-0008", "X", "numeric",
            "HuggingFace search: 30 HfApi.list_datasets queries found no measured S(k), S(Q,omega), Bragg or cold-atom dataset; the single neutron hit popoff4rtem/2D-Neutron-Diffraction-Dataset-for-Discriminative-Models (sha 648119c2030c5352c37a305deb74aa8ec84a4402, MIT tag) has a licence-only card and 4.38 GB of pickles; card and file list only, nothing downloaded or substituted.",
            [], num([DATA / "hf_search.json", DATA / "hf_neutron_card.json", R / "hf_search.py", R / "hf_card.py"])),
    ]
    ledger = {"schema_version": 1, "claims": claims}
    (HERE / "ledger.json").write_text(json.dumps(ledger, indent=1, ensure_ascii=False))
    print(f"claims {len(claims)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
