"""Run from the MS-CENSUS dir: python3 -I code/make_result.py"""
import glob
import hashlib
import json
import os

files = sorted(f for f in glob.glob('**/*', recursive=True)
               if os.path.isfile(f) and f not in ('result.json', 'code/d2c_filter'))
h = {f: hashlib.sha256(open(f, 'rb').read()).hexdigest() for f in files}
rows = {}
for n in range(3, 12):
    d = json.load(open(f'data/lemmas_n{n}.json'))
    rows[n] = dict(d2c=d['d2c_graphs'], max_edges=d['max_edges'], floor_n2_4=d['floor_n2_over_4'],
                   extremal=d['extremal_count'], extremal_are_Kab=d['extremal_are_Kab'],
                   equality_cases=len(d['equality_cases']), maximal_matchings=d['total_maximal_matchings'],
                   violations=d['viol'])
json.dump(dict(item="MS-CENSUS", outcome="CONSISTENT", tier="C", n_range=[3, 11],
               total_d2c=sum(r['d2c'] for r in rows.values()), per_n=rows,
               controls_all_pass=json.load(open('data/controls.json'))['all_controls_pass'],
               prereg_sha256=open('PREREG_ITEM.md.sha256').read().split()[0], file_sha256=h),
          open('result.json', 'w'), indent=1)
print(len(h))
