#!/usr/bin/env python3
"""Drive the v2 implementation cards: list, pick the next ready one, print a prompt-ready card.

    python tools/v2_tasks.py list [--tier low]
    python tools/v2_tasks.py next [--tier low]
    python tools/v2_tasks.py card V0-3
    python tools/v2_tasks.py done V0-3        # only after every accept command passed
    python tools/v2_tasks.py check            # validate the card graph (ids, deps, cycles)

Status lives in docs/v2/status.json so tasks.yaml stays a read-only spec.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "docs/v2/tasks.yaml"
STATUS = ROOT / "docs/v2/status.json"


def load() -> tuple[dict, dict[str, dict]]:
    data = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    return data, {c["id"]: c for c in data["cards"]}


def done_ids() -> set[str]:
    return set(json.loads(STATUS.read_text())) if STATUS.exists() else set()


def ready(cards: dict[str, dict], tier: str | None) -> list[dict]:
    done = done_ids()
    return [c for c in cards.values()
            if c["id"] not in done and set(c["depends_on"]) <= done
            and (tier is None or c["tier"] == tier)]


def problems(cards: dict[str, dict]) -> list[str]:
    out = []
    for c in cards.values():
        for d in c["depends_on"]:
            if d not in cards:
                out.append(f"{c['id']}: unknown dependency {d}")
        if c["tier"] != "human" and not c.get("accept"):
            out.append(f"{c['id']}: non-human card has no accept command")
    state: dict[str, int] = {}

    def visit(i: str, trail: list[str]) -> None:
        if state.get(i) == 2 or i not in cards:
            return
        if state.get(i) == 1:
            out.append("cycle: " + " -> ".join(trail + [i]))
            return
        state[i] = 1
        for d in cards[i]["depends_on"]:
            visit(d, trail + [i])
        state[i] = 2

    for i in cards:
        visit(i, [])
    return out


def render(data: dict, card: dict) -> str:
    lines = ["RULES (apply to every card):"] + [f"  {n}. {r}" for n, r in enumerate(data["rules"], 1)]
    lines += ["", f"CARD {card['id']}: {card['title']}   [tier={card['tier']}, phase={card['phase']}]"]
    for key in ("read_first", "create", "edit"):
        if card.get(key):
            lines.append(f"{key}: " + ", ".join(card[key]))
    lines += ["spec:"] + [f"  - {s}" for s in card.get("spec", [])]
    if card.get("tests"):
        lines += ["tests to write:"] + [f"  - {t}" for t in card["tests"]]
    lines += ["accept (run these; all must exit 0):"] + [f"  $ {a}" for a in card.get("accept", [])]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["list", "next", "card", "done", "check"])
    ap.add_argument("card_id", nargs="?")
    ap.add_argument("--tier", choices=["low", "mid", "human"])
    a = ap.parse_args()
    data, cards = load()
    if a.cmd == "check":
        errs = problems(cards)
        print("\n".join(errs) if errs else f"ok: {len(cards)} cards, no unknown deps, no cycles")
        return 1 if errs else 0
    if a.cmd == "list":
        done = done_ids()
        for c in cards.values():
            mark = "x" if c["id"] in done else " "
            print(f"[{mark}] {c['id']:6s} {c['tier']:5s} {c['title']}")
        return 0
    if a.cmd == "next":
        r = ready(cards, a.tier)
        print(render(data, r[0]) if r else "nothing ready")
        return 0 if r else 1
    if a.card_id not in cards:
        print(f"unknown card {a.card_id}", file=sys.stderr)
        return 2
    if a.cmd == "card":
        print(render(data, cards[a.card_id]))
        return 0
    ids = done_ids() | {a.card_id}
    STATUS.write_text(json.dumps(sorted(ids), indent=1) + "\n")
    print(f"marked {a.card_id} done ({len(ids)}/{len(cards)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
