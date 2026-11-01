import json, glob
G = 'results/proposal5/2026-10-27/GR-11'
keys = ['count', 'viol20', 'viol21', 'tie20', 'tie21', 'ctl29', 'ctl_l1', 'ctl_rank']
tot = dict.fromkeys(keys, 0); sec = 0; m20 = 9e9; m21 = 9e9; parts = set()
for f in sorted(glob.glob(G + '/logs/scan_n11_*of40.json')):
    r = json.loads(open(f).read())
    parts.add(r['res'])
    for k in keys:
        tot[k] += r[k]
    sec += r['sec']; m20 = min(m20, r['min_gap20']); m21 = min(m21, r['min_gap21'])
tot.update(parts=len(parts), expected=1006700565, count_ok=tot['count'] == 1006700565,
           cpu_core_hours=sec / 3600, min_gap20=m20, min_gap21=m21)
json.dump(tot, open(G + '/data/n11_aggregate.json', 'w'), indent=1)
print(json.dumps(tot, indent=1))
