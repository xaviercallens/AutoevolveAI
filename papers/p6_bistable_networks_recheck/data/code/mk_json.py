import hashlib, json, os
root = ".."
files = {}
for d, _, fs in os.walk(root):
    for f in sorted(fs):
        p = os.path.join(d, f)
        if f == "result.json" or "__pycache__" in p:
            continue
        files[os.path.relpath(p, root)] = hashlib.sha256(open(p, "rb").read()).hexdigest()
json.dump(dict(item="BIO-BISTAB", outcome="PARTIAL", claim="arXiv 2610.32739", orbits=681, witnesses_verified=27, jac=245, div=216,
               root_reproduced_my_reading=105, flux_reproduced=0, search_samples=85125000, negatives_with_hits=0,
               sha256=files), open("../result.json", "w"), indent=1)
print(len(files))
