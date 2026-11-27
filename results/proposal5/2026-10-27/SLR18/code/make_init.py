"""Build an init state (n lines 'v s') for cover_ls_fast from the certificate of size n-1:
keep its velocities and shifts, add one runner with the smallest unused velocity whose largest
prime factor is <= 5 (falls back to smallest unused integer), with a random shift."""
from __future__ import annotations

import json
import random
import sys

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from smooth_init import lpf  # noqa: E402


def main() -> None:
    cert, out, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    c = json.load(open(cert))
    v = list(c["v"])
    s = [x / c["D"] for x in c["a"]]
    used = set(v)
    w = next((x for x in range(1, 10 * len(v)) if x not in used and lpf(x) <= 5), None)
    if w is None:
        w = next(x for x in range(1, 10 * len(v)) if x not in used)
    rng = random.Random(seed)
    v.append(w)
    s.append(rng.random())
    with open(out, "w") as fh:
        for a, b in zip(v, s):
            fh.write(f"{a} {b:.17g}\n")
    print(len(v), w)


if __name__ == "__main__":
    main()
