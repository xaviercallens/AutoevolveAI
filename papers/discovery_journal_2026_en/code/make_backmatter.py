"""Generate the data-driven LaTeX pieces of the English edition of "The Discovery Journal".

Sources: results/discovery_journal_2026/TOP20_final.json (ranks, DOIs, dates, lessons, rubric scores) and the French
edition's papers/discovery_journal_2026/chapters/ORDER.json (which chapter file holds which rank). The English edition
keeps exactly the same file stems and the same order, so the label ch:cNN always points at chapters/cNN.tex.

English chapter titles: when chapters/cNN.tex exists in this edition, the title is read from its \\chapter[..]{..}
command (the long title, braces matched), so that the table of contents, the part openers and the tables always agree
with the chapter itself. Until a chapter arrives, the fallback title below is used (a plain translation of the French
chapter title).

Writes, under papers/discovery_journal_2026_en/gen/:
  titres.tex   -- \\definircontribution{file stem}{rank}{English title}{domain}{id};
  table20.tex  -- the table of the 20 contributions (rank, title with its DOI or repository underneath, field,
                  rigour score), two halves, set at the text width;
  dois.tex     -- the DOI index of the 20 (every DOI listed in TOP20_final.json, with its rank).
  titles_source.json -- for each stem, whether its title came from the chapter file or from the fallback.
The 'rigour' column prints the rubric's C1 score as is (0-3); the Elenchus badges stay in the chapters.
Usage: python -I code/make_backmatter.py   (from any directory)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BOOK = Path(__file__).resolve().parents[1]
TOP20 = ROOT / "results" / "discovery_journal_2026" / "TOP20_final.json"
ORDER = ROOT / "papers" / "discovery_journal_2026" / "chapters" / "ORDER.json"

DOMAINS_EN: dict[str, str] = {
    "cosmology": "cosmology",
    "physics": "physics",
    "genetics/biology": "genetics, biology",
    "mathematics": "mathematics",
    "numerics/software": "numerical computing",
    "AI methodology/verification": "method, verification",
    "education/textbook": "teaching",
}

# Fallback English titles, keyed by file stem (translations of ORDER.json's French chapter_title).
FALLBACK_TITLES: dict[str, str] = {
    "c01": "Cosmic distances with an error margin checked by a machine",
    "c02": "A famous tension in cosmology, written as a checked inequality",
    "c03": "The triangle, the cheapest arrangement: checked consequences and a simulation",
    "c04": "Screened repulsion joins the theorem's family, and a mistake is repaired",
    "c05": "A rule proved straight shows that our own sketch was wrong",
    "c06": "What chance does a mutation have of taking over a population?",
    "c07": "When the seating plan changes nothing for selection",
    "c08": "A textbook for following a theorem all the way to the laboratory",
    "c09": "Electron--hole pairs that line up in triangles, on paper",
    "c10": "The force in an atomically thin semiconductor, as a sand pile",
    "c11": "Perfect at rest, not when it shivers",
    "c12": "Test before you prove: a natural idea that does not hold",
    "c13": "Redoing someone else's calculation, without declaring it right",
    "c14": "Four stages out of twelve, and the price of the rest",
    "c15": "Rebuilding other people's machine in your own workshop",
    "c16": "One general guarantee, three precise certificates",
    "c17": "The engine of the calculations, and its inspection report",
    "c18": "A gate that stays shut when we do not know",
    "c19": "The test bench that inspected itself",
    "c20": "The thermostat was accused of overheating",
}


def tex_escape(text: str) -> str:
    """Escape the LaTeX specials that may occur in a fallback title (titles may already carry ~ and --)."""
    return text.replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")


def braced(text: str, start: int, open_ch: str, close_ch: str) -> tuple[str, int]:
    """Return the content of the group opening at text[start] (== open_ch), nesting-aware, and the index after it."""
    if text[start] != open_ch:
        raise ValueError(f"expected {open_ch!r} at {start}")
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == open_ch and (i == start or text[i - 1] != "\\"):
            depth += 1
        elif ch == close_ch and text[i - 1] != "\\":
            depth -= 1
            if depth == 0:
                return text[start + 1:i], i + 1
    raise ValueError("unbalanced group")


def chapter_title(path: Path) -> str | None:
    """Long title of the first uncommented \\chapter command in a chapter file, or None if there is none."""
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if not ln.lstrip().startswith("%")]
    text = "\n".join(lines)
    m = re.search(r"\\chapter\*?\s*", text)
    if not m:
        return None
    pos = m.end()
    if pos < len(text) and text[pos] == "[":
        _, pos = braced(text, pos, "[", "]")
        while pos < len(text) and text[pos].isspace():
            pos += 1
    if pos >= len(text) or text[pos] != "{":
        return None
    title, _ = braced(text, pos, "{", "}")
    title = re.sub(r"\\reference\{.*", "", title).strip()  # never carry a margin note into the TOC
    return " ".join(title.split()) or None


def doi_or_repo(pick: dict) -> str:
    """Primary DOI if the pick has one, otherwise its public repository name."""
    doi = pick.get("primary_doi")
    if doi:
        return "\\doi{" + doi + "}"
    names = [r["name"] for r in pick.get("repos", []) if r.get("visibility") == "PUBLIC"]
    if not names:
        raise SystemExit(f"{pick['id']}: no DOI and no public repository")
    return "repository \\texttt{" + names[0].replace("_", "\\_") + "}"


def main() -> None:
    picks = sorted(json.loads(TOP20.read_text())["picks"], key=lambda p: p["pick"])
    if [p["pick"] for p in picks] != list(range(1, 21)):
        raise SystemExit("TOP20_final.json does not hold ranks 1..20")
    order = {o["rank"]: o for o in json.loads(ORDER.read_text())["order"]}
    for p in picks:
        o = order.get(p["pick"])
        if o is None or o["id"] != p["id"]:
            raise SystemExit(f"ORDER.json and TOP20_final.json disagree at rank {p['pick']}")
    stems = [Path(order[p["pick"]]["file"]).stem for p in picks]
    if len(set(stems)) != 20 or set(stems) != set(FALLBACK_TITLES):
        raise SystemExit("chapter stems in ORDER.json do not match c01..c20 one to one")

    titles: dict[str, str] = {}
    source: dict[str, str] = {}
    for stem in stems:
        path = BOOK / "chapters" / f"{stem}.tex"
        found = chapter_title(path) if path.exists() else None
        if found:
            titles[stem], source[stem] = found, "chapter file"
        else:
            titles[stem], source[stem] = tex_escape(FALLBACK_TITLES[stem]), "fallback"
            if not path.exists():
                print(f"warning: chapters/{stem}.tex missing, placeholder chapter will be used")

    out = BOOK / "gen"
    out.mkdir(exist_ok=True)
    stamp = "% generated by code/make_backmatter.py from TOP20_final.json and ORDER.json -- do not edit"

    lines = [stamp]
    for p, stem in zip(picks, stems):
        lines.append(
            f"\\definircontribution{{{stem}}}{{{p['pick']}}}{{{titles[stem]}}}{{{DOMAINS_EN[p['domain']]}}}{{{p['id']}}}"
        )
    (out / "titres.tex").write_text("\n".join(lines) + "\n")

    head = [
        # Text width only (no margin overhang): an overhang decided on the wrong page side clipped the table (audit B1).
        "\\begin{tabularx}{\\linewidth}{@{}r>{\\raggedright\\arraybackslash}X"
        ">{\\raggedright\\arraybackslash}p{2.3cm}c@{}}",
        "\\toprule",
        "\\textsf{No.} & \\textsf{contribution (chapter title), DOI or repository} & \\textsf{field} & "
        "\\textsf{rigour}\\\\",
        "\\midrule",
    ]
    rows = [stamp] + head
    for p, stem in zip(picks, stems):
        if p["pick"] == 11:  # two tables of ten rows, so that each fits on a page
            rows += ["\\bottomrule", "\\end{tabularx}", "", "\\bigskip", ""] + head
        rigour = p["score_breakdown"]["c1_rigour"]  # rubric C1 score, printed as is (badges live in the chapters)
        lesson = " \\emph{(lesson)}" if p["lesson"] else ""
        rows.append(
            f"{p['pick']} & {titles[stem]}{lesson} \\newline "
            f"{{\\scriptsize\\color{{encre!60}}{p['date']}, p.~\\pageref{{ch:{stem}}}}} "
            f"\\newline{{\\footnotesize {doi_or_repo(p)}}} & "
            f"{DOMAINS_EN[p['domain']]} & {{\\sffamily\\small {rigour}\\,/\\,3}}\\\\"
        )
    rows += ["\\bottomrule", "\\end{tabularx}"]
    (out / "table20.tex").write_text("\n".join(rows) + "\n")

    dois = [stamp, "\\begin{description}"]
    for p, stem in zip(picks, stems):
        entry = ", ".join("\\doi{" + d + "}" for d in p["all_dois"]) or doi_or_repo(p)
        title = titles[stem]
        sep = "" if title.rstrip().endswith(("?", "!", ".")) else "."
        dois.append(f"\\item[No.\\,{p['pick']}] {title}{sep} {{\\footnotesize {entry}}}")
    dois.append("\\end{description}")
    (out / "dois.tex").write_text("\n".join(dois) + "\n")
    (out / "titles_source.json").write_text(json.dumps(source, indent=1) + "\n")
    n_file = sum(1 for v in source.values() if v == "chapter file")
    print(f"wrote {len(picks)} picks to {out} ({n_file} titles read from chapter files, {20 - n_file} fallback)")


if __name__ == "__main__":
    main()
