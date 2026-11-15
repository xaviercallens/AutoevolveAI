"""Auditor test: does an interrupted+resumed run give the same boxes as an uninterrupted run?"""
import sys, os, json
sys.path.insert(0, sys.argv[1])
from ph2_enclose import *
T = [QQ(n) / QQ(d) for n, d in [(0.1).as_integer_ratio(), (0.4).as_integer_ratio()]]
ck = sys.argv[2]
if os.path.exists(ck):
    os.remove(ck)
a = run(robertson(), [0, 0], T, p=24, tau=1e-22)
r1 = run(robertson(), [0, 0], T, p=24, tau=1e-22, ckpt=ck, max_attempts=50, ckpt_every=7)
print("interrupted at attempts", r1["attempts"], "outputs", len(r1["outputs"]), flush=True)
r2 = run(robertson(), [0, 0], T, p=24, tau=1e-22, ckpt=ck, ckpt_every=7, max_attempts=120)
print("second interruption attempts", r2["attempts"], "outputs", len(r2["outputs"]), flush=True)
r3 = run(robertson(), [0, 0], T, p=24, tau=1e-22, ckpt=ck, ckpt_every=7)
for o1, o2 in zip(a["outputs"], r3["outputs"]):
    print(o1["t"], "identical_box:", o1["box"] == o2["box"], o1["box"], o2["box"])
print("steps", a["steps"], r3["steps"], "attempts", a["attempts"], r3["attempts"])
# compare with the production checkpoint's first two outputs
d = json.load(open(sys.argv[3]))
for o in d["res"]["outputs"][:2]:
    m = [x for x in a["outputs"] if x["t"] == o["t"]][0]
    print("vs production ckpt", o["t"], "identical:", o["box"] == m["box"])
