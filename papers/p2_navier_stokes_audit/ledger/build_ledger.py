"""Build the Elenchus claim ledger for the A2 paper (papers/p2_navier_stokes_audit). Prefix P2NS.

Conventions follow papers/p2_sandier_serfaty_lean/ledger/build_ledger.py: every claim has a content-addressed evidence blob
(evidence/<sha256>.json). A rows (lean_axioms) carry VERBATIM `#print axioms` lines from our own audit files and the hashes of the
replay and leanchecker logs, and rest on nothing; L rows carry verbatim excerpts of a cited source; C rows (argument) rest only on
A, L and C rows; X rows (numeric) are observations of scripts and are never depended on by a higher-tier row.
Every input is a saved file of results/proposal2/2026-10-26/A2/ (committed) or the Clay PDF text saved there; nothing is re-run here.
Gate: tools/ledger.py ledger.json --evidence-dir evidence (see run_gate.py).
Run: /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
W = PAPER.parents[1]
EV = HERE / "evidence"
A2 = W / "results/proposal2/2026-10-26/A2"
AUD = A2 / "evidence/audit"
LOGS = A2 / "logs"
CTL = A2 / "evidence/controls"
H9 = W / "results/autoresearch/2026-10-25/H9/AUDIT.md"
CORPUS = Path("/mnt/disks/disk-socrateai-local-1/callensxavier_home_data/SocrateAI-Scientific-Agora-LeanMaster/lean4basesource/openai-navierstokes")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
TOOLCHAIN = ("Lean 4.34.0-rc2 (commit 6a10ac8c22beadecabdbb0919c2b50214762f91d; lean binary sha256 "
             "e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550), Mathlib 85e3a25e006c35636f0e53b0e9296caca2685bc0 "
             "(reused prebuilt, trusted), corpus openai/NavierStokesAndEuler f9e8bc5b38b6e212696e8a30e3e91517af887bbd")
STATUS = ("A2 run 2026-10-26 (Proposal 2, item A2); rebuild, audit files and paper written by AI agent instances of one pipeline; "
          "no human audit of any statement; Comparator, lean4export and nanoda NOT run")
CLAY_TXT = A2 / "evidence/clay_navierstokes.txt"
CLAY_SHA = "c1b5f27b1a64705cfaf1afceea513db5deedca8a18ca56ab32e7f86445a06d0c"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def file_ref(p: Path) -> dict:
    s = str(p)
    rel = str(p.relative_to(W)) if s.startswith(str(W)) else s
    return {"path": rel, "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def axiom_lines(path: Path, name: str) -> list[str]:
    """The verbatim `#print axioms` line(s) for one declaration, joined across the wrapped bracket if any."""
    txt = path.read_text().replace("\n ", " ")
    out = [ln.strip() for ln in txt.split("\n") if ln.startswith(f"'{name}'")]
    if len(out) != 1:
        raise SystemExit(f"{name}: {len(out)} axiom lines in {path}")
    return out


def lean_ev(path: Path, name: str, extra: list[Path]) -> dict:
    lines = axiom_lines(path, name)
    assert lines[0].endswith("depends on axioms: [propext, Classical.choice, Quot.sound]"), lines
    return {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": lines, "allowlist": ALLOW,
            "compile_transcripts": [file_ref(path)],
            "sources": [file_ref(CORPUS / "NavierStokes/ComparatorSolution.lean"), file_ref(CORPUS / "Euler/Solution.lean")],
            "kernel_replay_and_checker_logs": [file_ref(p) for p in extra],
            "status": STATUS,
            "statement_adequacy": "not audited by a person; the Clay correspondence of each statement is a Tier C claim; "
                                  "#print axioms alone does not detect a declaration added without kernel checking, so this row is "
                                  "to be read together with the kernel replay logs listed here (see X-0004, X-0005)"}


def num(files: list[Path], instrument: str, **kw: object) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "instrument": instrument,
            "files": [file_ref(p) for p in files], **kw}


def arg(files: list[Path], text: str) -> dict:
    return {"kind": "argument", "text": text, "text_files": [file_ref(p) for p in files]}


def excerpt(first: int, last: int, must: list[str]) -> str:
    lines = CLAY_TXT.read_text().split("\n")[first - 1:last]
    t = "\n".join(lines)
    for m in must:
        assert m in t, (m, first, last)
    return t


def cite(claim_excerpts: dict[str, str], note: str) -> dict:
    return {"kind": "citation", "source": "C. L. Fefferman, Existence and smoothness of the Navier-Stokes equation (Clay Mathematics Institute "
            "official problem description), https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf",
            "pdf_sha256": CLAY_SHA, "extraction": "pdftotext -layout; verbatim lines of the saved extraction (superscripts flattened by the extractor)",
            "excerpts": claim_excerpts, "excerpt_file": file_ref(CLAY_TXT), "citation_check_run": False, "note": note}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    result = A2 / "result.json"
    replay_logs = [LOGS / "replay_ns.log", LOGS / "replay_euler.log", LOGS / "leanchecker_roots.log"]
    ns_aud, eu_aud = AUD / "SolutionAudit_NS.out", AUD / "SolutionAudit_Euler.out"
    ex_c = excerpt(74, 81, ["(C) Breakdown of Navier", "(D) Breakdown of Navier", "there exist no solutions"])
    ex_four = excerpt(63, 66, ["we ask for a proof of one"])
    ex_err = excerpt(216, 217, ["should be made explicit in Eqn (8)"])
    ex_eul = excerpt(82, 83, ["not on the Clay Institute"])
    readme = (CORPUS / "README.md").read_text()
    assert "These are alternatives" in readme and "Breakdown of Navier" in readme
    readme_ex = readme[readme.index("## Navier Stokes"):readme.index("## Building the formalizations")]

    claims = [
        # ---------------------------------------------------------------- Tier A (our own audit files, re-run by us)
        rec("P2NS-A-0001", "A", "lean_axioms",
            "Lean theorem NavierStokes.Comparator.navier_stokes_breakdown_R3 (NavierStokes/ComparatorSolution.lean, over the solution-side "
            "definitions of NavierStokes/ComparatorDefinitions.lean): for every nu > 0 there are a smooth, divergence-free, rapidly decaying "
            "u0 : R^3 -> R^3 and a smooth, rapidly decaying force f such that no pair (v, p) of smooth functions on R^3 x [0,infty) satisfies "
            "the Navier-Stokes equations with data (nu, u0, f), the divergence-free condition, the initial condition and bounded energy. "
            "Our own #print axioms audit file (SolutionAudit_NS.lean, rc 0) reports exactly [propext, Classical.choice, Quot.sound]; the "
            "module was rebuilt from source and all 53,752 declarations of its closure re-passed the kernel (replay log hashed here). "
            "A statement about the Lean term only.",
            [], lean_ev(ns_aud, "NavierStokes.Comparator.navier_stokes_breakdown_R3", [LOGS / "replay_ns.log", LOGS / "leanchecker_roots.log"])),
        rec("P2NS-A-0002", "A", "lean_axioms",
            "Lean theorem NavierStokes.Comparator.navier_stokes_breakdown_periodic: for every nu > 0 there are smooth, divergence-free, "
            "1-periodic data u0 and a smooth 1-periodic force f with time decay such that no pair (v, p) of smooth functions on R^3 x [0,infty), "
            "with v and p 1-periodic in space, satisfies the equations with data (nu, u0, f), the divergence-free condition and the initial "
            "condition. Same audit file, same axioms, same replay as A-0001. A statement about the Lean term only (the periodic pressure is a "
            "field of the solution class; see C-0003).",
            [], lean_ev(ns_aud, "NavierStokes.Comparator.navier_stokes_breakdown_periodic", [LOGS / "replay_ns.log", LOGS / "leanchecker_roots.log"])),
        rec("P2NS-A-0003", "A", "lean_axioms",
            "Lean theorem Euler.euler_breakdown_R3 (Euler/Solution.lean): there is a smooth, divergence-free, rapidly decaying u0 : R^3 -> R^3 "
            "such that no triple (v, p) satisfies the incompressible Euler existence-and-smoothness class EulerExistenceAndSmoothnessR3 "
            "(smooth, bounded energy) for u0. Our own audit file SolutionAudit_Euler.lean (rc 0) reports exactly [propext, Classical.choice, "
            "Quot.sound]; all 34,648 declarations of the closure re-passed the kernel (replay log hashed here). A statement about the Lean term only.",
            [], lean_ev(eu_aud, "Euler.euler_breakdown_R3", [LOGS / "replay_euler.log", LOGS / "leanchecker_roots.log"])),
        rec("P2NS-A-0004", "A", "lean_axioms",
            "Lean theorem Euler.exists_compact_smooth_euler_singularity (Euler/Solution.lean): a supplementary statement for compactly supported "
            "smooth divergence-free initial velocity on R^3 in a Sobolev solution class on [0,T*), with a Beale-Kato-Majda-type divergence of "
            "the time integral of the vorticity sup norm. Same audit file, axioms and replay as A-0003. A statement about the Lean term only; "
            "we did not audit its solution class against a literature source.",
            [], lean_ev(eu_aud, "Euler.exists_compact_smooth_euler_singularity", [LOGS / "replay_euler.log", LOGS / "leanchecker_roots.log"])),
        # ---------------------------------------------------------------- Tier L
        rec("P2NS-L-0001", "L", "citation",
            "Fefferman's official statement of the Clay problem: 'we ask for a proof of one of the following four statements' (A), (B), (C), (D); "
            "(C) Breakdown of Navier-Stokes solutions on R^3 and (D) Breakdown on R^3/Z^3 are the two negative alternatives, as quoted.",
            [], cite({"four_statements": ex_four, "C_and_D": ex_c}, "Read in the saved extraction of the PDF; the PDF was fetched 2026-10-26 by curl; citation_check.py was not run.")),
        rec("P2NS-L-0002", "L", "citation",
            "The Clay errata appended to the problem description: 'The further condition p(x + e_j, t) = p(x, t) should be made explicit in Eqn (8).'",
            [], cite({"errata": ex_err}, "Verbatim line of the saved extraction; its placement 'in Eqn (8)' (data hypotheses) is the PDF's.")),
        rec("P2NS-L-0003", "L", "citation",
            "Fefferman on the Euler equations: 'These problems are also open and very important for the Euler equations (nu = 0), although the Euler "
            "equation is not on the Clay Institute's list of prize problems.'",
            [], cite({"euler": ex_eul}, "Verbatim lines of the saved extraction.")),
        rec("P2NS-L-0004", "L", "citation",
            "The corpus README (openai/NavierStokesAndEuler at f9e8bc5b) describes its results as the two Navier-Stokes results for every positive "
            "viscosity, named as alternatives (C) and (D) of the Clay description, and a smooth compactly supported divergence-free Euler initial "
            "velocity whose unforced solution develops a singularity in finite time. This records what the corpus authors claim, not that it holds.",
            [], {"kind": "citation", "source": "openai/NavierStokesAndEuler README.md at f9e8bc5b38b6e212696e8a30e3e91517af887bbd",
                 "excerpts": {"readme": readme_ex}, "excerpt_file": file_ref(CORPUS / "README.md"), "citation_check_run": False,
                 "note": "Read from the local clone; remote origin https://github.com/openai/NavierStokesAndEuler.git."}),
        # ---------------------------------------------------------------- Tier C
        rec("P2NS-C-0001", "C", "argument",
            "Scope. We independently rebuilt and audited the openai/NavierStokesAndEuler Lean corpus (rebuild, axioms, soundness-escape scans, "
            "kernel replay, elaborated-statement identity, a second statement-fidelity reading). This is not a claim that a Clay problem is "
            "solved, and not a verification that the mathematics of the proof is correct beyond what the checks in this paper establish. Credit "
            "for the proofs belongs to the corpus authors; the Clay Institute's own process decides any prize.",
            ["P2NS-A-0001", "P2NS-A-0002", "P2NS-A-0003", "P2NS-A-0004", "P2NS-L-0001", "P2NS-L-0004"],
            arg([A2 / "REBUILD.md", A2 / "AXIOMS.md", A2 / "SOUNDNESS_SCAN.md", A2 / "FIDELITY2.md", result],
                "Preregistered wording rule of Proposal 2 item A2: strictly 'independently rebuilt and audited'.")),
        rec("P2NS-C-0002", "C", "argument",
            "Fidelity of (C): a field-by-field reading (FIDELITY2.md, written before reading H9) of Fefferman's (C) against the Lean statement "
            "navier_stokes_breakdown_R3 and the definitions it is stated over found no mismatch: nu > 0 universally quantified; u0 smooth, "
            "divergence-free with (4); f smooth on R^3 x [0,infty) with (5); no solution (v,p) of (1), (2), (3), (6), (7), with the solution class "
            "carrying no extra restriction, and (7) encoded as MemLp together with a uniform energy bound. A judgement of statement fidelity "
            "by an AI agent, not a person. The witness uses zero initial data and a nonzero force, which (C) allows; (C) is not the negation of (A), "
            "which takes f = 0.",
            ["P2NS-A-0001", "P2NS-L-0001"],
            arg([A2 / "FIDELITY2.md"], "Table '(C) Breakdown on R^3' of FIDELITY2.md; the elaborated-term identity of the solution-side and "
                "reference statements is an observation (X-0007) cited in the text, not a premise of this row.")),
        rec("P2NS-C-0003", "C", "argument",
            "Fidelity of (D): the Lean statement navier_stokes_breakdown_periodic matches Fefferman's (D) as corrected by the Clay errata, with "
            "one interpretive caveat: it requires the pressure to be 1-periodic as a field of the solution class. This shrinks the class of "
            "admissible solutions, so nonexistence is weaker than nonexistence read against the main text alone (without periodic pressure, "
            "p = -g(t).x with a spatially constant flow is a classical non-uniqueness device). The errata attaches the condition to Eqn (8), the data "
            "hypotheses, although p is an unknown; reading it as a condition on accepted solutions is the only coherent reading we found. "
            "Judgement of an AI agent.",
            ["P2NS-A-0002", "P2NS-L-0001", "P2NS-L-0002"],
            arg([A2 / "FIDELITY2.md", H9], "Table '(D) Breakdown on R^3/Z^3' and the caveat of FIDELITY2.md; H9 AUDIT.md row D6 agrees.")),
        rec("P2NS-C-0004", "C", "argument",
            "Euler: euler_breakdown_R3 is the (C)-type statement with nu = 0 and f = 0 (conditions (1) with nu = 0 and f = 0, (2), (3), (4), (6), "
            "(7)); the Euler equations are not on the Clay list. exists_compact_smooth_euler_singularity has no Clay counterpart and is reported "
            "only as a Lean statement; its BKM-type clause matches the form of the Beale-Kato-Majda remark of the PDF, and its solution class was "
            "read but not audited against a literature source.",
            ["P2NS-A-0003", "P2NS-A-0004", "P2NS-L-0003"], arg([A2 / "FIDELITY2.md"], "Section 'Euler' of FIDELITY2.md.")),
        rec("P2NS-C-0005", "C", "argument",
            "Implication, conditional and not a Clay determination: if the Lean statement of (C) is a faithful formalization of Fefferman's (C) "
            "(a human judgement, C-0002), and if the Lean 4.34.0-rc2 kernel, the toolchain and the reused Mathlib are sound, then the kernel-checked "
            "theorem navier_stokes_breakdown_R3 is a formal proof of Fefferman's alternative (C). "
            "This is not a Clay determination: the Clay Institute's own process decides whether anything is a solution and whether any prize is due. Nothing in this paper "
            "says the problem is solved, or that the mathematics has been refereed by people.",
            ["P2NS-A-0001", "P2NS-C-0002", "P2NS-L-0001"], arg([A2 / "FIDELITY2.md", H9], "H9 AUDIT.md section 'Fidelity in spirit' makes the same conditional statement.")),
        rec("P2NS-C-0006", "C", "argument",
            "Why #print axioms alone is insufficient (a demonstration of a known limitation of axiom printing, not a new vulnerability): "
            "(1) Lean's addDecl run under set_option debug.skipKernelTC true stores a declaration without kernel type checking; (2) the .olean "
            "serializes it; (3) an importing file trusts the stored declaration; (4) #print axioms walks constant references only, and the forged "
            "proof True.intro of False references no axiom; (5) only a replay that re-runs the kernel on the stored declarations compares the "
            "stored type with the stored value and rejects it. Hence the axiom verdict (A-0001..A-0004) is to be read together with the kernel replay "
            "and with the source scan, which finds no skipKernelTC, addDecl, or set_option in the corpus. The observation on the planted module is X-0004.",
            ["P2NS-A-0001"], arg([CTL / "forged/src/A2Forged.lean", CTL / "forged/forged_control.log", CTL / "forged/replay_control.log"],
                                 "Explanation of the mechanism; the observed outputs of the planted control are recorded in X-0004.")),
        rec("P2NS-C-0007", "C", "argument",
            "What is not established: (i) Comparator, lean4export and nanoda were not run (the Comparator require was removed from the build copy "
            "and is absent from the prebuilt package set; the Comparator build on this machine targets Lean 4.34.1 while the corpus pins 4.34.0-rc2; "
            "nanoda is not installed); the kernel replay and leanchecker use the same Lean kernel through the same Lean.Replay mechanism, so they "
            "are a second driver of one kernel, not an independent kernel; (ii) Mathlib 85e3a25e and its dependencies were reused and trusted, neither "
            "rebuilt nor replayed; (iii) the diff of the challenge file against google-deepmind/formal-conjectures@8bf45ed (and whether the pinned "
            "openai/NavierStokesAndEuler@8937a8f referred to by the upstream index equals f9e8bc5b) was not done; (iv) the mathematics of the proof "
            "was not refereed by people by us, and the natural-language papers were not checked; (v) the Lean kernel and toolchain are trusted; "
            "(vi) statement fidelity is a human judgement, made here by AI agents, and no person has audited any statement.",
            ["P2NS-A-0001", "P2NS-A-0002", "P2NS-A-0003", "P2NS-A-0004"],
            arg([A2 / "REBUILD.md", A2 / "SOUNDNESS_SCAN.md", A2 / "AXIOMS.md"], "Trust base sections of REBUILD.md, SOUNDNESS_SCAN.md and AXIOMS.md.")),
        rec("P2NS-C-0008", "C", "argument",
            "Limitations of the audit itself: one AI agent instance rebuilt and audited, another wrote the fidelity table blind to H9, and a third "
            "(this paper stage) wrote the paper from the saved logs without re-running any check; all are instances of one pipeline. The planted "
            "controls show that each layer can reject what it is designed to reject; they do not show that no other kind of escape exists. The "
            "rebuild ran at machine contention (an unrelated Lean job ran concurrently), so wall times are not benchmarks. No human has reviewed "
            "the work.",
            ["P2NS-A-0001", "P2NS-C-0007"], arg([result, A2 / "REBUILD.md"], "result.json 'prominent_caveats' and REBUILD.md 'Contention'.")),
        # ---------------------------------------------------------------- Tier X
        rec("P2NS-X-0001", "X", "numeric",
            "Rebuild from source at HEAD f9e8bc5b (tree clean) with Lean 4.34.0-rc2 and the corpus's lakefile options: 609 modules of the "
            "NavierStokes.ComparatorSolution closure (rc 0, 'Build completed successfully (9371 jobs)', 3,300 s), 1,829 modules of Euler.Solution "
            "(rc 0, 10591 jobs, 5,109 s), the 2 ComparatorChallenges modules (rc 0, 4 intentional sorry warnings); 2,440 .olean files; zero warnings "
            "and zero errors in the two solution builds; Mathlib reused (0 'Built Mathlib' lines). One build-only lakefile change: the Comparator "
            "require and two manifest entries removed in the build copy.",
            ["P2NS-A-0001"], num([A2 / "REBUILD.md", LOGS / "build_progress.log", LOGS / "build_ComparatorChallenges.Euler.log",
                                  LOGS / "build_ComparatorChallenges.NavierStokes.log", LOGS / "lake_LEAN_PATH.txt", LOGS / "nobuild_mathlib.log", result],
                                 "lake build -v under taskset -c 0-3, LEAN_NUM_THREADS=4 (scripts/run_build.sh)",
                                 note="Contention: an unrelated Lean job ran concurrently; times are not benchmarks.")),
        rec("P2NS-X-0002", "X", "numeric",
            "Source scan (scripts/source_scan.py, comments stripped, strings blanked) of the 2,585-module closure and of all 2,659 corpus .lean files: "
            "0 code hits for sorry-in-solutions, admit, native_decide, ofReduceBool/trustCompiler, axiom, implemented_by, extern, unsafe, csimp, opaque, "
            "partial, #exit, set_option of any kind, debug.*, skipKernelTC, addDecl/modifyEnv/setEnv, #eval/run_cmd/initialize, import Lean, "
            "command_elab attributes; 4 sorry hits, all placeholders of ComparatorChallenges (not imported by either solution). The pattern group "
            "elab/macro/syntax matches 150 (closure) and 156 (all files) lines, all of them 'local notation' (148 / 154) or @[inherit_doc] (2 / 2); "
            "no file starts a line with elab, macro, syntax or macro_rules. attribute [local instance]: 10 (closure), 11 (all files). Planted "
            "controls: every category caught on a scratch copy; unmodified copy clean.",
            ["P2NS-A-0001"], num([AUD.parent / "scan_closure.txt", AUD.parent / "scan_allfiles.txt", AUD.parent / "scan_closure.json",
                                  AUD.parent / "scan_allfiles.json", CTL / "scan_plant/scan_result.txt", CTL / "scan_plant/plants.lean.txt"],
                                 "scripts/source_scan.py (Python regular expressions); a grep for line-initial elab/macro/syntax over the corpus found no file")),
        rec("P2NS-X-0003", "X", "numeric",
            "Environment scan (soundnessScan in lean_scripts/DumpCore.lean.txt, run inside the built environment): the proof closure of NS has 93,597 "
            "constants (31,516 from 597 corpus modules) and of Euler 94,411 (26,213 from 1,756 corpus modules); the only axioms in either closure are "
            "propext, Quot.sound, Classical.choice; no ofReduceBool, ofReduceNat, trustCompiler or sorryAx; no flagged constant from a corpus module "
            "(the flags are core extern/implemented_by/opaque and Mathlib irreducible_def wrappers); the corpus adds no axiom to the 15 that core "
            "declares; 12 (NS) and 39 (Euler) corpus _unsafe_rec compiler auxiliaries exist in the environment, none in a proof closure. Planted "
            "controls (axiom, native_decide auxiliary axiom, implemented_by, sorryAx, unsafe, partial, extern) all flagged.",
            ["P2NS-A-0001"], num([AUD / "sound_ns.txt", AUD / "sound_euler.txt", CTL / "env/ctl_sound.txt", CTL / "env/EnvControl.out", CTL / "env/EnvControl.lean",
                                  A2 / "evidence/lean_scripts/DumpCore.lean.txt"], "lean --run / lake env lean metaprogram walking the proof closure")),
        rec("P2NS-X-0004", "X", "numeric",
            "Planted forged declaration (controls/forged/src/A2Forged.lean): False 'proved' by True.intro, added with addDecl under debug.skipKernelTC. "
            "It compiles; a theorem using it prints 'does not depend on any axioms' under #print axioms; #check from a fresh importing file succeeds. "
            "leanchecker A2Forged exits 1 and A2Replay.lean exits 1 with '(kernel) declaration type mismatch, A2Forged.forged_false has type True but "
            "it is expected to have type False'. The positive control (NavierStokes.ComparatorDefinitions, 95 declarations) replays OK.",
            ["P2NS-A-0001"], num([CTL / "forged/src/A2Forged.lean", CTL / "forged/forged_control.log", CTL / "forged/replay_control.log",
                                  CTL / "forged/Importer.lean"], "lake env lean; leanchecker; lean --run A2Replay.lean")),
        rec("P2NS-X-0005", "X", "numeric",
            "Kernel replay of the whole corpus (A2Replay.lean, Lean.Replay, one shared base environment of 774,999 Mathlib-side constants): "
            "NS closure 609 modules, 53,752 declarations, 'REPLAY OK' in 621,964 ms (wall 11:33, max RSS 8.1 GB); Euler closure 1,829 modules, 34,648 "
            "declarations, 'REPLAY OK' in 933,056 ms (wall 15:42, max RSS 9.8 GB). Two corpus declarations per closure (the congr_simp lemmas "
            "HasDerivWithinAt/HasDerivAt and compLpL/compLeftContinuous) already exist in Mathlib with identical type hashes. "
            "Lean.Replay skips by design the 51 compiler-generated _unsafe_rec auxiliaries (12 NS, 39 Euler; none in any proof closure) and the 4 identical congr_simp "
            "duplicates; the auditor's independent replay attributes 53,750 / 34,646 constants to corpus modules (the 2 congr_simp per closure belong to Mathlib modules).",
            ["P2NS-A-0001", "P2NS-A-0003"], num([LOGS / "replay_ns.log", LOGS / "replay_euler.log", LOGS / "replay_clashes_ns.log", LOGS / "replay_clashes_euler.log",
                                                  A2 / "evidence/lean_scripts/A2Replay.lean", AUD / "replay_corpus_ns.txt", AUD / "replay_corpus_euler.txt"],
                                                 "lean --run A2Replay.lean under /usr/bin/time -v, pinned to one core")),
        rec("P2NS-X-0006", "X", "numeric",
            "leanchecker of the v4.34.0-rc2 toolchain on 8 modules (NavierStokes.ComparatorSolution, ComparatorR3Theorem, ComparatorTheorem, "
            "ComparatorDefinitions, Euler.Solution, Euler.SolutionDefinitions, ComparatorChallenges.NavierStokes, ComparatorChallenges.Euler): "
            "all rc 0, 15-17 s each. The challenge modules pass because sorryAx is a legitimate kernel axiom; the axiom check, not the kernel, rejects sorry. "
            "leanchecker without --fresh checks only the named module's own declarations against its imports; a forged lemma in an imported module would pass it "
            "(auditor control), so closure coverage rests on the full replay (X-0005).",
            ["P2NS-A-0001"], num([LOGS / "leanchecker_roots.log"], "leanchecker (toolchain binary) under lake env")),
        rec("P2NS-X-0007", "X", "numeric",
            "Elaborated-statement identity: the transitive statement closure (types of all constants, values of definitions and opaques; not theorem "
            "proofs) of the two root theorems has 5,599 constants (NS) and 5,521 (Euler) in the reference environment (verbatim ComparatorChallenges "
            "file + dump) and in the solution environment; 0 only on either side, 0 differing after normalising the module component of hygienic binder "
            "names (alpha-renaming); 23 (NS) and 25 (Euler) corpus constants also compared as full Expr text. Raw differences before normalisation (4 NS "
            "constructor types; 3 Euler constants) have equal Expr.hash. Negative control: changing < E to <= E in the reference gives 1 differing "
            "constant (NavierStokesExistenceAndSmoothnessRn.mk). Expr.hash is used for non-corpus constants.",
            ["P2NS-A-0001", "P2NS-A-0003"], num([AUD / "compare_ns.txt", AUD / "compare_euler.txt", AUD / "compare_ns.json", AUD / "compare_euler.json",
                                                  CTL / "dumpdiff/compare_mutated.txt", CTL / "dumpdiff/compare_mutated.json", AUD / "ChallengeDump_NS.lean"],
                                                 "scripts/compare_dumps.py over DumpCore.lean.txt dumps")),
        rec("P2NS-X-0008", "X", "numeric",
            "Planted #print axioms controls (controls/env/EnvControl.lean): a sorry (reports sorryAx), a smuggled axiom (reports the axiom), and "
            "native_decide proving a false equation through implemented_by (reports an auxiliary ..._native.native_decide.ax_1_1 axiom, not "
            "Lean.ofReduceBool, on 4.34.0-rc2); each is outside the whitelist and is caught.",
            ["P2NS-A-0001"], num([CTL / "env/EnvControl.out", CTL / "env/EnvControl.lean", CTL / "env/A2Plants.lean.txt"], "lake env lean; #print axioms")),
        rec("P2NS-X-0009", "X", "numeric",
            "Semantics probes compiled against the pinned Mathlib (audit/Semantics.lean, Semantics2.lean): the notation infinity under open ContDiff "
            "elaborates to WithTop.some (top : NatENat), not the analytic omega ('example : (infinity : WithTop NatENat) != omega := by decide' and "
            "an rfl example compile); the Laplacian on R^3 -> R^3 is instLaplacian and equals the sum over an orthonormal basis of D^2 w(x)[e_i,e_i] "
            "(an example using laplacian_eq_iteratedFDeriv_orthonormalBasis compiles); gradient is the Riesz representative of fderiv; the norm on R^3 x R "
            "is the max (rfl). One #check line of Semantics.lean uses a name that does not exist (InnerProductSpace.laplacian) and reports an "
            "unknown-identifier error; the assertions are the example lines, none of which errors.",
            [], num([AUD / "Semantics.lean", AUD / "Semantics.out", AUD / "Semantics2.lean", AUD / "Semantics2.out"], "lake env lean")),
        rec("P2NS-X-0010", "X", "numeric",
            "Comparison of the two statement audits: FIDELITY2.md (written before reading H9) and H9 AUDIT.md (2026-10-25) agree on every row of (C) "
            "(all MATCH) and on (D) (matches the errata-corrected text; the periodic-pressure caveat); no disagreement on any row. H9's open caveats "
            "4 (Mathlib version) and 6 (does the solution prove this exact statement) are addressed by X-0009 and X-0007; the diff against "
            "formal-conjectures@8bf45ed remains open in both.",
            [], num([A2 / "FIDELITY2.md", H9, result], "reading and comparison by an AI agent; no tool")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": claims}, indent=1, ensure_ascii=False))
    tiers = {t: sum(1 for c in claims if c["tier"] == t) for t in "ALCX"}
    print(f"claims {len(claims)} {tiers}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
