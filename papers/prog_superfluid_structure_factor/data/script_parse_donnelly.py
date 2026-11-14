"""Two independent parses of Donnelly & Barenghi (1998) Ch. 14 web page (pages.uoregon.edu/rjd/vapor15.htm).

Parse A: regex over the text rendering made by tag stripping.
Parse B: html.parser collecting text nodes cell by cell, numbers extracted token by token.
Both must give identical Table 14.1 triples (Q, S, key) and Table 14.3 pairs (Q, S).
Writes JSON with both tables and the agreement report.
"""
import hashlib
import html
import json
import re
import sys
from html.parser import HTMLParser

src = sys.argv[1]
outp = sys.argv[2]
raw = open(src, 'rb').read()
sha = hashlib.sha256(raw).hexdigest()
page = raw.decode('latin-1')

NUM = r'[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?'


def table_numbers_A(text: str, start_pat: str, end_pat: str):
    i = text.index(start_pat)
    j = text.index(end_pat, i)
    seg = text[i + len(start_pat):j]
    return [float(t) for t in re.findall(NUM, seg)]


# ---------- parse A: strip tags with regex
t = re.sub(r'<script.*?</script>|<style.*?</style>', '', page, flags=re.S | re.I)
t = re.sub(r'<[^>]+>', ' ', t)
t = html.unescape(t)
t = re.sub(r'\s+', ' ', t)
# Table 14.1 numbers
a1 = table_numbers_A(t, 'Q (Å-1) S(Q) Key Q (Å-1) S(Q) Key', 'Figure 14.1')
# Table 14.3
i3 = t.index('Recommended values of the structure factor')
j3 = t.index('S(Q)', t.index('S(Q)', i3) + 1) + len('S(Q)')
e3 = t.index('Chronological Bibliography', j3)
a3 = [float(x) for x in re.findall(NUM, t[j3:e3])]


# ---------- parse B: html.parser
class P(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.nodes.append(data.strip())


p = P()
p.feed(page)
nodes = p.nodes


def find_idx(sub: str, start: int = 0) -> int:
    for i in range(start, len(nodes)):
        if sub in re.sub(r'\s+', ' ', nodes[i]):
            return i
    raise ValueError(sub)


def numbers_B(i0: int, i1: int):
    out = []
    for n in nodes[i0:i1]:
        for tok in re.split(r'\s+', n):
            if re.fullmatch(NUM, tok):
                out.append(float(tok))
    return out


i_t1 = find_idx('Adopted database used for structure factor')
i_hdr = find_idx('Q (Å-1)', i_t1)
# the header cells are separate nodes: advance to the first numeric node after S(Q), Key, Q, S(Q), Key
i_fig = find_idx('14.1. The recommended values', i_hdr)
i_start1 = i_hdr
# skip the six header cells
cnt = 0
i = i_hdr
while cnt < 6:
    cnt += 1
    i += 1
b1 = numbers_B(i, i_fig)
i_t3 = find_idx('Recommended values of the structure factor', i_fig)
i_bib = find_idx('Chronological Bibliography', i_t3)
seen = 0
ii = i_t3
while seen < 2:
    ii += 1
    if 'S(Q)' in nodes[ii]:
        seen += 1
b3 = numbers_B(ii + 1, i_bib)
# drop header tokens that happen to be numeric ("14.3" lives in the caption node, not here)

report = dict(sha256=sha, len_A1=len(a1), len_B1=len(b1), len_A3=len(a3), len_B3=len(b3),
              equal_1=(a1 == b1), equal_3=(a3 == b3))
print(report)


def triples(vals):
    assert len(vals) % 3 == 0, len(vals)
    return [tuple(vals[k:k + 3]) for k in range(0, len(vals), 3)]


tr = triples(a1)
left = tr[0::2]
right = tr[1::2]
rows = []
for col, lst in (('L', left), ('R', right)):
    for idx, (q, s, key) in enumerate(lst):
        rows.append(dict(col=col, idx=idx, Q=q, S=s, key=int(key)))
rows.sort(key=lambda r: r['Q'])
report['n_table141'] = len(rows)
report['keys'] = {str(k): sum(1 for r in rows if r['key'] == k) for k in (1, 2, 3)}
report['monotone_left'] = all(left[i][0] < left[i + 1][0] for i in range(len(left) - 1))
report['monotone_right'] = all(right[i][0] < right[i + 1][0] for i in range(len(right) - 1))
pairs = [(a3[k], a3[k + 1]) for k in range(0, len(a3) - 1, 2)]
pairs.sort()
report['n_table143'] = len(pairs)
qs = [q for q, _ in pairs]
report['t143_uniform_0p05'] = all(abs((qs[i + 1] - qs[i]) - 0.05) < 1e-9 for i in range(len(qs) - 1))
report['t143_range'] = [qs[0], qs[-1]]
print(report)
json.dump(dict(report=report, table14_1=rows, table14_3=[dict(Q=q, S=s) for q, s in pairs]),
          open(outp, 'w'), indent=1)
