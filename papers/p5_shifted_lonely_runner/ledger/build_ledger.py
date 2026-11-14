"""Build the Elenchus claim ledger for the SLR-18 paper (papers/p5_shifted_lonely_runner).

Modelled on papers/p5_lonely_runner_ind/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not be filed above
anything in its depends_on, and the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
An independent AI audit exists (AUDIT.md, ACCEPT_WITH_CORRECTIONS, not a person): Tier A rows carry an ai_audit field and the gate
field audit stays null, so LEDGER_UNAUDITED_TIER_A remains open (exit 1 is the honest state).
Run:  python3 -I build_ledger.py     (standard library only)
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAPER = HERE.parent
EV = HERE / "evidence"
DATA = PAPER / "data"
LEAN = DATA / "lean"
LOGS = DATA / "logs"
GATE = LOGS / "lean_gate"
REPO = PAPER.parent.parent
TOOLCHAIN = ("Lean 4.34.1 + Mathlib d13f23b7 through scripts/certified_numerics/lean_pinned.py (modules import "
             "Mathlib.Tactic; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("Tier A pending a statement lock. Auditor (a different AI agent instance): lean_pinned.py compile + #print axioms for all 34 files n=5..38, rc 0 (AUDIT.md 2c); "
          "ours: lean_pinned.py compile with olean, anse/formal/lean_runner.py file-mode gate (lean_cmd = the pinned toolchain) and leanchecker rc 0 on n=18 and n=38. "
          "NO human audit of statement adequacy, NO statement lock")
AI_AUDIT = {"auditor": "independent AI audit agent (separate instance, producer != verifier), 2026-10-31", "human": False,
            "report": "papers/p5_shifted_lonely_runner/AUDIT.md", "verdict": "ACCEPT_WITH_CORRECTIONS",
            "scope": "own generator gen_lean.py (untrusted) + own compile of all 34 files with lean_pinned.py and #print axioms; escape-token grep; positive control (n=5) and tampered control (rc 1)",
            "not_scope": "anse/formal/lean_runner.py and a statement lock were NOT run by the auditor; statement adequacy (the Lean statement means the BCS Conj. 1.1(ii) counterexample its gloss claims) not certified by a person",
            "note": "AI audit, not a person: the gate field audit is left null so LEDGER_UNAUDITED_TIER_A stays open; no statement lock"}
SRC_COMMIT = "1e29c538f2ceacd0e644fc990cfba32ce45fa0d7"


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


def axiom_lines(text: str) -> list[str]:
    return [" ".join(ln.split()) for ln in text.splitlines() if "depends on axioms" in ln or "does not depend on any axioms" in ln]


def gate(name: str) -> dict:
    return json.loads((GATE / f"gate_{name}.json").read_text())


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
    g18, g38, gp1, gneg = gate("N18"), gate("N38"), gate("P1"), gate("P1neg")
    for g in (g18, g38, gp1):
        assert g["compile"]["rc"] == 0 and g["leanchecker"]["rc"] == 0
        assert all(r["compiled_successfully"] and not r["has_sorry"] and not r["untrusted_axioms"] for r in g["lean_runner_verify_file"])
    assert gneg["compile"]["rc"] != 0
    summ = json.loads((LEAN / "lean_all_summary_auditor.json").read_text())
    assert len(summ) == 34 and all(r["rc"] == 0 and not r["banned_tokens"] for r in summ)
    lit = json.loads((LOGS / "lean_literal_check.json").read_text())
    assert lit["all_ok"] and lit["files"] == 34

    c = [
        rec("SLR-A-0001", "A", "lean_axioms",
            "Lean covering statements, re-run by us for the sample n = 18 and n = 38 (SLRN18.lean, SLRN38.lean; Programmes/SLR18): for the typed v : Fin n -> N and s : Fin n -> Q (the "
            "certificate's a_i/D), v is injective (v_injective), positive (v_pos) and for every real t there are i and an integer k with "
            "|s_i + v_i t - k| < 1/(n+1) (cover), i.e. the negation of the conclusion of BCS Conj. 1.1(ii) for this (v, s). "
            "Gates: lean_pinned.py compile with olean rc 0; anse/formal/lean_runner.py verify_file (lean_cmd = pinned toolchain) clean for all 3 theorems at both n; leanchecker rc 0 on both modules. "
            "Axioms: cover, v_injective use propext, Classical.choice, Quot.sound; v_pos uses propext. The statement says nothing about gamma, compactness or the literature.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(g18["compile"]["output"]) + axiom_lines(g38["compile"]["output"]), "allowlist": ALLOW,
                 "compile_transcript": fref(GATE / "gate_N18.json"), "axiom_transcript": fref(GATE / "gate_N38.json"),
                 "sources": [fref(LEAN / "SLRN18.lean"), fref(LEAN / "SLRN38.lean")],
                 "leanchecker_replay": {"N18": g18["leanchecker"], "N38": g38["leanchecker"]},
                 "lean_runner": {"N18": [{"theorem": r["theorem_name"], "axioms": r["axioms"], "clean": r["compiled_successfully"] and not r["has_sorry"] and not r["untrusted_axioms"]} for r in g18["lean_runner_verify_file"]],
                                 "N38": [{"theorem": r["theorem_name"], "axioms": r["axioms"], "clean": r["compiled_successfully"] and not r["has_sorry"] and not r["untrusted_axioms"]} for r in g38["lean_runner_verify_file"]]},
                 "status": STATUS,
                 "statement_adequacy": "not audited by a person; the literals v and s equal the certificate JSON and the statement is the template (data/logs/lean_literal_check.json, SLR-C-0004)"}),
        rec("SLR-A-0002", "A", "lean_axioms",
            "The same covering statement for all 34 certificates n = 5..38 (21 new: n = 18..38; 13 controls: n = 5..17), compiled by the AUDITOR (not by us, except n = 18 and 38 in SLR-A-0001): "
            "34/34 rc 0, no banned token, cover and v_injective depend on propext, Classical.choice, Quot.sound and v_pos on propext (3456 s on one core). "
            "Only the pinned lean_pinned.py compile plus manual #print axioms; NOT anse/formal/lean_runner.py, NOT a statement lock.",
            ["SLR-A-0001"], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": [ln for r in summ for ln in r["axioms"]], "allowlist": ALLOW,
                 "compile_transcript": fref(LEAN / "lean_all_summary_auditor.json"),
                 "sources": [fref(LEAN / "SLRN18.lean"), fref(LEAN / "SLRN38.lean"), fref(LEAN / "gen_lean.py")],
                 "status": STATUS + "; the other 32 files are the auditor's run only (per-n transcripts in data/lean/auditor_transcripts/)",
                 "statement_adequacy": "not audited by a person"}),
        rec("SLR-A-0003", "A", "lean_axioms",
            "Lean controls: the positive control SLRP1.lean (n = 5, v = (1..5), s = (0,46,38,47,72)/94, delta = 1/6) compiles rc 0 with standard axioms through the same gates "
            "(lean_pinned.py, lean_runner file-mode, leanchecker); the tampered file SLRP1neg.lean (delta = 15/94 = the exact gamma, so no cover) is rejected by the kernel (rc non-zero, "
            "linarith fails), as it must be.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(gp1["compile"]["output"]), "allowlist": ALLOW,
                 "compile_transcript": fref(GATE / "gate_P1.json"),
                 "rejections": [fref(GATE / "gate_P1neg.json")],
                 "sources": [fref(LEAN / "SLRP1.lean")], "leanchecker_replay": gp1["leanchecker"], "status": STATUS,
                 "statement_adequacy": "not audited by a person"}),
        # ------------------------------------------------------------------ L
        rec("SLR-L-0001", "L", "citation",
            "Definition of the shifted lonely runner conjecture as pinned by the auditor from the sources: BCS arXiv 2603.24784 v4 Conj. 1.1(ii) (for distinct |v_i| and every s there is t with dist(s_i + v_i t, Z) >= 1/(n+1) for all i) "
            "and Def. 1.3 (gamma, gamma_sh); Zhang arXiv 2608.13599 v3 App. A and Question 8.5; Poliakova arXiv 2609.23952 v1 Sec. 1 (1/(n+1+E_n) = inf gamma). "
            "Consequence: gamma(v;s) < 1/(n+1) iff the OPEN arcs cover the circle (maximum attained); integer positive v and rational s lose no generality for counterexamples.",
            [], cite("arXiv:2603.24784v4; arXiv:2608.13599v3; arXiv:2609.23952v1", "BCS p.2, p.3, Def. 1.3; Zhang App. A, Q. 8.5, p.19; Poliakova Sec. 1, Thm 2, p.3",
                     "As read on alphaXiv by the independent AI auditor (AUDIT.md section 1), not taken from the producer", "taken as stated")),
        rec("SLR-L-0002", "L", "citation",
            "Prior results: the shifted conjecture is proved for n <= 4 (Alcantara-Criado-Santos; BCS Remark 1.2); it fails for n = 5..17 (BCS Prop. 5.14, as cited by the producer; BCS Table 2 gives exact gamma_sh(1..n) for n <= 15) "
            "and for every n >= 95 (Poliakova Thm 2, E_n >= 1); Zhang and Poliakova call 18 <= n <= 94 open (v3 of 18 Oct 2026; v1); BCS v4 (24 Oct 2026) states failure only for n = 5..17. "
            "Hence, with this paper, failure is known for n in 5..38 and n >= 95; n in 39..94 is open.",
            ["SLR-L-0001"], cite("arXiv:2603.24784v4; arXiv:2609.23952v1; arXiv:2608.13599v3", "BCS Rem. 1.2, Table 2, Props. 5.11/5.12/5.14; Poliakova Thm 2; Zhang p.19",
                                 "Read by the auditor; Prop. 5.14 as cited by the producer, not separately re-read", "taken as stated; not re-derived")),
        # ------------------------------------------------------------------ C
        rec("SLR-C-0001", "C", "argument",
            "The producer's two checkers accept all 34 certificates n = 5..38 (re-checked from the stored JSON by verify_all.py): checker 1 (slr_exact.py, Python integers, greedy sweep of open integer intervals) "
            "and checker 2 (check_cover.c, __int128, every arc right endpoint strictly inside another arc). Different criteria and languages, SAME author: not independent in authorship.",
            ["SLR-L-0001"], arg("C-exact-integer", "verify_all.json: 34 certificates, both checkers true; controls_run1.json and fuzz_agree.json (2400 tests, 0 mismatches).",
                                [LOGS / "verify_all.json", LOGS / "controls_run1.json", LOGS / "fuzz_agree.json", DATA / "code" / "slr_exact.py", DATA / "code" / "check_cover.c.txt"],
                                "slr_exact.py; check_cover.c; verify_all.py (producer)")),
        rec("SLR-C-0002", "C", "argument",
            "The auditor's third checker (audit_check.py, written from scratch, standard library; exact Fractions) accepts all 34 certificates by two methods: A = exact interval subtraction of all open arcs from [0,1] (nothing left), "
            "B = exact gamma(v;s) over all pairwise-crossing and single-peak candidates, gamma < 1/(n+1). Re-run by us: 34/34 valid, both methods COVERED, gamma values identical to the auditor's table. "
            "Exact margins 1/gamma - (n+1) lie in [0.0961, 0.1098] for n = 18..38 (min n = 30, max n = 25), so E_n >= 0.096 (Poliakova's notation) and Gamma(n) < 1/(n+1) for these n; upper bounds only.",
            ["SLR-L-0001"], arg("C-exact-integer", "auditor_checker_rerun.jsonl: per certificate valid, coverA, coverB, gamma (exact fraction), E_lower.",
                                [LOGS / "auditor_checker_rerun.jsonl", DATA / "code_auditor" / "audit_check.py"], "audit_check.py (auditor), re-run by us under python3 -I")),
        rec("SLR-C-0003", "C", "argument",
            "Controls. Producer: P1/P2 reproduce the published exact gamma 15/94 and 2/15; own shifts for [n], n = 5..17, certified; tangency at delta = gamma rejected; [n] with s = 0 never certified (n = 2..94); "
            "<= 14 speeds with s = 0 never certified (3005 instances); single-shift perturbation breaks 0/10 and 0/12 at the published deltas (reported, not hidden) and 4-10 per certificate on new ones. "
            "Auditor: [n], s = 0, n = 2..40, 0/39 covered; BCS gammas 15/94, 2/15, 9/67 reproduced; tangency at n = 5, 18, 29, 38 rejected at gamma and gamma - 1e-12, covered at gamma + 1e-12; invalid inputs flagged; "
            "delta/2 perturbations break 36/36 at n = 18 and 72/76 at n = 38; 0 disagreements between methods A and B; fuzz 400 x 4, 0 mismatches.",
            ["SLR-C-0001", "SLR-C-0002"],
            arg("C-exact-integer", "controls_run1.json, fuzz_agree.json (producer); auditor_adversarial.json (auditor).",
                [LOGS / "controls_run1.json", LOGS / "fuzz_agree.json", LOGS / "auditor_adversarial.json"], "controls.py, fuzz_agree.py (producer); adversarial.py (auditor)")),
        rec("SLR-C-0004", "C", "argument",
            "The 34 generated Lean files are about the certificates: for each n = 5..38 the typed literals v and s equal the certificate JSON (s_i = a_i/D), the cover statement is the template with only n substituted "
            "(delta = 1/(n+1)), v_injective and v_pos are present, the only import is Mathlib.Tactic and no sorry/admit/native_decide/axiom/unsafe/implemented_by occurs. A text check, not a proof; the kernel is the judge of cover.",
            ["SLR-A-0002"], arg("C-exact-integer", "lean_literal_check.json: all_ok true, files 34.", [LOGS / "lean_literal_check.json"], "ledger/check_lean_literals.py (ours)")),
        rec("SLR-C-0005", "C", "argument",
            "HEADLINE. For every n in 18..38 there is an explicit exact certificate (distinct positive integers v_1..v_n, rationals s_i = a_i/D) that is a counterexample of size n to the shifted lonely runner conjecture "
            "(BCS Conj. 1.1(ii)): the open arcs of radius 1/(n+1) cover the circle, gamma(v;s) < 1/(n+1) exactly. Together with the literature the conjecture is known to fail for n in 5..38 and n >= 95; n in 39..94 stays open. "
            "Upper bounds only (Gamma(n) < 1/(n+1); E_n >= 0.096); nothing about the unshifted conjecture; NOT 'fails for all n >= 5'. "
            "Rests on: the Lean covering statements (Tier A pending a statement lock), the definition (L), three exact checkers (two same-author, one independent). Filed C because an assembly argument is capped at C.",
            ["SLR-A-0001", "SLR-A-0002", "SLR-L-0001", "SLR-L-0002", "SLR-C-0001", "SLR-C-0002", "SLR-C-0003", "SLR-C-0004"],
            arg("C-assembly", "Assembly of the three checkers (C), the Lean statements (A) and the literature chain (L) as in Sections 2 to 6 of the paper.",
                [DATA / "result.json", DATA / "RESULT.md", PAPER / "AUDIT.md"], "none")),
        # ------------------------------------------------------------------ X
        rec("SLR-X-0001", "X", "numeric",
            "Floating-point search and its absences: the search (cover_ls.py, cover_ls_fast.c) found certificates n <= 38 and none for n = 39..60 within 29.75 of the 30 core-hour cap "
            "(attempts: n=39 0/23, n=40 0/15, n=41..59 0/12 each, n=60 0/11; n = 61..94 never attempted). This supports no claim about n >= 39. "
            "The 333 raw scratch files logs/fast_tmp/*.txt are omitted from the bundle (not in the hash list of result.json).",
            [], num([DATA / "RESULT.md", LOGS / "manual_runs_ledger.json", LOGS / "swap5_38_94.log"], "search logs of the producer; they contain no claim about validity")),
        rec("SLR-X-0002", "X", "numeric",
            "Scoop check, a recorded search and not a proof of absence: alphaXiv (several recency windows up to published_after 2026-10-24) and web search on 2026-10-28 (producer) and 2026-10-31 (auditor) found no source "
            "settling any n in 18..94; residual risk: arXiv listings after the alphaXiv index, unpublished BCS/Criado computations, private communications. The cited authors have not been contacted.",
            [], num([PAPER / "AUDIT.md", DATA / "RESULT.md"], "AUDIT.md section 3 and RESULT.md novelty section")),
        rec("SLR-X-0003", "X", "numeric",
            "NOT run: anse/formal/lean_runner.py and a statement lock on the 32 files other than n = 18 and n = 38 (the auditor ran lean_pinned.py only); no human audit; pytest tests/ and the repository guards "
            "were not run for this paper. Recorded so the absences are explicit.",
            [], num([LEAN / "lean_all_summary_auditor.json"], "the auditor's summary; the absences are in the text of AUDIT.md section 2c and 6")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
