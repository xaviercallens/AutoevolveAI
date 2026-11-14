"""Independent extraction of Appendix A numbers via PyMuPDF (word boxes) and pdfminer."""
import json
import re
import sys

import fitz  # pymupdf
from pdfminer.high_level import extract_text

PDF = sys.argv[1]
OUT = sys.argv[2]
NUM = re.compile(r"^[−\-]?\d\.\d{7}$")


def norm(s: str) -> str:
    return s.replace("−", "-")


doc = fitz.open(PDF)
start = None
for i, page in enumerate(doc):
    if "Table 2" in page.get_text():
        start = i
print("pages", len(doc), "table2 last page idx", start)
# collect words from table pages (Table 2 onwards until refs)
mu_rows = []
for i in range(len(doc)):
    words = doc[i].get_text("words")  # x0,y0,x1,y1,word,block,line,wordno
    nums = [w for w in words if NUM.match(norm(w[4]))]
    if not nums:
        continue
    print("page", i, "numeric tokens", len(nums))
    # group by row (y), then columns of triples by x
    rows: dict = {}
    for w in nums:
        yc = (w[1] + w[3]) / 2
        key = next((k for k in rows if abs(k - yc) < 3), round(yc, 1))
        rows.setdefault(key, []).append(w)
    for y in sorted(rows):
        ws = sorted(rows[y], key=lambda w: w[0])
        mu_rows.append((i, y, [norm(w[4]) for w in ws], [round(w[0], 1) for w in ws]))
# show column x positions for diagnostics
xs = sorted({x for r in mu_rows for x in r[3]})
print("distinct x0 count", len(xs), xs[:12])
# Column-major vs row-major: record both
tokens_rowmajor = [t for r in mu_rows for t in r[2]]
print("mupdf numeric tokens", len(tokens_rowmajor))
# pdfminer
txt = extract_text(PDF)
toks_pm = [norm(t) for t in re.findall(r"[−\-]?\d\.\d{7}\b", txt)]
print("pdfminer numeric tokens", len(toks_pm))
json.dump({"mupdf_rows": mu_rows, "pdfminer_tokens": toks_pm}, open(OUT, "w"))
