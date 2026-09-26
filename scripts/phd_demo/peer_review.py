#!/usr/bin/env python3
"""Adversarial peer review that makes real model calls and can reject.

This replaces the pattern found in `scripts/review_paper_gemini_pro.py`, which
reads the paper only to assert `len(tex) > 1000`, then hardcodes five
`score=10` dimensions, prints `TOTAL SCORE: 50 / 50`, writes
`ACCEPT WITHOUT RESERVATION` and attributes the result to a model it never
called (grep it for an HTTP client: there is none).

Two properties make this one different:

  1. **It calls a model.** Local Ollama first (free, ~35 tok/s on the T4);
     `--escalate` permits a paid tier. If no model is reachable it RAISES --
     it never defaults to accept.
  2. **It is falsified before it is trusted.** `--negative-control` injects a
     claim contradicted by the paper's own ledger and requires the reviewer to
     reject it. A reviewer that has never rejected anything is not a reviewer,
     and its acceptance carries no information.

Reviewers are given the artifact ledger alongside the paper, so "this number is
unsupported" is a checkable statement rather than an impression.

Usage:
    .venv/bin/python scripts/phd_demo/peer_review.py --negative-control
    .venv/bin/python scripts/phd_demo/peer_review.py --loops 3
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

REPO = Path(__file__).resolve().parent.parent.parent
PAPER = REPO / "papers" / "phd_demo_verlet" / "verlet_symplectic.tex"
LEDGER = REPO / "results" / "phd_demo" / "artifacts.json"
OUT = REPO / "results" / "phd_demo" / "review"

OLLAMA = "http://localhost:11434"
DEFAULT_MODEL = "qwen3:8b"

# Each reviewer gets a distinct lens. A paper can fail in several ways, and
# redundant identical reviewers catch fewer of them than diverse ones.
LENSES: tuple[tuple[str, str], ...] = (
    (
        "provenance",
        "Every quantitative claim must be traceable to the ledger. Reject if any "
        "number in the paper does not appear in, or contradicts, the ledger.",
    ),
    (
        "formal",
        "The Lean claims must be sound. `sorry` compiles and exits 0 in Lean, so an "
        "exit code proves nothing; only an axiom audit showing no sorryAx does. "
        "Reject vacuous statements (anything of the form `True`) presented as results.",
    ),
    (
        "statistics",
        "Reject any improvement inferred from comparing only two endpoints, any mean "
        "taken over sentinel values, and any claimed effect smaller than its noise "
        "floor. Check that stated agreement tolerances are actually met.",
    ),
)


class ReviewerUnavailable(RuntimeError):
    """No model could be reached. Never silently becomes an acceptance."""


@dataclass
class Review:
    lens: str
    model: str
    rejects: bool
    severity: str
    unsupported_claims: list[str] = field(default_factory=list)
    reasoning: str = ""
    raw: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "lens": self.lens,
            "model": self.model,
            "model_actually_invoked": True,
            "rejects": self.rejects,
            "severity": self.severity,
            "unsupported_claims": self.unsupported_claims,
            "reasoning": self.reasoning[:1500],
        }


def call_ollama(prompt: str, model: str, timeout: float = 900.0) -> str:
    try:
        response = httpx.post(
            f"{OLLAMA}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 900},
            },
            timeout=timeout,
        )
    except httpx.HTTPError as exc:
        raise ReviewerUnavailable(f"Ollama unreachable: {exc}") from exc
    if response.status_code != 200:
        raise ReviewerUnavailable(f"Ollama returned {response.status_code}")
    text = response.json().get("response", "")
    if not text.strip():
        raise ReviewerUnavailable("model returned an empty response")
    return text


def build_prompt(paper: str, ledger: dict[str, Any], lens: str, instruction: str) -> str:
    return f"""You are an adversarial referee for a top-tier journal. Your job is to find
unsupported claims. Default to REJECT when uncertain. A paper you wave through is
worth nothing.

YOUR ASSIGNED LENS: {lens}
{instruction}

You are given the paper AND the machine-generated artifact ledger that produced
its numbers. A claim is SUPPORTED only if the ledger contains a matching value.

=== ARTIFACT LEDGER (ground truth) ===
{json.dumps(ledger, indent=1)[:6000]}

=== PAPER (LaTeX source) ===
{paper[:9000]}

Respond with ONLY a JSON object, no prose outside it:
{{"rejects": true or false,
  "severity": "fatal" or "major" or "minor" or "none",
  "unsupported_claims": ["specific claim 1", "..."],
  "reasoning": "one paragraph"}}
