"""Reader for dump2.txt (dump driver 2). Each record type is parsed into exact integer intervals."""
from __future__ import annotations

from pathlib import Path

from l1common import DUMP2

IV = tuple[int, int]


def pairs(nums: list[int]) -> list[IV]:
    return [(nums[2 * k], nums[2 * k + 1]) for k in range(len(nums) // 2)]


class Dump2:
    def __init__(self, path: Path = DUMP2, want: set[str] | None = None):
        self.sc: dict[str, IV] = {}
        self.node: dict[int, tuple[int, IV, list[IV]]] = {}
        self.cell: dict[int, list[IV]] = {}
        self.pS: dict[int, tuple[IV, IV, dict[int, IV]]] = {}
        self.cS: dict[int, tuple[IV, IV, dict[int, IV]]] = {}
        self.init_ps: dict[int, IV] = {}
        self.ct: dict[tuple[int, int], list[IV]] = {}
        self.ct_n: dict[int, int] = {}
        self.ct_run: dict[int, list[IV]] = {}
        self.rec: dict[str, list[list[int]]] = {}
        with path.open() as fh:
            for line in fh:
                p = line.split()
                t = p[0]
                if want is not None and t not in want and not (len(p) == 3):
                    continue
                if t == "node":
                    nums = list(map(int, p[3:]))
                    pr = pairs(nums)
                    self.node[int(p[1])] = (int(p[2]), pr[0], pr[1:])
                elif t == "cell":
                    self.cell[int(p[1])] = pairs(list(map(int, p[2:])))
                elif t in ("pS", "cS"):
                    i, nps = int(p[1]), int(p[2])
                    nums = list(map(int, p[3:]))
                    s1, s2 = (nums[0], nums[1]), (nums[2], nums[3])
                    ps = {}
                    for q in range(nps):
                        k, u, v = nums[4 + 3 * q: 7 + 3 * q]
                        ps[k] = (u, v)
                    (self.pS if t == "pS" else self.cS)[i] = (s1, s2, ps)
                elif t == "init_ps":
                    self.init_ps[int(p[1])] = (int(p[2]), int(p[3]))
                elif t == "ct":
                    self.ct[(int(p[1]), int(p[2]))] = pairs(list(map(int, p[3:])))
                elif t == "ct_seg":
                    self.ct_n[int(p[1])] = int(p[2])
                elif t == "ct_run":
                    self.ct_run[int(p[1])] = pairs(list(map(int, p[2:])))
                elif t in ("bd", "gg", "ih", "gg_d", "gg_s", "ih_d", "ih_s", "bd_mesh", "gg_mesh", "ih_mesh"):
                    self.rec.setdefault(t, []).append(list(map(int, p[1:])))
                elif len(p) == 3:
                    try:
                        self.sc[t] = (int(p[1]), int(p[2]))
                    except ValueError:
                        pass
