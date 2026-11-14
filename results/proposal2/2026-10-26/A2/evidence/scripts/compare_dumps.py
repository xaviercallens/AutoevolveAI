"""Compare two statement-closure dumps (challenge env vs solution env).

Columns: name kind levels typehash valuehash corpus=… [TYPE=… VALUE=…]
The corpus flag text is ignored (module name differs: <current> vs a real module).
"""
import json
import re
import sys
from pathlib import Path


HYG = re.compile(r"\._@\.[A-Za-z_.]+?\.(\d+)\._hygCtx\._hyg\.(\d+)")


def load(p: str) -> dict[str, list[str]]:
    d: dict[str, list[str]] = {}
    for line in Path(p).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        cols = line.split("\t")
        key = cols[0]
        # alpha-renaming only: hygienic binder names embed the defining module (_stdin vs module name)
        keep = [HYG.sub(r"._@.MOD.\1._hygCtx._hyg.\2", c) for c in cols[1:] if not c.startswith("corpus=")]
        d[key] = keep
    return d


a, b = load(sys.argv[1]), load(sys.argv[2])
only_a = sorted(set(a) - set(b))
only_b = sorted(set(b) - set(a))
diff = sorted(k for k in set(a) & set(b) if a[k] != b[k])
corpus_a = sorted(k for k, v in a.items() if any(c.startswith("TYPE=") for c in v))
res = {"n_challenge": len(a), "n_solution": len(b), "only_in_challenge": only_a,
       "only_in_solution": only_b, "differing": diff, "corpus_constants_challenge": corpus_a}
Path(sys.argv[3]).write_text(json.dumps(res, indent=1))
print(f"challenge={len(a)} solution={len(b)} only_challenge={len(only_a)} only_solution={len(only_b)} differing={len(diff)}")
print("corpus constants (challenge side):", len(corpus_a))
for k in diff[:20]:
    print("DIFF", k, "\n  A:", "\t".join(a[k])[:400], "\n  B:", "\t".join(b[k])[:400])
for k in only_a[:20]:
    print("ONLY_CHALLENGE", k)
for k in only_b[:20]:
    print("ONLY_SOLUTION", k)
