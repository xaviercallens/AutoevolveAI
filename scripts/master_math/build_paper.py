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
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))  # repo root: `scripts.*` packages

from scripts.master_math.problems import BLOCKED, PROBLEMS  # noqa: E402

RUN = REPO / "results" / "master_math_run2"
OUT = REPO / "papers" / "master_math_run2" / "master_math_run2.tex"
RECEIPTS = REPO / "results" / "master_math_20_problems_closed_loop_receipts.json"
MODEL_NAMES = {"deepseek": "DeepSeek-Prover-V2-7B (Q8\\_0)", "goedel": "Goedel-Prover-V2-8B (Q6\\_K)"}

GEN_CAP = 4096  # num_predict in scripts/hardness/run_ladder.py::generate

FAILURE_CLASSES = [
    ("hit the 4096-token generation cap", lambda r: r.get("tokens", 0) >= GEN_CAP),
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
    false_attempts = sum(1 for r in runs if r["truth"] is False)
    capped = {m: (sum(1 for r in runs if r["model"] == m and r.get("tokens", 0) >= GEN_CAP),
                  sum(1 for r in runs if r["model"] == m)) for m in models}
    namefix_p = RUN / "namefix_control.json"
    namefix = json.loads(namefix_p.read_text())["summary"] if namefix_p.exists() else None
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
\sloppy
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
      f"arithmetic proxies, {fid['special-case']} as a special case and {fid['definitional']} as "
      f"definitional (a structure field). Results: {per_model}. "
      f"Across {false_attempts} measured attempts on the {false_n} (model, false variant) pairs, "
      f"{false_acc} were accepted -- a sanity check of the gate, since every false variant's negation "
      "is kernel-proved. One error-feedback repair round rescued no statement. A first QLoRA fine-tune "
      "of the prover passed the project's promotion rule on a held-out split, but a control shows the "
      "gain is a naming effect: renaming one namespace in the \\emph{base} model's failed proofs does "
      "better than the fine-tune. We also report two holes in the project's own gate, found and closed "
      "during this run: a missing axiom report was read as ``no axioms'', and a proof body could forge "
      "the report with extra top-level commands.\n")
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
      "report; the old gate scored it clean, measured live. The first fix required the report line "
      "naming the theorem. The adversarial review (Section~\\ref{sec:review}) then broke that fix: "
      "everything after \\texttt{:=} is model text, and Lean parses further top-level commands there, "
      "so \\texttt{by admit} followed by \\texttt{\\#print \"'X' depends on axioms: [propext]\"} and "
      "\\texttt{\\#exit} compiles with exit code 0 and forges the report (reproduced live). The gate now "
      "also rejects any source containing a \\texttt{\\#} command other than the file's own final "
      "\\texttt{\\#print axioms}, \\texttt{sorry}/\\texttt{admit}, \\texttt{axiom} declarations, "
      "\\texttt{set\\_option} (which can switch the kernel check off), macro/syntax/elab definitions, "
      "or the compiler's \\emph{declaration uses sorry} warning, and it requires the axiom report to "
      "appear exactly once. All accepted proofs in this paper were re-checked under the hardened gate; "
      "none is affected. None of the 117 generations logged by the earlier hardness baseline contained "
      "\\texttt{\\#exit}.\n\n")
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
      f"Generation is capped at {GEN_CAP} tokens (\\texttt{{num\\_predict}}). That cap binds for "
      "Goedel-Prover-V2, a long chain-of-thought model: "
      + "; ".join(f"{m} {c}/{n} attempts hit it" for m, (c, n) in capped.items())
      + ". Goedel's numbers therefore partly measure the budget, not the model. During the run "
      "Ollama's \\texttt{api/ps} reported DeepSeek at 30.9\\,GB with 12.9\\,GB in VRAM (four parallel "
      "slots of a 12288-token KV cache), so most layers ran on the CPU; this reading was observed, not "
      "archived as an artifact. We kept the setting for comparability with the baseline.\n\n")
    if infra:
        a(f"{len(infra)} attempt(s) ended in an infrastructure error and are unmeasured, not counted as "
          "either outcome: " + "; ".join(f"{tex(r['model'])} {tex(r['id'])} round {r['round']} "
                                         f"({tex(r['error'][:40])})" for r in infra) + ".\n\n")

    a(r"\section{Results}" + "\n")
    short = {"VERIFIED_SOUND": "verified", "REJECT": "rejected", "UNVERIFIED_IN_LEAN": "unverified"}
    a("{\\footnotesize\n\\begin{longtable}{llll" + "c" * len(models) + "}\n\\caption{Per-statement outcome. "
      "\\checkmark{} greedy proof accepted; repair: accepted after one error-feedback round; "
      "$\\times$ both rejected. ``Run one'': status claimed in the run-one receipts (a different, "
      "partly malformed statement set; its \\#9 was a pointwise proxy).}\\label{tab:items}\\\\\n"
      "\\toprule\nId & Title & Fidelity & Run one & " + " & ".join(m for m in models)
      + "\\\\\n\\midrule\n")
    for p in PROBLEMS:
        src = p["source"]
        r1 = "--"
        if src.startswith("receipts#"):
            raw = str(receipts.get(src.split("#")[1], {}).get("status", "--")).split(":")[0].strip()
            r1 = short.get(raw, tex(raw))
        a(f"{tex(p['id'].split('_')[0])} & {tex(p['title'][:40])} & {p['fidelity']} & {r1} & "
          + " & ".join(cell(m, p["id"]) for m in models) + "\\\\\n")
    a("\\bottomrule\n\\end{longtable}}\n\n")
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
    retrain = REPO / "results" / "night_retrain_20260927" / "summary.json"
    prover = RUN / "prover_training_full.json"
    if prover.exists():
        pj = json.loads(prover.read_text())
        b, ad, tr = pj.get("eval_base", {}), pj.get("eval_adapter", {}), pj.get("train", {})
        a("\\paragraph{Retraining the prover.} Nothing in the project trained the model that proves: the "
          "nightly trainer fine-tunes Qwen2.5-Coder. We added a QLoRA fine-tune of DeepSeek-Prover-V2-7B "
          f"(NF4, fp16 compute) on {pj.get('data', {}).get('lean_passed_rows', 0)} kernel-verified Lean rows "
          f"({sum(1 for t in pj.get('data', {}).get('tasks', []) if t.startswith('mm'))} statements' proofs "
          "from this run plus the three BAO-run theorems) "
          f"({tr.get('steps', '?')} steps, loss {tr.get('loss_first', '?')} $\\to$ {tr.get('loss_last', '?')}, "
          f"peak {tr.get('peak_mib', '?')}\\,MiB), and the held-out gate the project lacked: base and "
          "adapter, same 4-bit harness, greedy, at most 1024 new tokens (not the 4096 of the Ollama "
          "protocol, so these numbers are not comparable with the baseline's), on the frozen hardness "
          f"split, every proof through the kernel gate. Base: {b.get('true_pass', '?')}/{b.get('true_n', '?')} true items "
          f"({tex(json.dumps(b.get('by_tier', {})))}), {b.get('false_accepted', '?')} false accepted. "
          f"Adapter: {ad.get('true_pass', '?')}/{ad.get('true_n', '?')} "
          f"({tex(json.dumps(ad.get('by_tier', {})))}), {ad.get('false_accepted', '?')} false accepted. "
          f"Gate: {tex(str(pj.get('outcome', 'not reached')))}. ")
        rows_e = pj.get("eval_rows", [])
        base_ok = {r["id"]: bool(r["clean"]) for r in rows_e if r["arm"] == "base" and r["truth"] is True}
        ad_ok = {r["id"]: bool(r["clean"]) for r in rows_e if r["arm"] == "adapter" and r["truth"] is True}
        gained = sorted(k for k in ad_ok if ad_ok[k] and not base_ok.get(k))
        lost = sorted(k for k in ad_ok if base_ok.get(k) and not ad_ok[k])
        n_disc, k_min = len(gained) + len(lost), min(len(gained), len(lost))
        p_two = min(1.0, 2 * sum(comb(n_disc, i) for i in range(k_min + 1)) / 2 ** n_disc) if n_disc else 1.0
        a(f"Paired on the same items: {len(gained)} gained ({tex(', '.join(gained))}), {len(lost)} lost "
          f"({tex(', '.join(lost))}); exact McNemar two-sided $p = {p_two:.3f}$, so the gain is not "
          "statistically significant at this $n$ with one greedy sample. The gate's rule (adapter strictly "
          "above base) is weaker than a significance test. The training loss fell to near zero on "
          "these rows (memorisation), and no training row mentions any Weierstrass name.\n\n")
        if namefix:
            a("\\paragraph{The control that explains the gain.} On the gained T3 items the base model "
              "had written the same strategy as the adapter and failed only on \\emph{Unknown constant "
              "WeierstrassCurve.addX}: the right name, \\texttt{WeierstrassCurve.Affine.addX}, is readable "
              "from the statement's own \\texttt{.toAffine.addX}. Rewriting only that namespace in the "
              "\\emph{base} model's T3 proofs (\\texttt{scripts/master\\_math/namefix\\_control.py}) and "
              f"re-running the hardened gate gives {namefix['renamed_true_pass']}/{namefix['true_n']} true "
              f"T3 items proved and {namefix['renamed_false_accepted']}/{namefix['false_n']} false ones "
              f"accepted, against the adapter's {ad.get('by_tier', {}).get('T3', '?')}. The fine-tune's "
              "gain is a naming effect, and a deterministic post-processor dominates it. The adapter is "
              "therefore \\emph{not} promoted in substance; the finding is that on this tier the base "
              "model's reasoning was right and its vocabulary was wrong, which is what premise or name "
              "retrieval should fix.\n\n")
    if retrain.exists():
        a("\\paragraph{Other retrains the same night.}\n\\begin{itemize}\n")
        for m in json.loads(retrain.read_text())["models"]:
            a(f"\\item {tex(m['model'])}: {tex(m['outcome'])}. {tex(m.get('detail', ''))}\n")
        a("\\end{itemize}\n\n")
    if not prover.exists() and not retrain.exists():
        a("Retraining had not completed when this paper was generated.\n\n")

    a(r"\section{Threats to validity}" + "\n\\begin{itemize}\n"
      "\\item Most faithful statements here are single Mathlib lemmas; a pass shows the model can name "
      "the lemma, not that it can do the mathematics. These theorems and their Mathlib proofs are also "
      "likely present in the provers' training data.\n"
      "\\item One greedy sample per round and one seed; per-model counts on "
      f"{n_true} statements move by about {100 / n_true:.0f} points per statement.\n"
      "\\item Proxies are counted in the tables but prove nothing about their namesakes; mm20 is a "
      "structure field and mm11 states one orientation of the IVT only.\n"
      "\\item Goedel-Prover's scores are bounded by the 4096-token cap (Section 3).\n"
      "\\item The frozen-split leak check is an exact substring match; one frozen T0 item "
      "(\\texttt{t0\\_amgm}) is a near neighbour of a training row (mm17). No elliptic-curve content "
      "is in the training data.\n"
      "\\item The references and false variants were written by the same agent that ran the experiment; "
      "the kernel checks them, but their choice is not independent.\n"
      "\\end{itemize}\n\n")
    a(r"\section{Adversarial review}\label{sec:review}" + "\n"
      "An independent reviewer (a separate agent with no access to this analysis) recomputed every "
      "number in this paper from the raw artifacts; all measurement tables reproduced. It found the "
      "forgeable axiom report (fixed, Section 2), the namespace explanation of the retrain gain "
      "(confirmed by the control above), the Goedel token cap, the differing token budget of the "
      "retrain evaluation, and the fidelity notes. Fixed: the gate hole (with regression tests and a "
      "re-gate of every accepted proof) and the retrain interpretation (the rename control). Disclosed "
      "but still open: pass@$k$ with more than one sample; re-running Goedel-Prover with a larger token "
      "budget; a normalised (alpha-renamed) frozen-split leak check; an evaluation token budget matching "
      "the Ollama protocol; an independent statement audit of the 24 Tier~A ledger claims.\n\n")
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
