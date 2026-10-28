"""Per-graph reference output of the C1 Python decision code (C1b validation).

Usage: py_pergraph.py <graph6 file> <N> <out.tsv> [max_lines]

Imports decode_batch / build_tables / process from census_enclosure.py (the audit-revised copy with the overflow guard,
copied unchanged into C1b/code) and applies the decision of its flush() verbatim, writing one line per graph:
  graph6  X|C  N^_eff  upper_bound  E  X_max
in the same format as census_fast.c --verbose, so the two can be compared line by line by compare_pergraph.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import census_enclosure as ce  # noqa: E402


def main() -> None:
    path, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    max_lines = int(sys.argv[4]) if len(sys.argv) > 4 else -1
    pairs, qj, qi = ce.build_tables(n)
    two30 = 1 << ce.SCALE_BITS
    two31 = 1 << (ce.SCALE_BITS + 1)
    done = 0
    with open(path, "rb") as fh, open(out, "w") as fo:
        buf: list[bytes] = []

        def flush(lines: list[bytes]) -> None:
            adj = ce.decode_batch(lines, n)
            r = ce.process(adj, n, pairs, qj, qi)
            for g in range(len(lines)):
                e = int(r["E"][g])
                x = int(r["X"][g])
                s = int(r["S"][g])
                m = int(r["m"][g])
                ok = e < two31 and (m * two30 + s) * (two31 - e) + m * e * x < n * m * two30 * (two31 - e)
                excl = ok and not bool(r["regular"][g])
                neff_hat = 1 + s / (m * two30)
                eps = e / two31
                ub = neff_hat + eps * x / (two30 * (1 - eps))
                fo.write(f"{lines[g].strip().decode()}\t{'X' if excl else 'C'}\t{neff_hat:.15g}\t{ub:.15g}\t{e}\t{x}\n")

        for line in fh:
            if max_lines >= 0 and done >= max_lines:
                break
            buf.append(line)
            done += 1
            if len(buf) == ce.BATCH:
                flush(buf)
                buf = []
        if buf:
            flush(buf)
    print("wrote", done, "graphs", flush=True)


if __name__ == "__main__":
    main()
