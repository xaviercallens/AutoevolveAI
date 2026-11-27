"""Write the distinct .olean paths mapped by a process (argv[1] = pid) to argv[2], for cache warming."""
import sys

pid, out = sys.argv[1], sys.argv[2]
paths: set[str] = set()
with open(f"/proc/{pid}/maps") as fh:
    for line in fh:
        parts = line.split()
        if len(parts) >= 6 and parts[-1].endswith(".olean"):
            paths.add(parts[-1])
with open(out, "w") as fh:
    fh.write("\n".join(sorted(paths)) + "\n")
print(len(paths), "olean paths")
