"""Worker: python run11.py <worker 0|1>; runs n=11 parts res = worker, worker+2, ... of 40; skips finished parts."""
import sys, os, subprocess
G = 'results/proposal5/2026-10-27/GR-11'
w = int(sys.argv[1])
for res in range(w, 40, 2):
    out = f'{G}/logs/scan_n11_{res}of40.json'
    if os.path.exists(out) and os.path.getsize(out) > 0:
        continue
    tmp = out + '.tmp'
    fl = f'{G}/data/flagged_n11_{res}of40.txt'
    with open(tmp, 'w') as f:
        r = subprocess.run(['.venv/bin/python', f'{G}/code/scan.py', '11', str(res), '40', fl], stdout=f)
    if r.returncode == 0:
        os.rename(tmp, out)
