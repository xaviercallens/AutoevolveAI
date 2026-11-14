"""Tier X digitization of Stamper-Kurn et al. (cond-mat/9906035) Fig. 3a from the 600 dpi crop.

Calibration (pixel rows/cols of the crop): S = 1.0 at row 206, S = 0.0 at row 633 (axis lines);
top axis peak density 0 at col 205, 6 (x1e14 cm^-3) at col 969.
Error bars are the extent of dark pixels in the marker column (vertical) / marker row (horizontal).
"""
import json
import sys

import numpy as np
from PIL import Image

dark = np.array(Image.open(sys.argv[1]).convert('L')) < 128
outp = sys.argv[2]
Y1, Y0 = 206.0, 633.0
XD0, XD6 = 205.0, 969.0
guess = [(463, 402), (770, 471), (988, 508)]


def centroid(px, py, r=11):
    win = 16
    sub = dark[py - win:py + win + 1, px - win:px + win + 1]
    yy, xx = np.mgrid[-win:win + 1, -win:win + 1]
    m = sub & ((xx ** 2 + yy ** 2) <= r * r)
    return px + (xx * m).sum() / m.sum(), py + (yy * m).sum() / m.sum()


def walk(line, start, step, lo, hi):
    pos = start
    last = start
    gap = 0
    while lo < pos + step < hi and gap < 3:
        pos += step
        if line[pos]:
            last = pos
            gap = 0
        else:
            gap += 1
    return last


rows = []
for gx, gy in guess:
    cx, cy = centroid(gx, gy)
    col = dark[:, int(round(cx)) - 1:int(round(cx)) + 2].any(axis=1)
    up = walk(col, int(cy), -1, 210, 632)
    dn = walk(col, int(cy), +1, 210, 632)
    row = dark[int(round(cy)) - 1:int(round(cy)) + 2, :].any(axis=0)
    lf = walk(row, int(cx), -1, 206, 1040)
    rt = walk(row, int(cx), +1, 206, 1040)
    S = (Y0 - cy) / (Y0 - Y1)
    dens = (cx - XD0) / (XD6 - XD0) * 6.0
    r = dict(px=float(cx), py=float(cy), S=S, S_hi=(Y0 - up) / (Y0 - Y1), S_lo=(Y0 - dn) / (Y0 - Y1),
             dens_1e14=dens, dens_lo=(lf - XD0) / (XD6 - XD0) * 6.0, dens_hi=(rt - XD0) / (XD6 - XD0) * 6.0)
    rows.append(r)
    print({k: round(float(v), 3) for k, v in r.items()})
json.dump(rows, open(outp, 'w'), indent=1)
