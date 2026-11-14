"""Extract the .olean paths mapped by a running lean process (for cache warming)."""
import sys

pid, out = sys.argv[1], sys.argv[2]
paths = set()
for line in open(f"/proc/{pid}/maps"):
    parts = line.split()
    if len(parts) >= 6 and ".olean" in parts[5]:
        paths.add(parts[5])
with open(out, "w") as fh:
    fh.write("\n".join(sorted(paths)) + "\n")
print(len(paths), "olean paths")
