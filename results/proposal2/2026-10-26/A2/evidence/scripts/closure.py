"""Transitive import closure (inside the corpus) of given root modules; topological order output.

usage: closure.py <project_root> <out_json> <Root.Module> [<Root.Module> ...]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
ROOTS = sys.argv[3:]
LOCAL_PREFIXES = ("NavierStokes", "Euler", "ComparatorChallenges")
IMPORT_RE = re.compile(r"^\s*(?:public\s+|private\s+)?(?:meta\s+)?import\s+(?:all\s+)?([A-Za-z0-9_.«»']+)", re.M)


def mod_path(m: str) -> Path:
    return ROOT / (m.replace(".", "/") + ".lean")


def imports_of(m: str) -> list[str]:
    text = mod_path(m).read_text(encoding="utf-8")
    # imports must come at the head; strip block comments roughly
    text = re.sub(r"/-.*?-/", "", text, flags=re.S)
    return IMPORT_RE.findall(text)


def main() -> None:
    deps: dict[str, list[str]] = {}
    external: set[str] = set()
    stack = list(ROOTS)
    while stack:
        m = stack.pop()
        if m in deps:
            continue
        imps = imports_of(m)
        local = [i for i in imps if i.split(".")[0] in LOCAL_PREFIXES]
        external.update(i for i in imps if i.split(".")[0] not in LOCAL_PREFIXES)
        deps[m] = local
        stack.extend(local)
    order: list[str] = []
    seen: set[str] = set()

    def visit(m: str) -> None:
        if m in seen:
            return
        seen.add(m)
        for d in deps[m]:
            visit(d)
        order.append(m)

    sys.setrecursionlimit(100000)
    for r in ROOTS:
        visit(r)
    loc = sum(len(mod_path(m).read_text(encoding="utf-8").splitlines()) for m in order)
    OUT.write_text(json.dumps({"roots": ROOTS, "n_modules": len(order), "total_lines": loc,
                               "external_imports": sorted(external), "topo_order": order,
                               "deps": deps}, indent=1))
    print("modules", len(order), "lines", loc, "external", sorted(external)[:50], len(external))


if __name__ == "__main__":
    main()
