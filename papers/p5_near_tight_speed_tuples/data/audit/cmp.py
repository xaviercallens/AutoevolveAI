"""Compare two tuple files exactly (lines 'v1..vn p q k'); print counts, k-distribution, set diffs."""
import sys
import json
from collections import Counter


def load(path: str) -> set[tuple[int, ...]]:
    rows = set()
    with open(path) as f:
        for line in f:
            p = line.split()
            if p and p[0] not in ("NT", "k") and not p[0].startswith("N="):
                rows.add(tuple(map(int, p)))
            elif p and p[0] == "NT":
                # Cordella survey format: NT v1..vn  ML=p/q k=K ...
                vs = []
                i = 1
                while not p[i].startswith("ML="):
                    vs.append(int(p[i]))
                    i += 1
                pn, qn = map(int, p[i][3:].split("/"))
                k = int(p[i + 1][2:])
                rows.add(tuple(vs) + (pn, qn, k))
    return rows


def main() -> None:
    a, b = load(sys.argv[1]), load(sys.argv[2])
    out = {
        "A": sys.argv[1], "B": sys.argv[2], "nA": len(a), "nB": len(b),
        "kA": dict(sorted(Counter(r[-1] for r in a).items())),
        "kB": dict(sorted(Counter(r[-1] for r in b).items())),
        "identical": a == b,
        "onlyA": sorted(a - b)[:10], "onlyB": sorted(b - a)[:10],
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
