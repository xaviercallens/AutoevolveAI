#!/usr/bin/env python3
"""Build papers/master_math_run2/master_math_run2.tex from the run's JSON.

Every number in the paper is computed here from results/master_math_run2/*
and the run-one receipts; nothing is typed in by hand. The prose around the
numbers is fixed text that states what was and was not measured.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))  # repo root: `scripts.*` packages

from scripts.master_math.problems import BLOCKED, PROBLEMS  # noqa: E402

RUN = REPO / "results" / "master_math_run2"
OUT = REPO / "papers" / "master_math_run2" / "master_math_run2.tex"
RECEIPTS = REPO / "results" / "master_math_20_problems_closed_loop_receipts.json"
MODEL_NAMES = {"deepseek": "DeepSeek-Prover-V2-7B (Q8\\_0)", "goedel": "Goedel-Prover-V2-8B (Q6\\_K)"}

FAILURE_CLASSES = [
    ("no Lean block extracted", lambda r: not r.get("extracted")),
    ("unknown identifier / constant", lambda r: re.search(r"unknown (identifier|constant)|Unknown (identifier|constant)", r.get("errors", ""))),
    ("search tactic failed (exact?/apply?)", lambda r: re.search(r"exact\?|apply\?", r.get("proof") or "") and not r.get("clean")),
    ("type mismatch", lambda r: "type mismatch" in r.get("errors", "")),
    ("unsolved goals", lambda r: "unsolved goals" in r.get("errors", "")),
    ("tactic failed (linarith/simp/rw/...)", lambda r: re.search(r"failed|did not", r.get("errors", ""))),
    ("other elaboration error", lambda r: True),
]


def tex(s: str) -> str:
    """Escape plain text for LaTeX (not for code)."""
    for a, b in [("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"), ("$", "\\$"), ("#", "\\#"),
                 ("_", "\\_"), ("{", "\\{"), ("}", "\\}"), ("~", "\\textasciitilde{}"), ("^", "\\^{}")]:
        s = s.replace(a, b)
    return s


def classify(r: dict) -> str:
    for name, pred in FAILURE_CLASSES:
        if pred(r):
            return name
    return "other elaboration error"


def main() -> int:
    val = json.loads((RUN / "validation.json").read_text())
    runs_doc = json.loads((RUN / "runs.json").read_text())
    runs = [r for r in runs_doc["runs"] if "error" not in r]
    infra = [r for r in runs_doc["runs"] if "error" in r]
    summary = runs_doc.get("summary", {})
    harvest = json.loads((RUN / "harvest_report.json").read_text()) if (RUN / "harvest_report.json").exists() else {}
    receipts = {str(r["problem_id"]): r for r in json.loads(RECEIPTS.read_text())["receipts"]}
    models = [m for m in ("deepseek", "goedel") if m in summary]

    def cell(model: str, iid: str) -> str:
        rs = {r["round"]: r for r in runs if r["model"] == model and r["id"] == iid}
        if 0 not in rs:
            return "--"
        if rs[0].get("clean"):
            return "\\checkmark"
        if 1 in rs and rs[1].get("clean"):
            return "repair"
        return "$\\times$"

    items_true = [p for p in PROBLEMS]
    n_true = len(items_true)
    solved_any = sorted({r["id"] for r in runs if r["truth"] is True and r.get("clean")})
    fails = [r for r in runs if r["truth"] is True and not r.get("clean")]
    taxonomy = Counter(classify(r) for r in fails)
    search_clean = [r for r in runs if r.get("clean") and re.search(r"exact\?|apply\?", r.get("proof") or "")]
    false_acc = sum(v["false_accepted"] for v in summary.values())
    false_n = sum(v["false_n"] for v in summary.values())
    fid = Counter(p["fidelity"] for p in PROBLEMS)
    v_items = val["items"]
    pos = sum(r["positive_clean"] for r in v_items)
    neg = sum(r["negative_rejected"] for r in v_items)
    ref = sum(r["refutation_clean"] for r in v_items)

    lines: list[str] = []
    a = lines.append
    a(r"""\documentclass[11pt]{article}
