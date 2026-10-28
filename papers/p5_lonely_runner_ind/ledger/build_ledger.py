"""Build the Elenchus claim ledger for the LR-IND paper (papers/p5_lonely_runner_ind).

Modelled on papers/p4_amplifier_census_n11/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not
be filed above anything in its depends_on, and the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
An independent AI audit exists (AUDIT.md, ACCEPT_WITH_CORRECTIONS, not a person): Tier A rows carry an ai_audit field and the gate field audit stays null,
so LEDGER_UNAUDITED_TIER_A remains open (exit 1 is the honest state).
Run:  /home/callensxavier_gmail_com/AutoevolveAI/.venv/bin/python -I build_ledger.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EV = HERE / "evidence"
DATA = PAPER / "data"
LEAN = DATA / "lean"
LOGS = DATA / "logs"
TOOLCHAIN = ("Lean 4.34.1 + Mathlib d13f23b7 through scripts/certified_numerics/lean_pinned.py (module imports "
             "Mathlib.Tactic; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("AI-audited (AUDIT.md, a different AI agent instance, not a person); producer leanchecker replay rc 0 on "
          "Programmes.LonelyRunnerInd.ScalarInputs (data/logs/leanchecker.json); the auditor compiled a /tmp copy with lean_pinned.py compile, "
          "built its own olean and replayed it, rc 0; NO human audit of statement adequacy, NO statement lock")
AI_AUDIT = {"auditor": "independent AI audit agent (separate instance, producer != verifier), 2026-10-28", "human": False,
            "report": "papers/p5_lonely_runner_ind/AUDIT.md", "verdict": "ACCEPT_WITH_CORRECTIONS",
            "scope": "own compile of a /tmp copy of ScalarInputs.lean with #print axioms appended, own olean + leanchecker replay, escape-hatch grep, "
                     "comparison of the Lean P10 list with Table 1 of arXiv 2604.23906 v2 and with all primes in [127, 467]",
            "not_scope": "statement adequacy (the Lean statements about scalar inputs mean what their gloss says) not certified by a person; nothing beyond scalar inputs is formalised",
            "note": "AI audit, not a person: the gate field audit is left null so LEDGER_UNAUDITED_TIER_A stays open; no statement lock"}
SRC_COMMIT = "f2016dc913ac03d301076c1bb8126638a8bec4c1"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def blob(obj: dict) -> str:
    raw = json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False).encode()
    d = sha(raw)
    EV.mkdir(parents=True, exist_ok=True)
    (EV / f"{d}.json").write_bytes(raw)
    return f"sha256:{d}"


def fref(p: Path) -> dict:
    return {"path": str(p.relative_to(PAPER)), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}


def rec(cid: str, tier: str, kind: str, statement: str, depends: list[str], ev: dict) -> dict:
    r = {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
         "depends_on": depends, "evidence": blob(ev), "audit": None}
    if tier == "A":
        r["ai_audit"] = AI_AUDIT
    return r


def axioms_from(path: Path, names: list[str]) -> list[str]:
    out = json.loads(path.read_text())["output"]
    flat = out.replace("\n", " ")
    lines: list[str] = []
    for n in names:
        i = flat.find(f"'{n}'")
        if i < 0:
            raise SystemExit(f"axiom line missing for {n}")
        j = flat.find("]", i)
        k = flat.find("does not depend on any axioms", i)
        end = j if (k < 0 or (j >= 0 and j < k)) else k + len("does not depend on any axioms") - 1
        lines.append(" ".join(flat[i:end + 1].split()))
    return lines


def cite(source: str, where: str, text: str, note: str) -> dict:
    return {"kind": "citation", "source": source, "where": where, "text": text, "note": note}


def arg(subtier: str, text: str, files: list[Path], instrument: str) -> dict:
    return {"kind": "argument", "subtier": subtier, "text": text, "files": [fref(f) for f in files],
            "instrument": instrument, "source_commit": SRC_COMMIT}


def num(files: list[Path], note: str) -> dict:
    return {"kind": "numeric", "tier": "X", "claim_licence": False, "ran": True, "note": note,
            "files": [fref(f) for f in files]}


def main() -> int:
    for old in EV.glob("*.json"):
        old.unlink()
    d = DATA
    thm = ["LonelyRunnerInd.P10_length", "LonelyRunnerInd.P10_nodup", "LonelyRunnerInd.P10_gt_k2k",
           "LonelyRunnerInd.P10_prime", "LonelyRunnerInd.k_succ_prime", "LonelyRunnerInd.choose_11_2",
           "LonelyRunnerInd.B10_le_prod_nat", "LonelyRunnerInd.B10_le_prod",
           "LonelyRunnerInd.B10_not_le_prod_without_467"]
    c = [
        rec("LRI-A-0001", "A", "lean_axioms",
            "LonelyRunnerInd.ScalarInputs: P10 (typed from Table 1, row k = 10, of arXiv 2604.23906 v2) has length 61 (P10_length), no duplicates (P10_nodup), "
            "every entry is prime (P10_prime) and > 110 = 10^2 + 10 (P10_gt_k2k); 11 is prime (k_succ_prime); C(11,2) = 55 (choose_11_2); "
            "55^90 <= 10^10 * prod P10 in N (B10_le_prod_nat, kernel decide) and ((C(11,2))^9 / 10)^10 <= prod P10 in Q (B10_le_prod), i.e. B_10 <= prod P10; "
            "55^90 <= 10^10 * (prod P10 / 467) is false (B10_not_le_prod_without_467). "
            "These are statements about a list of numbers; they do not formalise J(10, p), Lemma 2.6, Proposition 2.7 or LRC(9).",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axioms_from(LOGS / "lean_axioms.json", thm), "allowlist": ALLOW,
                 "compile_transcript": fref(LOGS / "lean_compile.json"), "axiom_transcript": fref(LOGS / "lean_axioms.json"),
                 "sources": [fref(LEAN / "ScalarInputs.lean"), fref(LEAN / "AxiomAudit.lean")],
                 "leanchecker_replay": fref(LOGS / "leanchecker.json"), "status": STATUS,
                 "statement_adequacy": "not audited by anyone; the statements are about a hand-typed list P10 compared by the auditor with Table 1 and with all primes in [127, 467]"}),
        rec("LRI-A-0002", "A", "lean_axioms",
            "Lean controls: ControlsMustFail.lean (P10.length = 60, and the bound without 467 stated as holding) is rejected by the kernel (rc 1, "
            "logs/lean_ctl_mustfail.json); ControlsSorry.lean compiles with rc 0 but its axiom audit reports sorryAx for LonelyRunnerInd.ctl_cheat "
            "(logs/lean_ctl_sorry.json), which a compile exit code alone would accept.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axioms_from(LOGS / "lean_ctl_sorry.json", ["LonelyRunnerInd.ctl_cheat"]),
                 "allowlist": ALLOW, "compile_transcript": fref(LOGS / "lean_ctl_sorry.json"),
                 "rejections": [fref(LOGS / "lean_ctl_mustfail.json")],
                 "sources": [fref(LEAN / "ControlsMustFail.lean"), fref(LEAN / "ControlsSorry.lean")],
                 "leanchecker_replay": fref(LOGS / "leanchecker.json"), "status": STATUS,
                 "statement_adequacy": "not audited by anyone"}),
        # ------------------------------------------------------------------ L
        rec("LRI-L-0001", "L", "citation",
            "Sungkawichai-Trakulthongchai (S-T), arXiv 2604.23906 v2, Defs. 2.1 and 2.3: Z_{p,l} = {x in Z_{lp} : x not = 0 mod p}; v in Z_{p,l}^k is (k,p,l)-proper iff some i has "
            "gcd(l, v_j : j != i) > 1 or some t in (1/(lp))Z has ||t v_i|| >= 1/(k+1) for all i; I(k,p,l) = improper tuples; J(k,p) = v in Z_{p,1}^k with v in "
            "pi_{lp -> p} I(k,p,l) for every l. Table 1, row k = 10: P_10 = the 61 primes 127..467.",
            [], cite("arXiv:2604.23906v2", "Defs. 2.1, 2.3; Table 1",
                     "Definitions as read by the producer and re-read by the independent AI auditor",
                     "taken as stated; the producer implements properness as (k+1) min(r, N-r) >= N with N = lp, equivalent in integers")),
        rec("LRI-L-0002", "L", "citation",
            "S-T results used: Lemma 2.4 (J = empty iff I(k,p,l) = empty for some l); Corollary 2.5 (if LRC(k-1) holds and J(k,p) = empty then p divides u_1...u_k "
            "for every counterexample u); Proposition 2.7 (if LRC(k-1) holds, J(k,p) = empty for all p in P and prod P >= B_k then LRC(k) holds); Lemma 2.2 (pre-jump); "
            "Remark 3.2 and Section 5.2 (the k = 10 plan x2 x2 x2 /8 leaves only the class of (1..10)); Propositions 1.4/4.1/4.4 and Lemma 4.3 (the identity fibre at level k+1 = 11).",
            ["LRI-L-0001"], cite("arXiv:2604.23906v2", "Lemmas 2.2, 2.4, Cor. 2.5, Prop. 2.7, Rem. 3.2, Sec. 5.2, Props. 1.4/4.1/4.4, Lemma 4.3",
                                 "Read by the producer and the auditor; the proofs of Prop. 4.1/4.4 and Lemma 4.3 were re-checked computationally and by hand (AUDIT.md section 2); not formalised",
                                 "taken as stated; the proof of Prop. 3.1 contains a displayed identity that is false for general S (AUDIT.md correction 3), which does not affect the conclusion or the computation")),
        rec("LRI-L-0003", "L", "citation",
            "Premises of the chain to LRC(10) (the conjecture for 11 runners): LRC(9) (10 runners), Trakulthongchai, Electron. J. Combin. 33(2) P2.46; "
            "Lemma 2.6 = Malikiosis-Santos-Schymura Theorem A in the form of Rosenfeld arXiv 2509.14111 Corollary 3: a counterexample has prod u_i < B_k with "
            "B_k = (C(k+1,2)^(k-1) / k)^k, division by k and not k! (confirmed in three texts: Rosenfeld Cor. 3, Trakulthongchai arXiv 2511.22427 C_k, Allikvere arXiv 2609.02604). "
            "With the computation J(10,p) = empty (Tier C) and prod P_10 >= B_10 (Tier A) the chain gives LRC(10), which is S-T's Theorem 1.3 for k = 10: NOT a new result.",
            ["LRI-L-0002"], cite("Trakulthongchai EJC 33(2) P2.46; arXiv:2509.14111; arXiv:2511.22427; arXiv:2609.02604v2",
                                 "Rosenfeld Cor. 3; Trakulthongchai C_k; Allikvere B_k; Malikiosis-Santos-Schymura Thm A (FMS 2025)",
                                 "Formula and check values read by the auditor; ln B_10 = 337.634, S-T Table 1 states '< 338'; with k! it would be 209.6",
                                 "taken as stated; LRC(9) and the MSS bound are not re-derived; the AM-GM step of Cor. 3 was read")),
        # ------------------------------------------------------------------ C
        rec("LRI-C-0001", "C", "argument",
            "Soundness of the producer's own pruning in phase 1 (set-canonical supports; capacity bound; hitting-set branching with sibling exclusion): every class of I(k,p,1) has a "
            "set-canonical member; for distinct x, y in a set-canonical U, fold(y/x) >= u_2; multiplicities travel with the support; the capacity bound is a valid relaxation. "
            "Re-derived by the AI auditor (AUDIT.md section 2b) and checked empirically by three-mode agreement on 56 (k,p) cases and by the auditor's pairwise-lemma-free runs at p = 127, 137.",
            [], arg("C-argument", "mode_agreement.jsonl: 56 (k,p) cases, k = 5..10, 3 modes, 0 disagreements; brute_py.json: 24 cases k = 4..7, 0 disagreements; direct_vs_sieve.json: 14 cases, 0 disagreements.",
                    [LOGS / "mode_agreement.jsonl", LOGS / "brute_py.json", LOGS / "direct_vs_sieve.json", d / "code" / "lr_sieve.c"], "lr_sieve.c; mode_agreement.py; brute_py.py; direct_vs_sieve.py")),
        rec("LRI-C-0002", "C", "argument",
            "Phase 1 and lifts (plan 2,2,2,/) for k = 10 at all 61 primes of P_10 end with exactly one class, the canonical (1,...,10) (only_identity true, identity_survives true); "
            "|S_1| (classes of I(10,p,1)) ranges from 1 to 58,087 (max at p = 137); main pass 3,963 core-s; the unpruned second pass agrees with the main pass at class-hash level "
            "for 33 of 61 primes (127..307) and was stopped. Own-algorithm re-computation by the auditor at p = 127, 137, 263 only; the other 58 primes (incl. 467) rest on the producer's code.",
            ["LRI-C-0001", "LRI-L-0001"],
            arg("C-exact-integer", "summary.json fields k10_all_only_identity true, k10_missing [], k10_nocanon_done 33, k10_nocanon_all_agree true; per-prime outputs data/k10_main/p*.json.",
                [LOGS / "summary.json", d / "result.json"], "lr_sieve (gcc -O3), driver.py, analyze.py")),
        rec("LRI-C-0003", "C", "argument",
            "The level-11 fibre over (1,...,10) is (10,p,11)-proper at all 61 primes of P_10: fiber_check enumerates all 2,593,742,461 vectors w in (Z_11)^10 up to Z_11^* scaling, "
            "0 improper at each prime (158,218,290,121 vectors in all); cross-check by the generic x11 lift at p = 127 (25,937,424,601 lifts, 0 survivors). "
            "Together with LRI-C-0002 this gives J(10,p) = empty without Proposition 1.4. Independent: the auditor's own fibre program at p = 127, 137, 263, 467 (0 improper), "
            "exhaustive S-T Prop. 4.1 for k = 10 (15,937,424,600 vectors, 0 failures) and the Lemma 4.3 inclusion at all 61 primes.",
            ["LRI-C-0002"],
            arg("C-exact-integer", "summary.json k10_all_fiber11_zero true; data/k10_fiber11/p*.json; logs/probe_k10_p127_x11.json; logs/lemma43_check.json.",
                [LOGS / "summary.json", d / "k10_fiber11" / "p467.json", LOGS / "probe_k10_p127_x11.json", LOGS / "lemma43_check.json", d / "code" / "fiber_check.c"],
                "fiber_check (gcc -O3), lemma43_check.py")),
        rec("LRI-C-0004", "C", "argument",
            "What the independent AI auditor recomputed with its own code and different algorithms: phase 1 + lifts at p = 127, 137, 263 (identical class counts and hashes at every level, "
            "S1 = 8,228 / 58,087 / 17; unpruned at 127 and 137); all 214 positive-control cases k = 3..8, with and without the pairwise lemma (214/214 identical); level-11 fibre at p = 127, 137, 263, 467 "
            "(+53, 97): 0 improper; S-T Prop. 4.1 exhaustive; Lemma 4.3 at all 61 primes; no-symmetry brute force I(4,13,5) = empty over 12,960,000 ordered tuples. "
            "NOT done: its own phase 1 at the other 58 primes (p = 467 infeasible, stopped at 1,898 s).",
            ["LRI-C-0003"],
            arg("C-audit-report", "AUDIT.md section 2 (auditor's scratch in /tmp/lrindaudit, not shipped).", [PAPER / "AUDIT.md"], "aud_sieve.c, aud_fiber.c, prop41.c, lemma43.py, brute_I.py (auditor)")),
        rec("LRI-C-0005", "C", "argument",
            "Controls, run before the headline: positive, per-prime verdict patterns for k = 3..8 against Rosenfeld and Trakulthongchai (column 'I(k,p,l_final) = empty at the tested level'; "
            "k = 4, p = 13 flag withdrawn: Rosenfeld section 7 is hedged and makes no claim about 13, brute force I(4,13,5) = empty, controls_ok true); "
            "negative, planted mutations MUT=1 ('<' to '<=') and MUT=2 (floor for ceil) change the counts at k = 7, 8 and MUT=2 removes the identity at k = 10, "
            "both inert at the level-11 step, which has no mutation switch; the strict '>' control at p = 127, L = 11 flags exactly the identity orbit w = -(1..10); "
            "nonzero fibre counts agree in two independent programs (p = 13: 54,976; p = 23: 7,210); L = 5, 7 survivor control.",
            ["LRI-C-0002"],
            arg("C-exact-integer", "data/controls_pos/*, data/controls_neg/*, logs/summary.json (positive_controls, negative_control_mutations, negative_control_fiber).",
                [LOGS / "summary.json", d / "controls_neg" / "k10_p127_mut2.json", d / "controls_neg" / "fiber_k10_p467_L5.json", d / "controls_pos" / "k4_p13.json"],
                "lr_sieve with MUT switch; fiber_check; driver.py")),
        rec("LRI-C-0006", "C", "argument",
            "Comparison with the S-T logs (github.com/vzsky/13-lonely-runners, results/result_11), opened by the auditor only after its own counts at p = 127 and 137: "
            "S-T 'Step 1 (l=1): S size' equals the producer's S1_classes at all 61 primes, 0 disagreements; their log reports 'Subproof Mod p Done' for all 61. "
            "Later sizes are not comparable (S-T remove the identity before lifting). The producer did not read the repository (attestation, not verifiable by the auditor).",
            ["LRI-C-0002"],
            arg("C-audit-report", "AUDIT.md section 5; result.json st_repository_read false with sha256 of every producer file recorded before any such reading.",
                [PAPER / "AUDIT.md", d / "result.json"], "none (comparison by the auditor)")),
        rec("LRI-C-0007", "C", "argument",
            "Optional premise re-run (a check, not a derivation): lr_sieve 9 p 2,5 gives an empty final set at all 47 primes of Trakulthongchai's S_9 (137..401), 214 core-seconds. "
            "LRC(9) remains a literature premise; the re-run was not audited.",
            [], arg("C-exact-integer", "summary.json k9_S9 done 47 of 47, all_empty true; data/k9_S9/.", [LOGS / "summary.json"], "lr_sieve")),
        rec("LRI-C-0008", "C", "argument",
            "HEADLINE. J(10,p) = empty for every one of the 61 primes p in P_10 = {127,...,467} (exact integer arithmetic, exhaustive enumeration; the Proposition 1.4 step of S-T is replaced by a direct "
            "level-11 fibre computation), by an independently written implementation, independently AI-audited. This is a replication of S-T's computational input for k = 10, NOT a new theorem. "
            "With the Tier L premises LRC(9), the MSS/Rosenfeld bound B_k and S-T Cor. 2.5 / Prop. 2.7, and prod P_10 >= B_10 (Tier A, LRI-A-0001), the chain gives LRC(10), the conjecture for "
            "11 runners (k = 10 moving speeds plus the stationary runner), i.e. S-T's Theorem 1.3 for k = 10; the lonely runner conjecture in general is open. "
            "Filed C because the enumeration is not kernel-checked.",
            ["LRI-C-0002", "LRI-C-0003", "LRI-C-0005", "LRI-A-0001", "LRI-L-0001", "LRI-L-0002", "LRI-L-0003"],
            arg("C-assembly", "Assembly of the enumeration (C), the scalar Lean inputs (A) and the literature chain (L) as in Sections 3 and 4 of the paper.",
                [d / "result.json", d / "RESULT.md"], "none")),
        # ------------------------------------------------------------------ X
        rec("LRI-X-0001", "X", "numeric",
            "NOT run or not complete: pytest tests/ (not run); the repository guards antigravity_guard.py and test_rigor_guard.py exit 1 on pre-existing files elsewhere in the repository and flag no LR-IND file (logs/guard_*.txt); "
            "the unpruned producer pass (33 of 61 primes); the auditor's own phase 1 at 58 of 61 primes; any formalisation of J(10,p) = empty. Recorded so the absences are explicit.",
            [], num([LOGS / "guard_antigravity.txt", LOGS / "guard_test_rigor.txt"], "guard transcripts of the producer; they contain no claim about this paper")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
