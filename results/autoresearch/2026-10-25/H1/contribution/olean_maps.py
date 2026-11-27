"""Write the .olean paths mapped by the given Lean PIDs (from /proc/PID/maps) to an output file, one per line."""
from __future__ import annotations

import sys


def main() -> int:
    out, pids = sys.argv[1], sys.argv[2:]
    paths: set[str] = set()
    for pid in pids:
        try:
            with open(f"/proc/{pid}/maps") as fh:
                for line in fh:
                    parts = line.split()
                    if len(parts) >= 6 and ".olean" in parts[5]:
                        paths.add(parts[5])
        except OSError:
            continue
    with open(out, "w") as fh:
        fh.write("\n".join(sorted(paths)) + "\n")
    print(len(paths), "olean paths")
    return 0


if __name__ == "__main__":
    sys.exit(main())
