"""P3 axiom gate: parse the pinned-Lean compile logs of the CompletelyMonotone library.

For every library module: rc == 0, no `error`, no `declaration uses 'sorry'`, no `sorry`/`admit`/`axiom` token in the
source, and every `#print axioms` line within the whitelist {propext, Classical.choice, Quot.sound}.
For the planted Controls module: rc == 0 AND `ctl_sorry` must show `sorryAx`, `ctl_axiom` must show
`ProgCM.ctl_cheat` (the gate must catch both). Writes gate.json next to this script.

Usage: python -I gate.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SRC = REPO / "formal_cert" / "Programmes" / "CompletelyMonotone"
LOGS = HERE / "compile_logs"
WHITELIST = {"propext", "Classical.choice", "Quot.sound"}
LIBRARY = ["Basic", "Bernstein", "Laplace", "Limits", "Examples", "Corollaries", "NegativeControls",
           "MathlibOnly", "MathlibOnlyBridge", "Applications"]
MATHLIB_ONLY = ["MathlibOnly"]
CONTROLS = "Controls"
DEPS: dict[str, list[str]] = {
    "Basic": [], "Bernstein": ["Basic"], "Laplace": ["Basic"], "Limits": ["Basic"], "Examples": ["Bernstein"],
    "Corollaries": ["Bernstein", "Laplace"], "NegativeControls": ["Examples"], "Controls": ["Basic"],
    "MathlibOnly": [], "MathlibOnlyBridge": ["MathlibOnly", "Bernstein"], "Applications": ["Corollaries"],
}

AX_RE = re.compile(r"^'(\S*?)' depends on axioms: \[([^\]]*)\]", re.M)
NOAX_RE = re.compile(r"^'(\S*?)' does not depend on any axioms", re.M)


def parse_axioms(out: str) -> dict[str, list[str]]:
    res: dict[str, list[str]] = {}
    for name, body in AX_RE.findall(out):
        res[name] = [a.strip() for a in body.replace("\n", " ").split(",") if a.strip()]
    for name in NOAX_RE.findall(out):
        res[name] = []
    return res


def source_tokens(path: Path) -> list[str]:
    text = path.read_text()
    text = re.sub(r"/-.*?-/", "", text, flags=re.S)
    text = re.sub(r"--[^\n]*", "", text)
    bad = []
    for tok in ("sorry", "admit", "axiom "):
        if re.search(r"(?<![A-Za-z_.])" + re.escape(tok.strip()) + r"(?![A-Za-z_'])", text):
            if tok.strip() == "axiom" and not re.search(r"^\s*axiom\s", text, flags=re.M):
                continue
            bad.append(tok.strip())
    return bad


def main() -> int:
    report: dict[str, object] = {"whitelist": sorted(WHITELIST), "modules": {}}
    ok_all = True
    for mod in LIBRARY + [CONTROLS]:
        log = LOGS / f"{mod}.json"
        entry: dict[str, object] = {"log": str(log.relative_to(REPO))}
        if not log.exists():
            entry["status"] = "MISSING_LOG"
            ok_all = False
            report["modules"][mod] = entry  # type: ignore[index]
            continue
        d = json.loads(log.read_text())
        out = str(d["output"])
        src = SRC / f"{mod}.lean"
        entry["source_sha256"] = hashlib.sha256(src.read_bytes()).hexdigest()
        entry["log_newer_than_source"] = log.stat().st_mtime >= src.stat().st_mtime
        start = log.stat().st_mtime - float(d["seconds"])
        stale = [dep for dep in DEPS[mod]
                 if not (LOGS / f"{dep}.json").exists() or (LOGS / f"{dep}.json").stat().st_mtime > start]
        entry["compiled_after_imports"] = not stale
        entry["stale_against"] = stale
        if not entry["log_newer_than_source"] or stale:
            ok_all = False
        axioms = parse_axioms(out)
        errors = [ln for ln in out.splitlines() if ": error" in ln or ln.startswith("error")]
        sorry_warn = "declaration uses 'sorry'" in out or "declaration uses `sorry`" in out
        entry.update(rc=d["rc"], seconds=d["seconds"], n_print_axioms=len(axioms), errors=errors[:10],
                     sorry_warning=sorry_warn, axioms=axioms)
        if mod == CONTROLS:
            caught_sorry = "sorryAx" in axioms.get("ProgCM.ctl_sorry", [])
            caught_axiom = "ProgCM.ctl_cheat" in axioms.get("ProgCM.ctl_axiom", [])
            passed = d["rc"] == 0 and caught_sorry and caught_axiom
            entry.update(caught_sorry=caught_sorry, caught_axiom=caught_axiom,
                         status="CONTROLS_CAUGHT" if passed else "CONTROLS_NOT_CAUGHT")
        else:
            bad_tokens = source_tokens(SRC / f"{mod}.lean")
            off = {n: [a for a in ax if a not in WHITELIST] for n, ax in axioms.items()}
            off = {n: a for n, a in off.items() if a}
            text = (SRC / f"{mod}.lean").read_text()
            n_decl_printed = len(re.findall(r"^#print axioms", text, flags=re.M))
            code = re.sub(r"--[^\n]*", "", re.sub(r"/-.*?-/", "", text, flags=re.S))
            declared = re.findall(r"^(?:theorem|lemma)\s+(\S+)", code, flags=re.M)
            unprinted = [n for n in declared if not any(k == n or k.endswith("." + n) for k in axioms)]
            imports = re.findall(r"^import\s+(\S+)", text, flags=re.M)
            non_mathlib = [i for i in imports if not i.startswith("Mathlib.")] if mod in MATHLIB_ONLY else []
            entry.update(imports=imports, non_mathlib_imports=non_mathlib)
            passed = (d["rc"] == 0 and not errors and not sorry_warn and not bad_tokens and not off
                      and len(axioms) == n_decl_printed and not unprinted and not non_mathlib)
            entry.update(source_bad_tokens=bad_tokens, off_whitelist=off, n_print_requested=n_decl_printed,
                         n_declared=len(declared), unprinted_declarations=unprinted,
                         status="PASS" if passed else "FAIL")
        if not (entry["log_newer_than_source"] and not stale):
            passed = False
            entry["status"] = "STALE_LOG"
        ok_all = ok_all and passed
        report["modules"][mod] = entry  # type: ignore[index]
    report["overall"] = "PASS" if ok_all else "FAIL"
    (HERE / "gate.json").write_text(json.dumps(report, indent=2) + "\n")
    for mod, e in report["modules"].items():  # type: ignore[union-attr]
        print(f"{mod:18s} {e.get('status')} rc={e.get('rc')} axioms_printed={e.get('n_print_axioms')} "
              f"declared={e.get('n_declared')} unprinted={e.get('unprinted_declarations')} "
              f"fresh={e.get('log_newer_than_source')} after_imports={e.get('compiled_after_imports')}")
    print("OVERALL", report["overall"])
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
