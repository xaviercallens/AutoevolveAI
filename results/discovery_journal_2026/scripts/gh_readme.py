import json, re
B = "/home/callensxavier_gmail_com/AutoevolveAI/.scratchpad/gh_inv/"
E = json.load(open(B + "enriched.json"))
for n, e in E.items():
    rd = e.get("readme_head")
    if not rd:
        print("##", n, "NO README"); continue
    lines = [l.strip() for l in rd.splitlines() if l.strip() and not l.strip().startswith(("[![", "<", "![", "|", "```", "---"))]
    txt = " ".join(lines[:9])
    txt = re.sub(r"\s+", " ", txt)
    print("##", n, "::", txt[:520])
