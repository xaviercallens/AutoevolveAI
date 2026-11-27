"""Comment-stripped, whitespace-normalised diff of two Lean files (code only)."""
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from source_scan import strip_comments_and_strings  # noqa: E402


def norm(p: str) -> list[str]:
    code = strip_comments_and_strings(Path(p).read_text(encoding="utf-8"))
    return [" ".join(l.split()) for l in code.splitlines() if l.strip()]


a, b = norm(sys.argv[1]), norm(sys.argv[2])
for line in difflib.unified_diff(a, b, sys.argv[1], sys.argv[2], n=1, lineterm=""):
    print(line)
