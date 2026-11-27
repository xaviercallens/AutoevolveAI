"""One-off text corrections for the K1 v2 revision (advisor review): exact string replacements, each asserted to occur.

Usage: python -I fix_text_v2.py <paper dir> <results K1 dir>
"""

from __future__ import annotations

import sys
from pathlib import Path


def rep(p: Path, old: str, new: str, count: int | None = None) -> None:
    s = p.read_text()
    n = s.count(old)
    if n == 0 or (count is not None and n != count):
        raise SystemExit(f"{p.name}: {old[:60]!r} found {n} times")
    p.write_text(s.replace(old, new))


def main() -> int:
    paper, res = Path(sys.argv[1]), Path(sys.argv[2])
    tex = paper / "main.tex"
    rev = paper / "REVISION.md"
    meta = paper / "publication_meta.json"
    # 3: sign -> existence
    rep(tex, "but its size, and at full recovery its sign, depend on how the cost of chilling the feed air is priced.",
        "but its size, and at full recovery its existence, depend on how the cost of chilling the feed air is priced.")
    rep(meta, "but its size, and at full recovery its sign, depend on", "but its size, and at full recovery its existence, depend on")
    # 4: 9-18 -> 9-19
    rep(tex, "are $9$--$18\\%$ lower in our scan", "are $9$--$19\\%$ lower in our scan")
    rep(rev, "9–18 % lower", "9–19 % lower")
    # 5: not a paired test
    rep(tex, "less than each row's own printed $\\xi$ uncertainty;", "less than each row's own printed $\\xi$ uncertainty (not a paired test);")
    rep(tex, "less than each row's own printed $\\xi$ uncertainty ($0.7$--$8.5\\%$): a tie at the model's own precision.",
        "less than each row's own printed $\\xi$ uncertainty ($0.7$--$8.5\\%$; a marginal posterior spread, so this is not a paired test): a tie at the model's own precision.")
    # 2: survival scoped to ideal machines
    rep(tex, "The cold start survives every priced scenario only for VANNIK (two rows) and LETQAE01.",
        "With ideal machines, the cold start survives every feed-air pricing ($\\varepsilon\\in[0,1]$, every $r$) only for VANNIK (two rows) and LETQAE01; with a degraded refrigerator and the air priced even these lose (VANNIK below $\\eta_R\\approx0.29$ at $r=0$).")
    rep(rev, "- Only VANNIK ×2 and LETQAE01 survive every priced scenario.",
        "- With ideal machines, only VANNIK ×2 and LETQAE01 keep a cold start for every ε and r. With a degraded\n  refrigerator and the air priced, even these lose (VANNIK below η_R ≈ 0.29 at r = 0).")
    # 6: bibliography
    rep(tex, "NIST software licensing statement; read, not redistributed.",
        "NIST software licensing statement; read; not redistributed in this paper's bundle (its tarball was in the public repository's history, Section~\\ref{sec:licence}).")
    # 1: shell lapses, exact
    rep(tex, "During the v2 revision: three read-only commands were compound \\texttt{cd X; \\ldots} commands, two used \\texttt{echo} or \\texttt{mkdir}/\\texttt{cp} chained with \\texttt{;},",
        "During the v2 revision: about 13 commands were compound \\texttt{cd X; \\ldots} or \\texttt{cd X \\&\\& \\ldots} commands (all read-only inspections except one, which ran the first \\texttt{pdflatex} build and wrote its outputs), about 8 used \\texttt{git -C} (read-only: \\texttt{rev-parse}, \\texttt{log}, \\texttt{branch -r}, \\texttt{show}, \\texttt{ls-files}, \\texttt{status}), several chained \\texttt{echo}, \\texttt{mkdir} or \\texttt{cp} with \\texttt{;},")
    rep(tex, "no variable, loop or heredoc was used and none touched git.",
        "no shell variable, loop or heredoc was used and no command changed git state.")
    rep(rev, "  - Three early read-only commands were compound `cd X; …`.\n  - Two chained `mkdir`/`cp`/`echo` with `;`.",
        "  - About 13 commands were compound `cd X; …` or `cd X && …`. All were read-only except one, the first\n    `cd … && pdflatex` build, which wrote the build outputs.\n  - About 8 used `git -C`, all read-only (`rev-parse`, `log`, `branch -r`, `show`, `ls-files`, `status`). The brief\n    banned this.\n  - Several chained `mkdir`/`cp`/`echo` with `;`.")
    rep(rev, "  - No shell variables, loops or heredocs were used, and none of these commands touched git.",
        "  - No shell variables, loops or heredocs were used, and no command changed git state.")
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
