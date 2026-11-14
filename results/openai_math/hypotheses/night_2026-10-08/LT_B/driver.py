import datetime
import os
import subprocess
import time

os.environ.update(OMP_NUM_THREADS="2", MKL_NUM_THREADS="2", OPENBLAS_NUM_THREADS="2")
ROOT = "/home/callensxavier_gmail_com/AutoevolveAI/.claude/worktrees/openai-math-discovery"
LANE = ROOT + "/results/openai_math/hypotheses/night_2026-10-08/LT_B"
PY = "/usr/bin/python3"
LC = ROOT + "/scripts/openai_math/lt_matrix/"
G = {0.75: (14, 360, 1600), 1.0: (14, 200, 1600), 1.25: (14, 160, 1600), 1.4: (14, 160, 1600), 3.0: (40, 240, 2000)}
STOP = "19:00"


def p1(cell, gamma, fam, seed0):
    jobs = []
    for k in range(4):
        out = f"{LANE}/part1/{cell}_call{k}.json"
        jobs.append((out, [PY, LC + "campaign.py", "--gamma", str(gamma), "--m", "3", "--family", fam, "--K", "2",
                           "--P", "8", "--seed0", str(seed0 + 2 * k), "--restarts", "2", "--budget-s", "450",
                           "--threads", "2", "--out", out]))
    return jobs


def p2(gamma, m, neg=False):
    L, M, Q = G[gamma]
    out = f"{LANE}/part2/g{gamma}_m{m}.json"
    cmd = [PY, LC + "second_variation.py", "--gamma", str(gamma), "--m", str(m), "--P", "8", "--L", str(L),
           "--M", str(M), "--Q", str(Q), "--threads", "2", "--out", out]
    if neg:
        cmd.append("--negative-control")
    return [(out, cmd)]


jobs = p1("control_gamma1.5_m3", 1.5, "random", 2000)
for g in (1.0, 1.25, 1.4, 0.75):
    jobs += p2(g, 1)
jobs += p2(3.0, 1, True) + p2(3.0, 2, True)
for g in (1.0, 1.25, 1.4, 0.75):
    jobs += p2(g, 2)
for cell, g, fam, s in [("g1.0_random", 1.0, "random", 2100), ("g1.0_embed", 1.0, "embed", 2200),
                        ("g1.0_twist", 1.0, "twist", 2300), ("g1.25_random", 1.25, "random", 2400),
                        ("g1.25_embed", 1.25, "embed", 2500), ("g1.25_twist", 1.25, "twist", 2600)]:
    jobs += p1(cell, g, fam, s)
for g in (1.25, 1.0, 1.4, 0.75):
    jobs += p2(g, 3)
os.makedirs(LANE + "/part1", exist_ok=True)
os.makedirs(LANE + "/part2", exist_ok=True)
log = open(LANE + "/driver.log", "a")
for out, cmd in jobs:
    if os.path.exists(out):
        continue
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")
    if "11:00" <= now < "23:59" and now >= STOP:
        log.write(f"{now} STOP time reached, remaining jobs BLOCKED (first: {out})\n")
        log.flush()
        break
    t = time.time()
    log.write(f"{now} START {out}\n")
    log.flush()
    with open(out + ".log", "w") as lf:
        rc = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT).returncode
    log.write(f"  END rc={rc} {time.time() - t:.0f}s {out}\n")
    log.flush()
log.write("DRIVER DONE\n")
log.flush()
