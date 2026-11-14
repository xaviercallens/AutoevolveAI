import json, sys, re
B = "/home/callensxavier_gmail_com/AutoevolveAI/.scratchpad/gh_inv/"
H = json.load(open(B + "honest.json"))
for n, d in H.items():
    for p, hits in d.items():
        if hits:
            print("##", n, p)
            for h in hits[:4]:
                print("  -", h[:220])
