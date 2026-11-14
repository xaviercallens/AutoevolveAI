import re, sys, json, hashlib
sys.path.insert(0, "/tmp/muc9audit/pylib")
import fitz
pdf = "/tmp/muc9audit/pdf/p.pdf"
def h(o): return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()
# Tool 1: pdftotext -layout
txt = open("/tmp/muc9audit/pdf/p.txt").read()
a = txt.index("R is the set of 175"); b = txt.index("The vertex-processing order"); c = txt.index("B     An elementary")
def ints(s, drop_pageno=None):
    lines = [l for l in s.splitlines() if l.strip() != str(drop_pageno)]
    return [int(x) for x in re.findall(r"\d+", "\n".join(lines))]
R1 = ints(txt[a+len("R is the set of 175"):b], 13)
pis = txt[b:c]; pis = pis[pis.index("top to bottom:")+14:]
P1 = ints(pis)
# Tool 2: PyMuPDF word boxes, sorted by (page, y, x)
doc = fitz.open(pdf)
words = []
for pno in range(len(doc)):
    for w in doc[pno].get_text("words"):
        words.append((pno, round(w[1], 1), w[0], w[4]))
words.sort()
seq = " ".join(w[3] for w in words)
i = seq.index("175 deleted edge indices:"); j = seq.index("The vertex-processing order"); k = seq.index("An elementary proof")
def ints2(s): return [int(x) for x in re.findall(r"(?<![\w.])\d+(?![\w])", s)]
R2 = ints2(seq[i+len("175 deleted edge indices:"):j])
P2s = seq[j:k]; P2s = P2s[P2s.index("top to bottom:")+14:]
P2 = ints2(P2s)
m = re.search(r"C = \{([^}]*)\}", txt); C = [int(x) for x in re.findall(r"\d+", m.group(1))]
m = re.search(r"J = \{([^}]*)\}", txt); J = [int(x) for x in re.findall(r"\d+", m.group(1))]
print("R1", len(R1), "R2", len(R2), "R2[-1]", R2[-1], "R2[:-1]==R1", R2[:-1] == R1, "sets", set(R2[:-1]) == set(R1), "sorted", R1 == sorted(set(R1)))
print("P1", len(P1), "P2", len(P2), "P1==P2", P1 == P2, "perm", sorted(P1) == list(range(182)))
print("R2 tail", R2[-5:], "P2 head/tail", P2[:3], P2[-3:])
print(json.dumps({"R": h(R1), "pi": h(P1), "C": h(C), "J": h(J)}, indent=1))
json.dump({"R": R1, "pi": P1, "C": C, "J": J}, open("/tmp/muc9audit/work/lists.json", "w"))
