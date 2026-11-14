#!/usr/bin/env python3
"""LT_D2: finish the kernel pilot of upstream's Lieb-Thirring closure on a DISCLOSED, renamed scratch copy.

Lane LT_D compiled 14 of 38 files under LeanMaster's Mathlib (Lean v4.34.0-rc2) and stopped at one unknown constant,
`Set.equivOfEq`, which LeanMaster's Mathlib spells `Equiv.setCongr` (same statement: an equality of sets gives an
equivalence of the subtypes).  This script copies the closure to a scratch directory, applies ONLY the renames passed on the
command line (each recorded with before/after sha256 and replacement count), and resumes the compile there.  Upstream's
files and LeanMaster's build are never modified.  Rules, fixed in preregistration.json before the first run:
  * a rename is allowed only if the replacement exists in LeanMaster's Mathlib with the same meaning at the use site
    (checked by hand and recorded); statements, definitions and theorem names are never changed;
  * the first error that is not an unknown identifier fixed by such a rename stops the run (reported, not patched around).
What a green run would establish: the kernel of THIS toolchain accepts an adapted copy of upstream's proof with only
standard axioms.  It would NOT be a Comparator run, and the text-level statement comparison below is not an elaborated one.

Subcommands: prepare | closure | axioms | statements
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lt_d_lean as D  # noqa: E402
import d1_hole_bodies as B  # noqa: E402

ROOTS = [D.ROOT_MODULE]
FINALS = [D.FINAL_THEOREM]
CHALLENGE = D.UP / "ComparatorChallenges" / "LiebThirring.lean"
CARRY_FROM: Path | None = None
# upstream's lakefile sets `autoImplicit false` for every OAI library; plain `lean` defaults to true, which is more permissive
LEAN_OPTS: list[str] = ["-DautoImplicit=false"]
LANE_D = Path(__file__).resolve().parents[2] / "results" / "openai_math" / "hypotheses" / "night_2026-10-08" / "LT_D"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def cmd_prepare(lane: Path, renames: list[tuple[str, str]], regex_renames: list[tuple[str, str]], resume: bool) -> None:
    order: list[str] = []
    for r in ROOTS:  # each closure lists dependencies first, so appending unseen items keeps dependency order
        order += [m for m in D.closure_order(r) if m not in order]
    src = lane / "src"
    patches: dict[str, dict[str, object]] = {}
    old_hash: dict[str, str] = {}
    if resume and src.exists():  # hashes of the sources the existing records were compiled from
        for m in order:
            q = src / (m.replace(".", "/") + ".lean")
            if q.exists():
                old_hash[m] = sha(q.read_text(encoding="utf-8"))
    new_hash: dict[str, str] = {}
    for m in order:
        text = D.mod_path(m).read_text(encoding="utf-8")
        new = text
        counts = {}
        for old, rep in renames:
            n = new.count(old)
            if n:
                counts[old] = n
                new = new.replace(old, rep)
        for pat, rep in regex_renames:
            new, n = re.subn(pat, rep, new)
            if n:
                counts["regex:" + pat] = n
        dst = src / (m.replace(".", "/") + ".lean")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(new, encoding="utf-8")
        new_hash[m] = sha(new)
        if counts:
            patches[m] = {"replacements": counts, "sha256_original": sha(text), "sha256_modified": sha(new)}
    D.save(lane, "patches.json", {"renames": renames, "regex_renames": regex_renames, "patched_files": patches})
    # carry over the oleans of lane LT_D for files whose source is unchanged
    scratch = lane / "scratch_olean"
    rec: dict[str, dict[str, object]] = {}
    if CARRY_FROM is not None:
        prior = json.loads((CARRY_FROM / "part1b_closure.json").read_text())
        if not scratch.exists():
            shutil.copytree(CARRY_FROM / "scratch_olean", scratch)
        rec = {m: {"status": "compiled", "seconds": v["seconds"], "carried_from": "LT_D", "first_error": ""}
               for m, v in prior.items() if v["status"] == "compiled" and m not in patches}
    scratch.mkdir(exist_ok=True)
    if resume and (lane / "part1b_closure.json").exists():
        old = json.loads((lane / "part1b_closure.json").read_text())
        for m, v in old.items():
            if v.get("status") == "compiled" and old_hash.get(m) == new_hash.get(m) and (scratch / (m.replace(".", "/") + ".olean")).exists():
                rec[m] = v

    D.save(lane, "part1b_closure.json", rec)
    D.save(lane, "closure.json", {"roots": ROOTS, "n_files": len(order), "order": order})
    print(f"prepared {len(order)} files, {len(patches)} patched, {len(rec)} carried over")


def cmd_closure(lane: Path, max_seconds: int) -> None:
    order = json.loads((lane / "closure.json").read_text())["order"]
    src = lane / "src"
    scratch = lane / "scratch_olean"
    recp = lane / "part1b_closure.json"
    rec = json.loads(recp.read_text())
    lp = D.lean_path() + ":" + str(scratch)
    t_start = time.time()
    for m in order:
        if m in rec and rec[m]["status"] in ("compiled", "failed", "blocked"):
            continue
        path = src / (m.replace(".", "/") + ".lean")
        deps = [d for d in D.IMPORT_RE.findall(path.read_text()) if d.startswith("OAI")]
        bad = [d for d in deps if rec.get(d, {}).get("status") != "compiled"]
        if bad:
            rec[m] = {"status": "blocked", "blocked_by": bad}
            D.save(lane, "part1b_closure.json", rec)
            continue
        if time.time() - t_start > max_seconds:
            print("time slice used; resume later", flush=True)
            break
        out_o = scratch / (m.replace(".", "/") + ".olean")
        out_o.parent.mkdir(parents=True, exist_ok=True)
        res = D.run_lean([*LEAN_OPTS, f"--root={src}", "-o", str(out_o), "-i", str(out_o.with_suffix(".ilean")), str(path)], lp, 3000)
        ok = (not res["has_error"]) and out_o.exists()
        rec[m] = {"status": "compiled" if ok else "failed", "seconds": res["seconds"],
                  "first_error": "" if ok else D.first_error(str(res["output"])), "timed_out": res["timed_out"]}
        D.save(lane, "part1b_closure.json", rec)
        print(m, rec[m]["status"], res["seconds"], rec[m]["first_error"], flush=True)
        if not ok:
            break  # rule: stop at the first failure, never patch around it
    print("compiled", sum(1 for v in rec.values() if v["status"] == "compiled"), "of", len(order))


def cmd_axioms(lane: Path) -> None:
    scratch = lane / "scratch_olean"
    f = lane / "scratch_axioms.lean"
    body = "".join(f"#print axioms {n}\n#check @{n}\n" for n in FINALS)
    f.write_text("".join(f"import {r}\n" for r in ROOTS) + body, encoding="utf-8")
    res = D.run_lean([str(f)], D.lean_path() + ":" + str(scratch), 3000)
    res["verdicts"] = {n: D.axiom_verdict(str(res["output"]), n) for n in FINALS}
    res["axioms_by_theorem"] = {n: D.parse_axioms(str(res["output"])).get(n) for n in FINALS}
    res["verdict"] = D.axiom_verdict(str(res["output"]), FINALS[0])
    res["axioms"] = D.parse_axioms(str(res["output"])).get(FINALS[0])
    D.save(lane, "part_axioms.json", res)
    print(res["verdicts"], res["axioms_by_theorem"])


def cmd_statements(lane: Path) -> None:
    """Text-level comparison (comments stripped, alpha-renaming allowed) of every declaration in the challenge file against
    the declaration of the same name in the solution closure. Not elaboration; a reading aid, labelled as such."""
    chal = B.extract_decls(CHALLENGE.read_text(), CHALLENGE.name)
    order = json.loads((lane / "closure.json").read_text())["order"]
    sol: dict[str, list[B.Decl]] = {}
    for m in order:
        for d in B.extract_decls((lane / "src" / (m.replace(".", "/") + ".lean")).read_text(), m):
            sol.setdefault(d.full_name, []).append(d)
    rows = []
    for d in chal:
        cands = sol.get(d.full_name, [])
        if not cands:
            rows.append({"name": d.full_name, "kind": d.kind, "verdict": "NOT_FOUND_IN_SOLUTION", "challenge_has_sorry": B.has_sorry(d)})
            continue
        results = []
        for c in cands:
            a_tok, b_tok = d.tokens_after_name, c.tokens_after_name
            if d.kind in ("theorem", "lemma"):  # compare the statement only: a proof body may legitimately differ from `sorry`
                a_tok = a_tok[: a_tok.index(":=")] if ":=" in a_tok else a_tok
                b_tok = b_tok[: b_tok.index(":=")] if ":=" in b_tok else b_tok
            same, nsub, _ = B.alpha_compare(a_tok, b_tok)
            results.append({"module": c.file, "line": c.line, "identical_up_to_binder_renaming": same, "substitutions": nsub})
        rows.append({"name": d.full_name, "kind": d.kind, "challenge_has_sorry": B.has_sorry(d), "solution_matches": results,
                     "verdict": "MATCH" if any(r["identical_up_to_binder_renaming"] for r in results) else "DIFFERS"})
    D.save(lane, "part_statements.json", {"note": "text-level, comments stripped; not elaboration", "rows": rows})
    from collections import Counter
    print(Counter(r["verdict"] for r in rows))
    for r in rows:
        print(r["name"], r["kind"], r["verdict"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prepare", "closure", "axioms", "statements"])
    ap.add_argument("--lane", required=True)
    ap.add_argument("--rename", action="append", default=[], help="OLD=NEW plain-text rename (recorded in patches.json)")
    ap.add_argument("--rename-re", action="append", default=[], help="PATTERN=>REPL regex rename (recorded in patches.json)")
    ap.add_argument("--resume", action="store_true", help="keep records/oleans of previously compiled files whose patched source is unchanged")
    ap.add_argument("--max-seconds", type=int, default=3000)
    ap.add_argument("--root", action="append", default=[], help="root module(s) of the closure (default: Lieb-Thirring Main)")
    ap.add_argument("--final", action="append", default=[], help="theorem(s) whose axioms are printed (default: Lieb-Thirring)")
    ap.add_argument("--challenge", default=None, help="challenge file name in ComparatorChallenges/ for the statement comparison")
    ap.add_argument("--carry-from", default=None, help="lane dir whose compiled oleans/records may be reused for unchanged files")
    ap.add_argument("--lean-opt", action="append", default=None,
                    help="lean option(s); default -DautoImplicit=false as in upstream's lakefile; an empty value --lean-opt= "
                         "clears the list (plain lean, the earlier LT_D / LT_D2 runs)")
    args = ap.parse_args()
    global LEAN_OPTS
    if args.lean_opt is not None:
        LEAN_OPTS = [o for o in args.lean_opt if o]
    global ROOTS, FINALS, CHALLENGE, CARRY_FROM
    ROOTS = args.root or ROOTS
    FINALS = args.final or FINALS
    if args.challenge:
        CHALLENGE = D.UP / "ComparatorChallenges" / args.challenge
    CARRY_FROM = Path(args.carry_from).resolve() if args.carry_from else None
    lane = Path(args.lane).resolve()  # Lean runs with cwd = LeanMaster, so every path it receives must be absolute
    lane.mkdir(parents=True, exist_ok=True)
    if args.cmd == "prepare":
        cmd_prepare(lane, [tuple(r.split("=", 1)) for r in args.rename], [tuple(r.split("=>", 1)) for r in args.rename_re], args.resume)
    elif args.cmd == "closure":
        cmd_closure(lane, args.max_seconds)
    elif args.cmd == "axioms":
        cmd_axioms(lane)
    else:
        cmd_statements(lane)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
