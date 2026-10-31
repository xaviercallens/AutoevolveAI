import subprocess, json, hashlib, glob, os
G = 'results/proposal5/2026-10-27/GR-11'
for n in range(4, 9):
    out = subprocess.run(['.venv/bin/python', G + '/code/scan.py', str(n), '0', '1'], capture_output=True, text=True).stdout
    open(f'{G}/logs/scan_n{n}.json', 'w').write(out)
rows = []
for f in sorted(glob.glob(G + '/logs/scan_n*.json')):
    for l in open(f):
        if l.strip():
            rows.append(json.loads(l))
agg = {}
for r in rows:
    a = agg.setdefault(r['n'], dict(count=0, viol20=0, viol21=0, ctl29=0, ctl_l1=0, ctl_rank=0, tie21=0, tie20=0))
    for k in a:
        a[k] += r[k]
res = dict(per_n=agg, total=sum(a['count'] for a in agg.values()))
files = {}
for p in sorted(glob.glob(G + '/**/*', recursive=True)):
    if os.path.isfile(p) and not p.endswith('result.json'):
        files[os.path.relpath(p, G)] = hashlib.sha256(open(p, 'rb').read()).hexdigest()
res['sha256'] = files
json.dump(res, open(G + '/result.json', 'w'), indent=1)
print(json.dumps(agg, indent=0))
