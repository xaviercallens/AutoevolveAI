import glob
import hashlib
import json
import os

HERE = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery/results/proposal6/2026-11-03/AIC-MUC9"
os.chdir(HERE)


def sh(p: str) -> str:
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


m = json.load(open("data/main_results.json"))
files = {p: sh(p) for p in sorted(glob.glob("**/*", recursive=True))
         if os.path.isfile(p) and p != "result.json" and "__pycache__" not in p}
out = {
    "item": "AIC-MUC9",
    "outcome": "CONFIRMED (finite checks A1-A10, tiers C/X); LP optimum equals 147/157 (tier X); refutation of conjecture and amplification are tier L",
    "recheck_of": "arXiv 2610.10108v1 (Braverman, He); own code; authors' verifier not run",
    "construction_hashes": m["hashes"],
    "checks": {k: m[k].get("PASS") for k in m if k.startswith("A") and isinstance(m[k], dict)},
    "key_numbers": {"dim_W": 166, "dim_W_C": 157, "E_after": 735, "sum_dist": 785, "all_dist": 5, "bound": "147/157",
                    "lp_optimum": 0.9363057324840819, "trials": "1000/1000 + 157 unit inputs"},
    "thirdparty_transcription_sha256": sh("/home/callensxavier_gmail_com/muc9_thirdparty/appendixA_transcribed.py"),
    "thirdparty_location": "/home/callensxavier_gmail_com/muc9_thirdparty/ (not in repo)",
    "file_sha256": files,
}
json.dump(out, open("result.json", "w"), indent=1)
print(len(files))
