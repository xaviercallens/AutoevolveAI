"""Emit control graphs as graph6: positives first (expected D2C), then negatives. Writes ctl_pos.g6, ctl_neg.g6."""
import sys
from itertools import combinations

sys.path.insert(0, "/tmp/msaudit")
from dfh import to_g6  # noqa: E402


def cycle(n: int) -> set[tuple[int, int]]:
    return {(i, (i + 1) % n) for i in range(n)}


def complete(n: int) -> set[tuple[int, int]]:
    return set(combinations(range(n), 2))


def kab(a: int, b: int) -> set[tuple[int, int]]:
    return {(i, a + j) for i in range(a) for j in range(b)}


petersen = {(i, (i + 1) % 5) for i in range(5)} | {(i, i + 5) for i in range(5)} | {(5 + i, 5 + (i + 2) % 5) for i in range(5)}
pos = [(4, cycle(4)), (5, cycle(5)), (10, petersen), (5, kab(2, 3)), (6, kab(3, 3)), (9, kab(4, 5)), (6, kab(1, 5))]
neg = [(3, complete(3)), (4, complete(4)), (5, complete(5)), (4, complete(4) - {(0, 1)}), (6, cycle(6)), (7, cycle(7)),
       (4, {(0, 1), (1, 2), (2, 3)})]
open("/tmp/msaudit/ctl_pos.g6", "w").write("\n".join(to_g6(n, e) for n, e in pos) + "\n")
open("/tmp/msaudit/ctl_neg.g6", "w").write("\n".join(to_g6(n, e) for n, e in neg) + "\n")
