"""Report page-cache residency of the files listed (one path per line) using fincore."""
import subprocess
import sys

paths = sorted({p.strip() for p in open(sys.argv[1]) if p.strip()})
tot_res = 0
tot_size = 0
worst = []
for i in range(0, len(paths), 500):
    out = subprocess.run(["fincore", "-b", "-n", "-o", "RES,SIZE,FILE"] + paths[i:i + 500],
                         capture_output=True, text=True).stdout
    for line in out.splitlines():
        parts = line.split(None, 2)
        if len(parts) == 3:
            r, s = int(parts[0]), int(parts[1])
            tot_res += r
            tot_size += s
            if s > 0 and r < s:
                worst.append((s - r, parts[2]))
worst.sort(reverse=True)
print("resident MB", tot_res // 2**20, "of", tot_size // 2**20)
for w in worst[:8]:
    print(w[0] // 1024, "KB missing", w[1])
