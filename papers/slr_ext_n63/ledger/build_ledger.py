"""Build the Elenchus claim ledger for the SLR-EXT n=63 paper (papers/slr_ext_n63).

Modelled on papers/p5_shifted_lonely_runner/ledger/build_ledger.py. Tier discipline: a claim may not be filed above anything in
its depends_on; the kind caps the tier (lean_axioms A, citation L, argument C, numeric X).
One Tier A row (SLR63-A-0001, kind lean_axioms): the full Lean recompile of the fixed file passed (rc 0). Gate field audit null, as in the sibling paper.
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
SRC_COMMIT = "3fa606c (HEAD at writing; paper and data uncommitted)"


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
    return {"schema_version": 1, "id": cid, "statement": statement, "tier": tier, "kind": kind,
            "depends_on": depends, "evidence": blob(ev), "audit": None}


def cite(source: str, where: str, text: str, note: str) -> dict:
    return {"kind": "citation", "source": source, "where": where, "text": text, "note": note}


def arg(subtier: str, text: str, files: list[Path], instrument: str) -> dict:
    return {"kind": "argument", "subtier": subtier, "text": text, "files": [fref(f) for f in files],
            "instrument": instrument, "source_commit": SRC_COMMIT}


def num(files: list[Path], note: str) -> dict:
    return {"kind": "numeric", "files": [fref(f) for f in files], "note": note, "source_commit": SRC_COMMIT}


TOOLCHAIN = ("Lean 4.34.1 + Mathlib (partial build) through scripts/certified_numerics/lean_pinned.py (imports "
             "Mathlib.Tactic; no import Mathlib)")
ALLOW = ["propext", "Classical.choice", "Quot.sound"]


def axiom_lines(text: str) -> list[str]:
    return [" ".join(ln.split()) for ln in text.splitlines() if "depends on axioms" in ln or "does not depend on any axioms" in ln]


def main() -> int:
    lean_full = json.loads((DATA / "lean" / "lean_full.json").read_text())
    assert lean_full["rc"] == 0
    lean_second = json.loads((DATA / "lean" / "lean_second.json").read_text())
    assert lean_second["rc"] == 0 and axiom_lines(lean_second["output"]) == axiom_lines(lean_full["output"])
    cert = DATA / "certificates" / "cert_n063.json"
    c = [
        rec("SLR63-A-0001", "A", "lean_axioms",
            "Lean covering statement for the stated n=63 certificate (SLRN63.lean): for the typed v : Fin 63 -> N and s : Fin 63 -> Q (the certificate's a_i/520), v is injective (v_injective), "
            "positive (v_pos) and for every real t there are i and an integer k with |s_i + v_i t - k| < 1/64 (cover). Full compile rc 0 (3327.6 s) through lean_pinned.py (compile + #print axioms); "
            "cover and v_injective depend on propext, Classical.choice, Quot.sound; v_pos on propext; no sorry/admit/native_decide/axiom in the source. First compile failed on v_injective (maxRecDepth), fixed with "
            "set_option maxRecDepth 1000000. A second run of the same compile (same runner, byte-identical regenerated file) also gave rc 0 (2028.2 s), identical axioms; both runs by the main session, not an independent auditor. "
            "Certifies this Lean statement only, not its physical or conjecture-level meaning beyond the stated covering.",
            [], {"kind": "lean_axioms", "toolchain": TOOLCHAIN,
                 "axiom_output": axiom_lines(lean_full["output"]), "allowlist": ALLOW,
                 "compile_transcript": fref(DATA / "lean" / "lean_full.json"),
                 "second_compile_transcript": fref(DATA / "lean" / "lean_second.json"),
                 "sources": [fref(DATA / "lean" / "SLRN63.lean")],
                 "ai_audit": "compiled twice by the main session (same runner, same file); NOT by an independent auditor, NOT through anse/formal/lean_runner.py; not a person",
                 "status": "Tier A with the caveats: not run through anse/formal/lean_runner.py; no LeanMaster statement lock; file made by an untrusted generator (kernel re-checks every case); no person has certified the statement's meaning",
                 "statement_adequacy": "not audited by a person"}),
        rec("SLR63-L-0001", "L", "citation",
            "Definition and prior ranges, taken as stated from the sources: shifted lonely runner conjecture (BCS arXiv:2603.24784 Conj. 1.1(ii)); "
            "distinct positive integer velocities, shifts in R/Z, gamma(v;s)=max_t min_i ||s_i+v_i t||; fails for n=5..17 (BCS) and n>=95 (Poliakova arXiv:2609.23952); "
            "Zhang arXiv:2608.13599 lists the middle range open; earlier note doi:10.5281/zenodo.23842167 covers n=18..38.",
            [], cite("arXiv:2603.24784; arXiv:2609.23952; arXiv:2608.13599; doi:10.5281/zenodo.23842167", "Section 1 of the cited papers",
                     "see statement", "read on alphaXiv by the auditor (2026-11-08); not re-derived")),
        rec("SLR63-C-0001", "C", "argument",
            "Three exact checkers accept cert_n063.json (n=63, 63 distinct positive velocities in 1..128, D=520, delta=1/64): checker 1 slr_exact.py and checker 2 check_cover.c "
            "(producer, same author, COVERED, 3961 endpoints), checker 3 audit63.py (independent AI auditor, exact Fractions/integers: COVERED at 1/64). "
            "Exact gamma = 66/4225 at t = 4291/8450, gap 1/64 - gamma = 1/270400; cover fails at r = gamma and at r = 1/65.",
            ["SLR63-L-0001"],
            arg("C-exact", "Exact integer/rational interval and crossing-candidate computation; the cover criterion is the open-arc criterion of the definition.",
                [cert, DATA / "code" / "slr_exact.py", DATA / "code" / "check_cover.c.txt", DATA / "code_auditor" / "audit63.py",
                 DATA / "code_main" / "verify63.py", DATA / "logs" / "audit63_run.txt", DATA / "logs" / "verify63_run.txt"],
                "Python integers/Fractions, C __int128")),
        rec("SLR63-C-0002", "C", "argument",
            "Controls: positive control Poliakova rule at N=96 (n=95) COVERED by both producer checkers; negative controls: s=0 with [63] rejected, duplicated velocity rejected, "
            "cert not covered at radius 1/65, perturbation by +-1/(2D) breaks 83 of 126 (auditor), +-1/(10 sum v) breaks 3 of 126 (producer).",
            ["SLR63-C-0001"],
            arg("C-controls", "Controls executed with the same checkers.",
                [DATA / "logs" / "final_checks.json", DATA / "logs" / "controls_run.log", DATA / "logs" / "audit63_run.txt"],
                "same checkers as SLR63-C-0001")),
        rec("SLR63-C-0003", "C", "argument",
            "HEADLINE. The shifted lonely runner conjecture (BCS Conj. 1.1(ii)) fails at n = 63: explicit exact certificate, gamma(v;s) = 66/4225 < 1/64, so E_63 >= 1/66 only. "
            "Shifted conjecture only; nothing about the unshifted lonely runner conjecture; one n only; sporadic; to our knowledge first in 39..94. "
            "Producer and independent auditor are AI agents; no human audit. Filed C because an assembly argument is capped at C; the Lean covering statement is filed separately as SLR63-A-0001 and is not an input to this C row.",
            ["SLR63-L-0001", "SLR63-C-0001", "SLR63-C-0002"],
            arg("C-assembly", "Assembly of the exact checkers (C), controls (C) and the definition (L), as in Sections 1 to 3.",
                [DATA / "RESULT.md", DATA / "result.json", DATA / "AUDIT.md"], "none")),
        rec("SLR63-X-0001", "X", "numeric",
            "Search and negative sweeps: CP-SAT pool of 3-smooth multiples of 4 and {3,5}-smooth odds, J=8: INFEASIBLE for N=95..65 and 63..60, FOUND at N=64; J=16 infeasible N=47,46,44, UNKNOWN elsewhere; "
            "larger pools UNKNOWN. Statements are about that pool, menu and N only. NOT re-run by the auditor. Supports no claim about the conjecture for other n.",
            [], num([DATA / "logs" / "cpsat_sweep1.log", DATA / "logs" / "cpsat_smooth_cont.log", DATA / "logs" / "cpsat_smooth_J16.log"], "producer logs")),
        rec("SLR63-X-0002", "X", "numeric",
            "Scoop check, a recorded search and not a proof of absence: alphaXiv recency searches (producer 2026-11-07; auditor 2026-11-08, one with published_after 2026-10-01) and a web search "
            "found no paper covering n in 39..94. Residual risk: later listings, unpublished work. Authors not contacted.",
            [], num([DATA / "RESULT.md", DATA / "AUDIT.md"], "RESULT.md prior-art section and AUDIT.md section 5")),
        rec("SLR63-X-0003", "X", "numeric",
            "NOT done: statement lock (LeanMaster); anse/formal/lean_runner.py gate on SLRN63.lean; human audit; re-run of the CP-SAT sweeps by the auditor; independent Lean compile by the auditor.",
            [], num([DATA / "lean" / "compile_first_attempt.log", DATA / "lean" / "lean_inj.json", DATA / "lean" / "compile_full.log"],
                    "first full compile rc 1 (v_injective maxRecDepth); small-file fix test rc 0; full recompile rc 0 (see SLR63-A-0001)")),
    ]
    (HERE / "ledger.json").write_text(json.dumps({"schema_version": 1, "claims": c}, indent=1, ensure_ascii=False))
    print(f"claims {len(c)}; evidence blobs {len(list(EV.glob('*.json')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