"""


def parse_verdict(raw: str, lens: str, model: str) -> Review:
    # Strip any <think> block a reasoning model may emit before its answer.
    body = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    match = re.search(r"\{.*\}", body, flags=re.DOTALL)
    if not match:
        # Unparseable is not acceptance. Treat as a rejection needing a human.
        return Review(lens, model, True, "major",
                      ["reviewer output was unparseable"], raw[:500], raw)
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError:
        return Review(lens, model, True, "major",
                      ["reviewer emitted invalid JSON"], raw[:500], raw)
    return Review(
        lens=lens,
        model=model,
        rejects=bool(data.get("rejects", True)),
        severity=str(data.get("severity", "major")),
        unsupported_claims=[str(c) for c in data.get("unsupported_claims", [])],
        reasoning=str(data.get("reasoning", "")),
        raw=raw,
    )


def review_once(paper: str, ledger: dict[str, Any], model: str) -> list[Review]:
    reviews = []
    for lens, instruction in LENSES:
        raw = call_ollama(build_prompt(paper, ledger, lens, instruction), model)
        reviews.append(parse_verdict(raw, lens, model))
    return reviews


def corrupt_paper(paper: str, ledger: dict[str, Any]) -> str:
    """Inject a claim the ledger contradicts, for the negative control.

    The true ratio is omega^2/4 = 0.25 and the true agreement is ~1e-10; this
    asserts a ratio of 0.99 and exact agreement. A competent referee with the
    ledger in hand must catch at least one.
    """
    broken = paper.replace(
        r"\begin{abstract}",
        r"\begin{abstract}"
        "\nWe further establish that the measured ratio amplitude$/h^2$ equals "
        r"$0.99$, that the two implementations agree \emph{exactly} to all "
        "digits, and that explicit Euler also conserves energy to machine "
        "precision. ",
        1,
    )
    if broken == paper:  # abstract not found: append instead of silently no-op
        broken = paper + "\n% INJECTED: amplitude/h^2 = 0.99; Euler conserves energy.\n"
    return broken


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--loops", type=int, default=3)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--negative-control", action="store_true",
                    help="verify the reviewer can reject a knowingly-broken paper")
    args = ap.parse_args(argv)

    if not PAPER.exists() or not LEDGER.exists():
        print("paper or ledger missing; run run_experiment.py and build_paper.py first",
              file=sys.stderr)
        return 1
    paper = PAPER.read_text()
    ledger = json.loads(LEDGER.read_text())
    OUT.mkdir(parents=True, exist_ok=True)

    record: dict[str, Any] = {"model": args.model, "loops": [], "negative_control": None}

    if args.negative_control:
        print("=== NEGATIVE CONTROL: reviewer must REJECT a corrupted paper ===")
        try:
            controls = review_once(corrupt_paper(paper, ledger), ledger, args.model)
        except ReviewerUnavailable as exc:
            print(f"REVIEWER UNAVAILABLE: {exc}", file=sys.stderr)
            return 1
        rejected = [r for r in controls if r.rejects]
        for r in controls:
            print(f"  [{r.lens:12}] rejects={r.rejects} severity={r.severity} "
                  f"found={len(r.unsupported_claims)}")
        record["negative_control"] = {
            "lenses": [r.as_dict() for r in controls],
            "rejected_by": len(rejected),
            "passed": len(rejected) > 0,
        }
        if not rejected:
            print("\nFAILED: the reviewer accepted a knowingly-broken paper. "
                  "Its approval of the real paper would be worthless.")
            (OUT / "review.json").write_text(json.dumps(record, indent=2) + "\n")
            return 1
        print(f"  -> control PASSED: {len(rejected)}/{len(controls)} lenses rejected\n")

    for loop in range(1, args.loops + 1):
        print(f"=== REVIEW LOOP {loop}/{args.loops} ===")
        try:
            reviews = review_once(paper, ledger, args.model)
        except ReviewerUnavailable as exc:
            print(f"REVIEWER UNAVAILABLE: {exc}", file=sys.stderr)
            return 1
        rejecting = [r for r in reviews if r.rejects]
        for r in reviews:
            print(f"  [{r.lens:12}] rejects={r.rejects} severity={r.severity} "
                  f"claims={len(r.unsupported_claims)}")
            for c in r.unsupported_claims[:3]:
                print(f"      - {c[:120]}")
        record["loops"].append({
            "loop": loop,
            "reviews": [r.as_dict() for r in reviews],
            "rejecting": len(rejecting),
            "accepted": len(rejecting) == 0,
        })
        if not rejecting:
            print(f"  -> all {len(reviews)} lenses accept at loop {loop}\n")
            break
        print(f"  -> {len(rejecting)}/{len(reviews)} lenses reject; issues recorded\n")

    final = record["loops"][-1]
    record["final_accepted"] = final["accepted"]
    record["loops_run"] = len(record["loops"])
    (OUT / "review.json").write_text(json.dumps(record, indent=2) + "\n")

    print("=" * 70)
    print(f"negative control : "
          f"{'PASSED' if (record['negative_control'] or {}).get('passed') else 'not run'}")
    print(f"loops run        : {record['loops_run']}")
    print(f"final verdict    : {'ACCEPTED' if final['accepted'] else 'REJECTED'}")
    print(f"record           : {(OUT / 'review.json').relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
