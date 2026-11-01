"""Build the Elenchus claim ledger for the E3 low-dissipation zeta-monotonicity paper (papers/p4_low_dissipation_zeta).

Modelled on papers/p4_carbon_impulse_response/ledger/build_ledger.py. Tier discipline (tools/ledger.py): a claim may not
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
RES = DATA / "data"
CODE = DATA / "code"
AUD = DATA / "audit_scripts"
AUDLOG = DATA / "audit_logs"
TOOLCHAIN = ("Lean 4.34.1 + Mathlib d13f23b7 through scripts/certified_numerics/lean_pinned.py (imports Mathlib.Tactic and "
             "Mathlib.Analysis.SpecialFunctions.Pow.Real; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]
STATUS = ("AI-audited (AUDIT.md, a different AI agent instance, not a person); producer compile + leanchecker replay rc 0 on Core, Instances, Engine "
          "(data/logs/leanchecker_replay.json); the auditor recompiled all five files into a fresh olean directory (Core 14.1 s, Instances 6.7 s, Engine 400.8 s, "
          "rc 0) and replayed leanchecker (rc 0 on Core, Instances, Engine; rc 1 on a nonexistent module) (data/audit_logs/build.log); NO human audit of statement adequacy, NO statement lock")
AI_AUDIT = {"auditor": "independent AI audit agent (separate instance, producer != verifier), 2026-11-01", "human": False,
            "report": "papers/p4_low_dissipation_zeta/AUDIT.md", "verdict": "ACCEPT_WITH_CORRECTIONS",
            "scope": "own clean recompile of Core, Instances, Engine, Axioms, Controls with #print axioms (27/27 whitelisted), own leanchecker replay, escape-hatch grep "
                     "(only planted controls and one set_option maxHeartbeats 3000000 on engine_bound), Controls caught by the axiom gate, reading of hypotheses for vacuity",
            "not_scope": "statement adequacy not certified by a person; the lemma 'engine with asymmetry zeta implies eta/eta_C <= etaPlus(zeta)' is not in Lean; "
                         "Eq. (13) = root form is symbolic + numerical, not in Lean; P~=0 and Mh=0/Mc=0 not formalised; no Lean instance of engine_bound's hypotheses",
            "note": "AI audit, not a person: the gate field audit is left null so LEDGER_UNAUDITED_TIER_A stays open; no statement lock"}
SRC_COMMIT = "b6dad99c428e53a7ae5492d915d4b95630245538"


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


def axiom_lines(path: Path, names: list[str]) -> list[str]:
    lines: list[str] = []
    text = path.read_text()
    for n in names:
        hit = [ln.strip() for ln in text.splitlines() if ln.strip().startswith(f"'{n}'")]
        if len(hit) != 1:
            raise SystemExit(f"axiom line missing or duplicated for {n}")
        lines.append(hit[0])
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
    ax = AUDLOG / "Axioms.txt"
    core = ["LowDissE3.G_eq", "LowDissE3.qA_pos", "LowDissE3.qB_nonneg", "LowDissE3.qC_pos", "LowDissE3.wPlus_root", "LowDissE3.wPlus_nonneg",
            "LowDissE3.root_lt_one", "LowDissE3.G_strict_mono_zeta", "LowDissE3.G_sub", "LowDissE3.root_strict_anti", "LowDissE3.root_unique",
            "LowDissE3.etaPlus_strictMono", "LowDissE3.etaPlus_mono", "LowDissE3.etaPlus_one", "LowDissE3.etaPlus_le_one_value", "LowDissE3.eq1_of_P",
            "LowDissE3.inst_root_neg", "LowDissE3.inst_root_pos", "LowDissE3.inst_eta_neg", "LowDissE3.inst_eta_pos", "LowDissE3.pert_root_at_neg",
            "LowDissE3.pert_root_at_pos", "LowDissE3.pert_roots_increase", "LowDissE3.pert_eta_not_mono", "LowDissE3.esposito_sandwich"]
    eng = ["LowDissE3.cs2", "LowDissE3.engine_bound"]
    c = [
        rec("LD-A-0001", "A", "lean_axioms",
            "LowDissE3.Core and Instances, for 0<c<1, 1<K, zeta in [-1,1], with etaPlus c K zeta := (1 - wPlus^2)/c and wPlus the explicit positive root of the quadratic "
            "G(w) = K(w^2-(1-c)) - c((1-zeta)+(1+zeta)w)^2/4: etaPlus_strictMono (zeta1<zeta2 implies etaPlus zeta1 < etaPlus zeta2, strict, whole box; elementary: a root of a quadratic "
            "moves monotonically with a parameter in which the quadratic is monotone); supporting lemmas wPlus_root, root_unique, root_strict_anti; etaPlus_one = (K-1)/(K-c); "
            "etaPlus_le_one_value; eq1_of_P (Eq. (1) of Ma et al. for the root form, P~ in (0,1]); esposito_sandwich (positive control at P~=1: 1/2 <= etaPlus <= 1/(2-c)); "
            "exact-rational instances (c=48/49, K=2: roots 5/7, 1/5; eta 1/2, 49/50) and pert_eta_not_mono, which only restates the instance values at negated arguments (a weak control). "
            "These state the paper's model THROUGH THE ROOT FORM: that the root form equals Eq. (13) as printed, and that it is the paper's eta~+, is outside Lean (LD-C-0001, LD-C-0002).",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": axiom_lines(ax, core), "allowlist": ALLOW,
                 "compile_transcript": fref(ax), "producer_axioms_json": fref(LOGS / "lean" / "axioms.json"),
                 "sources": [fref(LEAN / "Core.lean"), fref(LEAN / "Instances.lean"), fref(LEAN / "Axioms.lean")],
                 "leanchecker_replay": fref(LOGS / "leanchecker_replay.json"), "auditor_recompile": fref(AUDLOG / "build.log"), "status": STATUS,
                 "statement_adequacy": "not audited by a person; Core.lean sha256 b69a97be...2b5, Instances.lean 4a3876ce...1f1 match result.json"}),
        rec("LD-A-0002", "A", "lean_axioms",
            "LowDissE3.Engine: engine_bound (with cs2, Cauchy-Schwarz in Engel form) for every engine of the paper's Eqs. (3)-(4) with a=sqrt(Mh)>0, b=sqrt(Mc)>0, q>0, 0<c<1, th,tc>0, P>0 and positive "
            "hot-bath heat (q/c - a^2/th > 0), Pt q^2 = 4(a+b)^2 P: eta/eta_C + (1-c)Pt/(2(1+sqrt(1-Pt)) - c Pt) <= 1 (Eq. (1)), with no zeta and without Eq. (13). "
            "This is a machine check of a KNOWN result (analytic proofs: Ma & Fu arXiv:2411.03849 App. B; Zhai arXiv:2605.02732); only the machine check is new. "
            "One declaration uses set_option maxHeartbeats 3000000 (elaboration budget; leanchecker rc 0). No Lean instance of the hypotheses exists (non-vacuity is numerical, LD-X-0001).",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN, "axiom_output": axiom_lines(ax, eng), "allowlist": ALLOW,
                 "compile_transcript": fref(ax), "producer_engine_compile": fref(LOGS / "lean" / "engine.json"),
                 "sources": [fref(LEAN / "Engine.lean")],
                 "leanchecker_replay": fref(LOGS / "leanchecker_replay.json"), "auditor_recompile": fref(AUDLOG / "build.log"), "status": STATUS,
                 "statement_adequacy": "not audited by a person; Engine.lean sha256 30ac26ba...1e1 matches result.json; hypotheses read against Eqs. (3)-(4) by the auditor"}),
        rec("LD-A-0003", "A", "lean_axioms",
            "Lean controls: Controls.lean (never to be imported) compiles with rc 0 but its axiom audit reports sorryAx for LowDissE3.ctl_sorry and the smuggled axiom LowDissE3.ctl_cheat for "
            "LowDissE3.ctl_axiom, which a compile exit code alone would accept; the auditor reproduced both. A leanchecker run on a missing module exits 1.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(AUDLOG / "Controls.txt", ["LowDissE3.ctl_sorry", "LowDissE3.ctl_axiom"]), "allowlist": ALLOW,
                 "compile_transcript": fref(AUDLOG / "Controls.txt"), "producer_controls": fref(LOGS / "lean" / "controls.txt"),
                 "sources": [fref(LEAN / "Controls.lean")], "leanchecker_replay": fref(LOGS / "leanchecker_replay.json"), "status": STATUS,
                 "statement_adequacy": "not audited by anyone; the controls are meant to fail the gate"}),
        # ------------------------------------------------------------------ L
        rec("LD-L-0001", "L", "citation",
            "Ma, Xu, Dong, Sun, arXiv:1802.09806v4 (Phys. Rev. E 98, 042112 (2018)), 'Universal constraint for efficiency and power of a low-dissipation heat engine': low-dissipation model Q_x = Q_x^(r) - M_x/t_x (Eq. 2), "
            "P and eta (Eqs. 3-4), Eq. (1) universal bound, eta~+ over th+tc = tau+ (Eqs. 10-11), Eq. (13) closed form, asymmetry zeta (Eq. 14), 'it is not a supremum for all the P~' (p. 3), "
            "Appendix B: 'the analytical proof of its monotonicity is tedious and difficult. Instead numerical calculate the derivative'.",
            [], cite("Ma, Xu, Dong, Sun arXiv:1802.09806v4", "Eqs. (1)-(4), (10)-(14), Appendix B (pp. 1-3, 7)",
                     "Read from the PDF page images by the producer and by the independent AI auditor (AUDIT.md section 1); the square-root vinculum of Eq. (13) ends after '+ 1 - eta_C'",
                     "taken as stated; third-party PDF not redistributed; arXiv identifier and PRE reference resolved on export.arxiv.org 2026-11-01")),
        rec("LD-L-0002", "L", "citation",
            "Ma & Fu, arXiv:2411.03849 (Phys. Rev. E 112, 054130 (2025)), 'Unified approach to power-efficiency trade-off relations of generic thermal machines', Appendix B: analytic proof (sign of "
            "d eta~+/d delta) that their upper bound increases in the dissipation ratio delta in [0,1]; at delta = 1 it is Eq. (1) of Ma et al. 2018. Their family is a different interpolation: it agrees with "
            "the root form at zeta = -1 (delta=0) and zeta = 1 (delta=1) but differs in between (max 0.038 under delta=(1+zeta)/2; 0.40 and 0.055 under two other natural maps; auditor script mafu_cmp.py).",
            [], cite("Ma & Fu arXiv:2411.03849", "Appendix B, Eqs. (B6), (14)", "Read by the independent AI auditor via alphaXiv (AUDIT.md section 5); not re-read by this paper's writer",
                     "taken as stated; arXiv identifier and journal reference resolved on export.arxiv.org 2026-11-01")),
        rec("LD-L-0003", "L", "citation",
            "Zhai, arXiv:2605.02732 (2026), 'Geometric Formulation of Power-Efficiency Bounds in Carnot-like Engines': re-derives Eq. (1) by a short geometric / linear-programming argument (as reported in AUDIT.md section 5). "
            "Zhai, Yue, Sun, arXiv:2509.07721, 'Exact bound of power-efficiency trade-off in finite-time thermodynamic cycles': state that Ma et al. 2018 already rigorously proved the Holubec-Ryabov conjecture and give an exact, tighter bound.",
            [], cite("Zhai arXiv:2605.02732; Zhai, Yue, Sun arXiv:2509.07721", "abstracts / main results as summarised in AUDIT.md section 5",
                     "Read by the independent AI auditor via alphaXiv; the paper's writer verified only that both identifiers exist with these titles and authors (export.arxiv.org 2026-11-01)",
                     "taken as stated at the level of the audit's summary")),
        rec("LD-L-0004", "L", "citation",
            "Holubec & Ryabov, arXiv:1603.02551 (J. Stat. Mech. (2016) 073204), 'Maximum Efficiency of Low-Dissipation Heat Engines at Arbitrary Power': their Eq. (34) upper bound equals Eq. (1); derived "
            "analytically only near P~ = 0 and P~ = 1, numerical evidence in between (read by the auditor). Ye & Holubec 2021 (arXiv:2112.08923) concerns heat pumps, not relevant. "
            "Esposito et al. 2010 (efficiency at maximum power bounds eta_C/2 <= eta* <= eta_C/(2-eta_C)) was NOT re-read; only used as the positive control at P~=1.",
            [], cite("Holubec & Ryabov arXiv:1603.02551", "Eq. (34) and the surrounding derivation (as read by the auditor)",
                     "Read by the independent AI auditor; Esposito 2010 and Ye-Holubec 2021 not re-read by the producer or this paper",
                     "taken as stated; arXiv identifier resolved on export.arxiv.org 2026-11-01")),
        # ------------------------------------------------------------------ C
        rec("LD-C-0001", "C", "argument",
            "Hand derivation of the root form from the paper's model (code/derivation.md steps 1-4, with step 3 as corrected by audit correction 6): eta = u c, w = sqrt(1-eta); q(1-u) = w^2 a^2/th + b^2/tc; "
            "Cauchy-Schwarz gives q(1-u) tau+ >= (wa+b)^2 on th+tc <= tau+, with q tau+ = K M, K = 2/(1-sqrt(1-P~)); eta~+ is the largest u for which this holds, i.e. the MAXIMUM of eta over th+tc = tau+, "
            "an upper bound at power P that is not attained in general (the efficiency Cauchy-Schwarz equality needs th/tc = w a/b, the power equality th/tc = a/b); G(w,zeta) = K(w^2-(1-c)) - c((1-zeta)+(1+zeta)w)^2/4 "
            "is a convex quadratic with G(0)<0, so the feasible set is w >= w+ and eta~+/eta_C = (1-w+^2)/c. Checked independently by the auditor (AUDIT.md section 1). Not in Lean.",
            ["LD-L-0001"], arg("C-argument", "code/derivation.md (producer text; step 3 superseded by the paper's Section 3); AUDIT.md section 1 (independent derivation).",
                               [CODE / "derivation.md", PAPER / "AUDIT.md"], "hand derivation, re-derived by the auditor")),
        rec("LD-C-0002", "C", "argument",
            "Eq. (13) as printed equals the root form. Symbolic (sympy, auditor): eliminating w from the tangency equality by squaring twice gives a quadratic R(u)=0; R(u13(x)) reduces to 0 modulo x^2 - radicand, "
            "so both sign branches of Eq. (13) are exact roots of R once square roots are squared away (an identity). Branch selection numerical (mpmath, 50 digits, 5000 random (c,P~,zeta)): the + branch matches "
            "the root form to 5.0e-48, the - branch is off by up to 0.47, the 'term inside the root' misreading by up to 0.23; minimum radicand 2.0e-3 > 0. Producer: 3000 random points at 60 digits, max |difference| 1.6e-58. "
            "None of this is in Lean; the branch choice is numerical only. The producer's preregistered transcription of Eq. (13) was wrong (the term -((1+zeta)/4) eta_C (1-sqrt(1-P)) put inside the root); "
            "the original disagreement (up to 0.23) is kept in logs/link_first_transcription.log.txt.",
            ["LD-L-0001", "LD-C-0001"], arg("C-symbolic-numeric", "audit_scripts/sym_audit.py (sympy + mpmath, auditor); code/link.py, code/sym.py and logs/link.log (producer).",
                                            [AUD / "sym_audit.py", CODE / "link.py", CODE / "link_funcs.py", CODE / "sym.py", LOGS / "link.log", LOGS / "link_first_transcription.log", LOGS / "sym.log"],
                                            "sympy remainder; mpmath 50/60 digits")),
        rec("LD-C-0003", "C", "argument",
            "Controls, run before the headline: P1 Esposito sandwich (Lean + numerics: exact 1/2 and 1/(2-c) at P~=1); P2 exact rational instance (roots 5/7, 1/5); P3 Eq. (13) transcription agreement after the correction; "
            "N1 perturbed factor (zeta -> -zeta): perturbed roots increase, perturbed eta decreases 49/50 -> 1/2, grid 15,200/15,200 pairs non-increasing (the Lean pert_eta_not_mono only restates instance values, a weak control); "
            "N2 B sign flipped (5,920 bad pairs), K halved (611), C sign flipped (13,256, 558 undefined): all caught, true formula 0; N3 planted sorry and axiom caught by the axiom gate (LD-A-0003); "
            "N4 mistyped Eq. (13) (sign of zeta inside the root) differs by up to 0.156; perturbed Eq. (1) (1-c -> 1+c) violated by 11,522 of 17,355 random engines (auditor: 20,112 of 53,021).",
            ["LD-A-0001"], arg("C-controls", "logs/link.log, logs/numerics2.log, data/numerics2.json, Instances.lean, audit_scripts/num_audit.py.",
                               [LOGS / "link.log", LOGS / "numerics2.log", RES / "numerics2.json", AUD / "num_audit.py"], "link.py; numerics2.py; num_audit.py")),
        rec("LD-C-0004", "C", "argument",
            "HEADLINE (model-conditional, elementary). In the phenomenological low-dissipation Carnot model (Eqs. (2)-(4)), with the paper's eta~+ defined by the root form of the tangency quadratic: "
            "(i) eta~+ is strictly increasing in the asymmetry zeta on the whole box 0<c<1, K>1, zeta in [-1,1] (Lean, Tier A pending statement lock; the paper's Appendix B checked it only numerically; "
            "no analytic proof of the zeta-monotonicity of Eq. (13) found in the literature search, which was not systematic); (ii) Eq. (1) holds for every engine of Eqs. (3)-(4) (Lean machine check of a known result). "
            "NOT proved: that eta~+ is attained, or that every engine with asymmetry zeta has eta/eta_C <= etaPlus(zeta) (derivation + numerics only). "
            "The identification etaPlus = Eq. (13) is outside Lean. No device or power-plant claim.",
            ["LD-A-0001", "LD-A-0002", "LD-C-0001", "LD-C-0002", "LD-C-0003", "LD-L-0001", "LD-L-0002", "LD-L-0003", "LD-L-0004"],
            arg("C-assembly", "Assembly of the Lean theorems (A), the derivation and symbolic link (C) and the literature (L) as in Sections 3-6 of the paper.",
                [DATA / "result.json", DATA / "RESULT.md", PAPER / "AUDIT.md"], "none")),
        # ------------------------------------------------------------------ X
        rec("LD-X-0001", "X", "numeric",
            "Float / high-precision scans, not proofs: root-form monotonicity grid 124,800 consecutive-zeta pairs at 60 digits (producer), 0 non-increasing; auditor 336,200 pairs "
            "(41 c x 41 P~ x 201 zeta, mpmath 40 digits), 0 non-increasing, smallest increment 1.25e-12; E3x implicit-differentiation grid of 801,900 points: d etaPlus/d zeta > 0, minimum 1.2e-5, maximum 0.34; "
            "17,355 random exact-rational engines (producer) and 53,021 random engines (auditor) with 0 violations of Eq. (1) and 0 violations of eta/eta_C <= etaPlus(zeta) (max LHS of Eq. (1) 0.99999091, so the bound is nearly attained); "
            "the root form is a valid upper bound, NOT attained in general, on a brute-force float optimum of the engine at exactly given power (producer 8 points, root - brute in [4.8e-7, 2.2e-3]; "
            "auditor 8 other points, [1.3e-5, 6.6e-3]; all >= 0). The 53,021 engines are the only evidence that engine_bound's hypotheses are satisfiable.",
            [], num([RES / "numerics2.json", LOGS / "numerics2.log", AUD / "num_audit.py", LOGS / "diag.log"], "float and mpmath outputs; they support no claim by themselves")),
        rec("LD-X-0002", "X", "numeric",
            "NOT done or not establishable here, recorded so the absences are explicit: statement lock for the Lean statements; human audit; Lean proof of the lemma 'engine with asymmetry zeta implies eta/eta_C <= etaPlus(zeta)' "
            "(short: Cauchy-Schwarz => G(w,zeta) >= 0 => w >= wPlus via root_unique / convexity); Lean proof that Eq. (13) equals the root form; the + branch choice is numerical only; P~=0 and the endpoints Mh=0 / Mc=0 not formalised; "
            "a Lean example that engine_bound's hypotheses can be met; Esposito et al. 2010 not re-read; a systematic literature search; ordering of the preregistration against the work (hash matches).",
            [], num([DATA / "prereg_E3.json", DATA / "prereg_E3.sha256"], "preregistration file and its hash; they contain no claim about this paper's results")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
