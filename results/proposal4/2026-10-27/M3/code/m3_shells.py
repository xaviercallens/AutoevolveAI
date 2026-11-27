"""M3 shell multiplicities, enumerated independently with numpy (no use of the paper's tables).

FCC  L_F = 2^{-1/3} D3,  |v|^2 = 2^{1/3} n,   N_n = #{m in Z^3 : |m|^2 = 2n}   (even norm forces even coordinate sum)
BCC  L_B = L_F^*,        |v|^2 = 2^{-4/3} l,  M_l = #{m in Z^3 : |m|^2 = l, m1 = m2 = m3 (mod 2)}

usage: python -I m3_shells.py KMAX OUT.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


def r3_table(kmax: int) -> np.ndarray:
    """r3[k] = #{m in Z^3 : |m|^2 = k} for 0 <= k <= kmax, by brute-force box enumeration."""
    b = int(np.floor(np.sqrt(kmax))) + 1
    x = np.arange(-b, b + 1, dtype=np.int64)
    sq = x * x
    s2 = (sq[:, None] + sq[None, :]).ravel()
    s2 = s2[s2 <= kmax]
    out = np.zeros(kmax + 1, dtype=np.int64)
    for s in sq:
        tot = s2 + s
        tot = tot[tot <= kmax]
        out += np.bincount(tot, minlength=kmax + 1)
    return out


def same_parity_table(lmax: int) -> np.ndarray:
    """M[l] by direct enumeration of same-parity triples (independent of the r3 shortcut)."""
    b = int(np.floor(np.sqrt(lmax))) + 1
    x = np.arange(-b, b + 1, dtype=np.int64)
    out = np.zeros(lmax + 1, dtype=np.int64)
    for parity in (0, 1):
        xs = x[(x % 2) == parity]
        sq = xs * xs
        s2 = (sq[:, None] + sq[None, :]).ravel()
        for s in sq:
            tot = s2 + s
            tot = tot[tot <= lmax]
            out += np.bincount(tot, minlength=lmax + 1)
    return out


def shells(nmax: int, lmax: int) -> tuple[dict[int, int], dict[int, int]]:
    r3 = r3_table(max(2 * nmax, lmax))
    fcc = {n: int(r3[2 * n]) for n in range(1, nmax + 1) if r3[2 * n] > 0}
    mp = same_parity_table(lmax)
    bcc = {ell: int(mp[ell]) for ell in range(1, lmax + 1) if mp[ell] > 0}
    # cross-check of the parity shortcut: l = 3 (mod 8) -> r3(l); 4 | l -> r3(l/4); else 0
    for ell in range(1, lmax + 1):
        exp = int(r3[ell]) if ell % 8 == 3 else (int(r3[ell // 4]) if ell % 4 == 0 else 0)
        assert int(mp[ell]) == exp, (ell, int(mp[ell]), exp)
    return fcc, bcc


def main() -> int:
    kmax = int(sys.argv[1])
    out = Path(sys.argv[2])
    fcc, bcc = shells(kmax // 2, kmax)
    out.write_text(json.dumps({"kmax": kmax, "fcc_N": fcc, "bcc_M": bcc}) + "\n")
    print("FCC N_1..12:", [fcc.get(n, 0) for n in range(1, 13)])
    print("BCC (l, M_l) l<=48:", [(k, v) for k, v in bcc.items() if k <= 48])
    return 0


if __name__ == "__main__":
    sys.exit(main())
