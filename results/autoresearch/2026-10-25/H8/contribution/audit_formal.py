"""Audit for FORMAL.md: extract exact theorem headers from the Lean file and check the axiom output.

Usage: python -I audit_formal.py CONTRIB_DIR
Prints (1) every `theorem ... :=` header verbatim, (2) axiom audit results of compile_main.json and
compile_controls.json, (3) whether compile_main.json stdout appears verbatim in FORMAL.md.
"""
import json
import re
import sys

ALLOWED = {"propext", "Classical.choice", "Quot.sound"}


def headers(src: str) -> list[str]:
    out = []
    for m in re.finditer(r"^theorem .*?:=", src, flags=re.S | re.M):
        out.append(m.group(0))
    return out


def axiom_sets(stdout: str) -> list[tuple[str, set[str]]]:
    res = []
    for m in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", stdout):
        names = {a.strip() for a in m.group(2).replace("\n", " ").split(",") if a.strip()}
        res.append((m.group(1), names))
    return res


def main(d: str) -> None:
    src = open(d + "/Autoresearch_SkBoundShape.lean").read()
    hs = headers(src)
    print("## theorem headers (verbatim, %d)" % len(hs))
    for h in hs:
        print(h)
        print()
    main_j = json.load(open(d + "/compile_main.json"))
    ctl_j = json.load(open(d + "/compile_controls.json"))
    ms = axiom_sets(main_j["stdout"])
    bad = [n for n, s in ms if not s <= ALLOWED]
    print("## audit")
    print("main rc", main_j["rc"], "sha256", main_j["sha256"], "decls", len(ms), "theorem headers", len(hs),
          "outside whitelist", bad)
    cs = dict(axiom_sets(ctl_j["stdout"]))
    sorry_caught = "sorryAx" in cs.get("QuantumFluids.AutoresearchSkBoundShapeControls.ctl_sorry", set())
    ax_caught = "QuantumFluids.AutoresearchSkBoundShapeControls.ctl_cheat" in cs.get(
        "QuantumFluids.AutoresearchSkBoundShapeControls.ctl_axiom", set())
    print("controls rc", ctl_j["rc"], "ctl_sorry flagged", sorry_caught, "ctl_axiom flagged", ax_caught)
    formal = open(d + "/FORMAL.md").read()
    print("compile_main stdout verbatim in FORMAL.md:", main_j["stdout"].strip() in formal)


if __name__ == "__main__":
    main(sys.argv[1])
