"""Warm the page cache for the full transitive .olean import closure of a Lean module.

argv[1]: LEAN_PATH-like colon-separated search roots; argv[2:]: root module names.
Imports are read from the .olean files themselves is hard; instead we parse the `import` lines of the
corresponding .lean sources next to each root (lib/lean/X.olean <-> package source X.lean).
Fallback: scan for the module name strings inside the .olean header (first 64 KiB), which lists imports.
"""
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

lp = open(sys.argv[1]).read().strip() if os.path.isfile(sys.argv[1]) else sys.argv[1]
roots = [r for r in lp.split(":") if r]
todo = list(sys.argv[2:])
seen: set[str] = set()
files: list[str] = []


def find(mod: str) -> str | None:
    rel = mod.replace(".", "/") + ".olean"
    for r in roots:
        p = os.path.join(r, rel)
        if os.path.exists(p):
            return p
    return None


def src_imports(olean: str, mod: str) -> list[str]:
    # lib/lean/A/B.olean -> package root is .../.lake/build/lib/lean ; source at package root/A/B.lean
    base = olean[: -len(mod.replace(".", "/") + ".olean")]
    pkg = base
    for _ in range(4):
        pkg = os.path.dirname(pkg.rstrip("/"))
    cand = [os.path.join(pkg, mod.replace(".", "/") + ".lean")]
    for c in cand:
        if os.path.exists(c):
            out = []
            with open(c, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    s = line.strip()
                    m = re.match(r"^(?:public\s+)?(?:meta\s+)?import\s+(?:all\s+)?([A-Za-z0-9_.']+)", s)
                    if m:
                        out.append(m.group(1))
                    elif s and not s.startswith(("--", "/-", "module", "prelude", "public", "import", "meta")) and out:
                        break
            return out
    return []


while todo:
    mod = todo.pop()
    if mod in seen:
        continue
    seen.add(mod)
    p = find(mod)
    if p is None:
        continue
    files.append(p)
    todo.extend(src_imports(p, mod))


def warm(f: str) -> int:
    n = 0
    for ext in ("", ".private", ".server"):
        try:
            with open(f + ext, "rb") as fh:
                while fh.read(1 << 20):
                    pass
            n += 1
        except OSError:
            pass
    return n


with ThreadPoolExecutor(16) as ex:
    print(sum(ex.map(warm, files)), "files warmed;", len(files), "modules in closure")
