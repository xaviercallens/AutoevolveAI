"""Check: no screened-stable scan point on the scan-domain boundary (x = 0.15 or y = 1.15), for every a."""

import csv
import glob
import os
import sys

d = sys.argv[1]
for f in sorted(glob.glob(os.path.join(d, "scan_a*.csv"))):
    pts = [p for p in csv.DictReader(open(f)) if p["stable_screen"] == "True"]
    xb = [p for p in pts if abs(float(p["x"]) - 0.15) < 1e-9]
    yb = [p for p in pts if abs(float(p["y"]) - 1.15) < 1e-9]
    print(os.path.basename(f), "stable", len(pts), "on x=0.15:", len(xb), "on y=1.15:", len(yb),
          "x range", min(float(p["x"]) for p in pts), "y max", max(float(p["y"]) for p in pts))
