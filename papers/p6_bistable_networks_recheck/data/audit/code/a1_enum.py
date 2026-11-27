import sys
sys.path.insert(0, "/tmp/bistabaudit/code")
from net import enumerate_catalogue, label, catalogue

L, R, fx, s = enumerate_catalogue()
print("labelled", len(L), "fixed", fx, "orbits", len(R), "sizes", s)
ids = catalogue()
T1 = """N0438 X->X+Y 2X->X X+Y->2X
N0440 X->X+Y 2X->X 2Y->X
N0442 X->X+Y 2X->X 2Y->2X
N0443 X->X+Y 2X->X 2Y->X+Y
N0448 X->X+Y 2X->Y X+Y->2X
N0450 X->X+Y 2X->Y 2Y->X
N0452 X->X+Y 2X->Y 2Y->2X
N0453 X->X+Y 2X->Y 2Y->X+Y
N0459 X->X+Y 2X->X+Y 2Y->X
N0467 X->X+Y 2X->2Y 2Y->X
N0474 X->X+Y X+Y->X 2Y->X
N0476 X->X+Y X+Y->X 2Y->2X
N0477 X->X+Y X+Y->X 2Y->X+Y
N0480 X->X+Y X+Y->Y 2Y->X
N0482 X->X+Y X+Y->Y 2Y->2X
N0483 X->X+Y X+Y->Y 2Y->X+Y
N0489 X->X+Y X+Y->2Y 2Y->X
N0510 X->2Y 2X->X X+Y->2X
N0514 X->2Y 2X->X 2Y->2X
N0515 X->2Y 2X->X 2Y->X+Y
N0520 X->2Y 2X->Y X+Y->2X
N0524 X->2Y 2X->Y 2Y->2X
N0525 X->2Y 2X->Y 2Y->X+Y
N0548 X->2Y X+Y->X 2Y->2X
N0549 X->2Y X+Y->X 2Y->X+Y
N0554 X->2Y X+Y->Y 2Y->2X
N0555 X->2Y X+Y->Y 2Y->X+Y"""
ok = 0
for line in T1.splitlines():
    n, *rs = line.split()
    got = label(ids[n]).replace(" ", "").split(",")
    if got == rs:
        ok += 1
    else:
        print("MISMATCH", n, rs, got)
print("Table1 matches", ok, "/27")
for n in ["N0056", "N0350", "N0354", "N0355", "N0361", "N0369", "N0391", "N0600", "N0610",
          "N0638", "N0646", "N0648", "N0649", "N0661", "N0673"]:
    print(n, label(ids[n]))