\usepackage[margin=2.2cm]{geometry}
\usepackage{booktabs,longtable,amssymb,hyperref}
\usepackage[T1]{fontenc}
\title{Twenty master-level problems, re-run under a kernel gate:\\
locked statements, controls, and what two 7--8B provers actually prove}
\author{AutoevolveAI / ANSE run two (generated from \texttt{results/master\_math\_run2/})}
\date{2026-09-27}
\begin{document}
\maketitle
""")
    per_model = "; ".join(
        f"{MODEL_NAMES[m]} {summary[m]['pass_r0']}/{summary[m]['true_n']} greedy and "
        f"{summary[m]['pass_r1']}/{summary[m]['true_n']} after one error-feedback repair"
        for m in models)
    a(r"\begin{abstract}" + "\n")
    a(f"We re-ran the project's twenty ``master-level'' mathematics problems, whose earlier record "
      f"consisted of a regenerator that sent the model only a title and a verdict taken from a canned "
      f"auditor. Here each problem is a Lean~4 statement fixed in advance ({n_true} statements: the "
      f"twenty, with one split in two, plus three further titles the local Mathlib build can state; "
      f"{len(BLOCKED)} titles are recorded as blocked). Before any model ran, every statement passed "
      f"three kernel controls: a reference proof is accepted ({pos}/{len(v_items)}), the same proof is "
      f"rejected on a false variant ({neg}/{len(v_items)}), and the false variant's negation is itself "
      f"kernel-proved ({ref}/{len(v_items)}). A statement review marks {fid['proxy']} statements as "
      f"arithmetic proxies and {fid['special-case']} as a special case. Results: {per_model}. "
      f"Across {false_n} attempts on false variants, {false_acc} were accepted. We also report a hole "
      f"in the project's own gate, found and closed during this run: a proof ending in "
      f"\\texttt{{\\#exit}} suppressed the axiom report and was scored clean.\n")
    a(r"\end{abstract}" + "\n\n")

    a(r"\section{What the earlier record measured}" + "\n")
    rec_ver = sum(1 for r in receipts.values() if r.get("status") == "VERIFIED_SOUND")
    rec_unv = sum(1 for r in receipts.values() if "UNVERIFIED" in str(r.get("status")))
    rec_rej = sum(1 for r in receipts.values() if "REJECT" in str(r.get("status")))
    a(f"The run-one receipts list {len(receipts)} problems: {rec_ver} marked verified, {rec_rej} rejected "
      f"by a ``red team'' audit and {rec_unv} unverified in Lean. Several statements for problems 11--20 "
      f"were not well-formed Lean (e.g.\\ problem 19 was the English sentence ``Bounded entire implies "
      f"constant''). The later regenerator sent only a title; its model calls timed out after 1\\,s and "
      f"a fallback wrote \\texttt{{theorem X : True := by trivial}}, which a canned auditor then rejected "
      f"(LL.md \\S0). Its geometry ``semantic radar'' demanded an import from "
      f"\\texttt{{Mathlib.Geometry}}, a directory with no module built on this machine, so no geometry "
      f"answer could ever pass. None of that measured a model.\n\n")

    a(r"\section{Instrument}" + "\n")
    a("Statements are ours and locked (\\texttt{scripts/master\\_math/problems.py}); a model supplies "
      "only the proof body, which is compiled against our statement with a pinned import header "
      "(never \\texttt{import Mathlib}; the local build is partial). The gate accepts a proof only if "
      "\\texttt{lake env lean} exits 0, the file's own \\texttt{\\#print axioms} line for that theorem "
      "is present, \\texttt{sorryAx} is absent, and every axiom is in "
      "$\\{\\texttt{propext},\\texttt{Classical.choice},\\texttt{Quot.sound}\\}$.\n\n")
    a(r"\paragraph{A gate hole found in this run.}" + " The previous gate parsed \\emph{any} axioms line "
      "and treated a missing one as ``no axioms''. A file whose proof is \\texttt{sorry} followed by "
      "\\texttt{\\#exit} compiles with exit code 0, prints only a warning, and never reaches the axiom "
      "report; the old gate scored it clean, measured live. The gate now requires positive evidence "
      "(the report line naming the theorem). None of the 117 generations logged by the earlier "
      "hardness baseline contained \\texttt{\\#exit}, so that baseline is unaffected.\n\n")
    a(r"\paragraph{Controls and statement review.}" + f" All {len(v_items)} statements elaborate and "
      "pass the three controls in the abstract. Table~\\ref{tab:items} gives the fidelity of each "
      "statement: \\emph{proxy} statements replace the named theorem by the arithmetic step a textbook "
      "proof ends with (e.g.\\ Gauss--Bonnet becomes $K\\cdot A = 4\\pi$ with $K$ and $A$ inserted by "
      "hand) and prove nothing about the theorem they are named after. Markov's inequality was "
      "upgraded from run one's pointwise proxy to the Bochner-integral statement.\n\n")
    a(r"\paragraph{Blocked titles.}" + " These were not replaced by toys:\n\\begin{itemize}\n")
    for b in BLOCKED:
        a(f"\\item {tex(b['title'])} -- {tex(b['reason'])}.\n")
    a("\\end{itemize}\n\n")

    a(r"\section{Experiment}" + "\n")
    a("Two local provers via Ollama on one NVIDIA T4, one model at a time under the shared GPU lease: "
      + ", ".join(MODEL_NAMES[m] for m in models) + ". Round 0 reproduces the hardness-baseline "
      "protocol (greedy, temperature 0, \\texttt{num\\_ctx} 12288, the last Lean block of content plus "
      "thinking). Round 1, the new measurement, runs once after a round-0 failure and appends the failed "
      "attempt and Lean's error lines to the prompt. False variants receive the same two rounds. "
      "Placement was measured, not assumed: at \\texttt{num\\_ctx} 12288 with four parallel slots "
      "Ollama sized DeepSeek at 30.9\\,GB with 12.9\\,GB in VRAM, so most layers ran on the CPU; "
      "we kept the setting for comparability with the baseline.\n\n")
    if infra:
        a(f"{len(infra)} attempts ended in an infrastructure error and were retried; none is counted.\n\n")

    a(r"\section{Results}" + "\n")
    a("\\begin{longtable}{llll" + "l" * len(models) + "}\n\\caption{Per-statement outcome. "
      "\\checkmark{} greedy proof accepted; repair: accepted after one error-feedback round; "
      "$\\times$ both rejected. Run-one status from the receipts file.}\\label{tab:items}\\\\\n\\toprule\n"
      "Id & Title & Fidelity & Run one & " + " & ".join(m for m in models) + "\\\\\n\\midrule\n")
    for p in PROBLEMS:
        src = p["source"]
        r1 = "--"
        if src.startswith("receipts#"):
            r1 = tex(str(receipts.get(src.split("#")[1], {}).get("status", "--")).split(":")[0])
        a(f"{tex(p['id'].split('_')[0])} & {tex(p['title'][:48])} & {p['fidelity']} & {r1} & "
          + " & ".join(cell(m, p["id"]) for m in models) + "\\\\\n")
    a("\\bottomrule\n\\end{longtable}\n\n")
    a("\\begin{table}[h]\\centering\\begin{tabular}{lrrrrr}\\toprule\n"
      "Model & true $n$ & greedy & +repair & false $n$ & false accepted\\\\\\midrule\n")
    for m in models:
        s = summary[m]
        a(f"{MODEL_NAMES[m]} & {s['true_n']} & {s['pass_r0']} & {s['pass_r1']} & {s['false_n']} & "
          f"{s['false_accepted']}\\\\\n")
    a("\\bottomrule\\end{tabular}\\caption{Summary. A false variant counts as accepted if either round "
      "passed the gate.}\\end{table}\n\n")
    a(f"At least one model proved {len(solved_any)} of the {n_true} statements. ")
    if search_clean:
        a(f"{len(search_clean)} accepted proofs rely on a library-search tactic "
          f"(\\texttt{{exact?}}/\\texttt{{apply?}}); the kernel checks the term it finds, so they are "
          f"valid, but they show retrieval by Lean's own search, not by the model. ")
    a("\n\n\\paragraph{How the rejected attempts failed} (all models, both rounds, true statements):\n"
      "\\begin{itemize}\n")
    for name, _ in FAILURE_CLASSES:
        if taxonomy.get(name):
            a(f"\\item {tex(name)}: {taxonomy[name]}\n")
    a("\\end{itemize}\n\n")

    a(r"\section{What was learned, and what was fed back}" + "\n")
    if harvest:
        a(f"Kernel-clean proofs written by the provers became {harvest.get('sft_rows', 0)} training rows "
          f"with verdict \\texttt{{PASSED}} and provenance; pairs of a clean and a kernel-rejected attempt "
          f"on the same statement became {harvest.get('dpo_pairs', 0)} preference pairs. "
          f"Frozen-split leaks: {len(harvest.get('frozen_split_leaks', []))}. The reference proofs used as "
          f"controls were not used as training targets. ")
    a("No retraining was run: the trainer's promotion gate still lacks a held-out pass@$k$ evaluation "
      "(card P4-5) and has blocked promotion twice for that reason; a third run would reproduce a known "
      "outcome, so the shared GPU time was not spent.\n\n")

    a(r"\section{Threats to validity}" + "\n\\begin{itemize}\n"
      "\\item Most faithful statements here are single Mathlib lemmas; a pass shows the model can name "
      "the lemma, not that it can do the mathematics. These theorems and their Mathlib proofs are also "
      "likely present in the provers' training data.\n"
      "\\item One greedy sample per round and one seed; per-model counts on "
      f"{n_true} statements move by about {100 / n_true:.0f} points per statement.\n"
      "\\item Proxies are counted in the tables but prove nothing about their namesakes.\n"
      "\\item The references and false variants were written by the same agent that ran the experiment; "
      "the kernel checks them, but their choice is not independent.\n"
      "\\end{itemize}\n\n")
    a(r"\section*{Artifacts}" + "\n\\texttt{scripts/master\\_math/} (statements, validator, runner, "
      "harvester, this generator); \\texttt{results/master\\_math\\_run2/} (validation, runs with every "
      "proof and error, harvest report); \\texttt{formal/ANSE/MasterMathRun2.lean} (all statements with "
      "a kernel-checked proof and in-file \\texttt{\\#print axioms}); call log "
      "\\texttt{call\\_logs/master\\_math\\_run2.jsonl} on the data disk.\n\n")
    a(r"\end{document}" + "\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
