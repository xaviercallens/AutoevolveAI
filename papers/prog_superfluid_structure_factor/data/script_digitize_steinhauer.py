"""Tier X digitization of Steinhauer et al. (cond-mat/0111438) Fig. 4 from the 400 dpi crop.

Marker centres are hand-picked (guesses) then refined with a local centroid when the
marker is isolated; vertical error-bar extents are measured from the dark pixels in the
marker column.  Axis calibration is taken from detected tick pixels:
  x: k = 0 at px 231.0, 14 at px 1135.0 (ticks 129 px per 2 um^-1) -> 64.571 px per um^-1
  y: S = 0 at py 773.0, 1.4 at py 56.0 (ticks 102.4 px per 0.2) -> 512.1 px per unit
Writes a JSON with the rows.
"""
import json
import sys

import numpy as np
from PIL import Image

img = sys.argv[1]
outp = sys.argv[2]
dark = np.array(Image.open(img).convert('L')) < 128

X0, X14 = 231.0, 1135.0
Y0, Y14 = 773.0, 56.0
sx = (X14 - X0) / 14.0
sy = (Y0 - Y14) / 1.4


def kx(px: float) -> float:
    return (px - X0) / sx


def sy_(py: float) -> float:
    return (Y0 - py) / sy


# hand-picked marker centre guesses (px, py) read from the 1454x963 crop
filled = [(258, 766), (277, 752), (299, 691), (322, 652), (345, 641), (366, 561), (389, 574),
          (410, 603), (434, 628), (501, 450), (671, 345), (900, 266), (1174, 325)]
opened = [(258, 738), (276, 679), (299, 658), (322, 624), (345, 628), (366, 605), (388, 556),
          (410, 553), (434, 527), (501, 476), (671, 394), (900, 337), (1174, 297)]


def refine(px: float, py: float, r: int = 9, win: int = 14):
    sub = dark[int(py) - win:int(py) + win + 1, int(px) - win:int(px) + win + 1]
    yy, xx = np.mgrid[-win:win + 1, -win:win + 1]
    inside = (xx ** 2 + yy ** 2) <= r * r
    # centroid of dark pixels within the marker radius
    m = sub & inside
    if m.sum() < 50:
        return px, py
    return px + float((xx * m).sum() / m.sum()), py + float((yy * m).sum() / m.sum())


def bar_extent(px: float, py: float):
    col = dark[:, int(round(px)) - 1:int(round(px)) + 2].any(axis=1)
    # walk up and down from py while dark in column (error bar line), allow 2 px gaps
    up = int(py)
    gap = 0
    y = int(py)
    while y > 57 and gap < 3:
        y -= 1
        if col[y]:
            up = y
            gap = 0
        else:
            gap += 1
    dn = int(py)
    y = int(py)
    gap = 0
    while y < 772 and gap < 3:
        y += 1
        if col[y]:
            dn = y
            gap = 0
        else:
            gap += 1
    return up, dn


rows = []
for px, py in filled:
    cx, cy = refine(px, py)
    up, dn = bar_extent(cx, cy)
    rows.append(dict(kind='filled', k=kx(cx), S=sy_(cy), S_hi=sy_(up), S_lo=sy_(dn), px=cx, py=cy,
                     up_px=up, dn_px=dn))
for px, py in opened:
    rows.append(dict(kind='open', k=kx(px), S=sy_(py), px=px, py=py))
for r in rows:
    print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()})
json.dump(rows, open(outp, 'w'), indent=1)
