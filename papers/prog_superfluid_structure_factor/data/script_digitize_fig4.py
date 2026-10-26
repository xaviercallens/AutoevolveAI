"""Pixel digitizer for scatter markers in a cropped figure (Tier X extraction).

usage: digitize_fig4.py CROP.png OUT.json [R]
Finds the axis frame, major ticks, and marker centroids (filled or open circles).
"""
import json
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

path = sys.argv[1]
r = int(sys.argv[3]) if len(sys.argv) > 3 else 9
im = np.array(Image.open(path).convert('L'))
dark = im < 128
rows = dark.sum(axis=1)
cols = dark.sum(axis=0)
xaxis_row = int(np.argmax(rows))
yaxis_col = int(np.argmax(cols))
print('x-axis row', xaxis_row, rows[xaxis_row], 'y-axis col', yaxis_col, cols[yaxis_col])
band = dark[xaxis_row + 5:xaxis_row + 14, :].sum(axis=0) > 5
xs = np.where(band)[0]
groups = np.split(xs, np.where(np.diff(xs) > 3)[0] + 1)
ticks_x = [float(g.mean()) for g in groups if len(g) > 0]
print('x ticks px', [round(t, 1) for t in ticks_x])
bandy = dark[:, yaxis_col - 14:yaxis_col - 5].sum(axis=1) > 5
ys = np.where(bandy)[0]
gy = np.split(ys, np.where(np.diff(ys) > 3)[0] + 1)
ticks_y = [float(g.mean()) for g in gy if len(g) > 0]
print('y ticks px', [round(t, 1) for t in ticks_y])
filled = ndi.binary_fill_holes(dark)
yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
disk = (xx * xx + yy * yy) <= r * r
op = ndi.binary_opening(filled, structure=disk)
lab, n = ndi.label(op)
out = []
for i in range(1, n + 1):
    m = lab == i
    cy, cx = ndi.center_of_mass(m)
    out.append(dict(px=float(cx), py=float(cy), area=float(m.sum()), dark_frac=float(dark[m].mean())))
out.sort(key=lambda d: d['px'])
for d in out:
    print(round(d['px'], 1), round(d['py'], 1), d['area'], round(d['dark_frac'], 2))
json.dump(dict(xaxis_row=xaxis_row, yaxis_col=yaxis_col, ticks_x=ticks_x, ticks_y=ticks_y, markers=out),
          open(sys.argv[2], 'w'))
