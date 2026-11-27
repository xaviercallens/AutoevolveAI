"""Mechanical fidelity check of the English edition against the French edition of the discovery journal.

For every pair of sources (main.tex, cadre/*.tex, chapters/c01..c20.tex) it extracts, after removing LaTeX comments,
ordered token sequences and compares them:
  dois      every Zenodo record number (doi:10.5281/zenodo.N, \\doi{...}, zenodo.N)
  numbers   every number in the text and in math, normalised (FR 1{,}5 / 1,5 -> 1.5; FR 1\\,685 / EN 1{,}685 / 1,685
            -> 1685), after removing layout dimensions, colour mixes, DOIs, labels, refs and file names
  percents  every number followed by a percent sign
  months    month names (FR mapped to EN)
  niveau    every \\niveau{...} badge
  refs      every \\ref{...}; labels: every \\label{...}
  figures   every \\includegraphics file name
  headings  (chapters only) the \\chapter title count and the five \\section* headings, mapped FR -> EN
A sequence pair is 'ok' when equal, 'order' when the multisets agree but the order differs, 'mismatch' otherwise.
The report lists the difflib opcodes of each non-ok pair so that a human or agent can resolve it by reading.
Usage: python -I code/fidelity_check.py   (any working directory). Writes fidelity_report.json next to main.tex.
Exit code 0 always (the report is a list of things to resolve, not a gate).
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from collections import Counter
from pathlib import Path

EN = Path(__file__).resolve().parents[1]
FR = EN.parent / "discovery_journal_2026"

MONTHS_FR = {
    "janvier": "January", "février": "February", "mars": "March", "avril": "April", "mai": "May", "juin": "June",
    "juillet": "July", "août": "August", "septembre": "September", "octobre": "October", "novembre": "November",
    "décembre": "December",
}
MONTHS_EN = set(MONTHS_FR.values())
HEADINGS = {
    "L'idée en une image": "The idea in one picture",
    "Ce qui a été fait": "What was done",
    "Comment on s'est assuré que ce n'est pas faux": "How we made sure it is not wrong",
    "Ce que ça ne dit pas": "What this does not say",
    "Pour aller plus loin": "Going further",
}


def strip_comments(tex: str) -> str:
    """Remove LaTeX comments (an unescaped % to the end of the line)."""
    return "\n".join(re.sub(r"(?<!\\)%.*", "", line) for line in tex.splitlines())


def dois(tex: str) -> list[str]:
    return re.findall(r"zenodo\.(?:\\allowbreak\s*)?(\d{6,})", tex)


def braced(tex: str, cmd: str) -> list[str]:
    return re.findall(r"\\" + cmd + r"\*?(?:\[[^\]]*\])?\{([^{}]*)\}", tex)


def figures(tex: str) -> list[str]:
    return [Path(f).stem for f in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^{}]*)\}", tex)]


def scrub_for_numbers(tex: str) -> str:
    """Remove the places where digits are not content: DOIs, labels, refs, files, dimensions, colour mixes."""
    t = re.sub(r"(?:doi:)?10\.5281/(?:\\allowbreak\s*)?zenodo\.(?:\\allowbreak\s*)?\d+", " ", tex)
    t = re.sub(r"zenodo\.\d+", " ", t)
    t = re.sub(r"\\(?:ref|label|pageref|includegraphics|input|doi|nolinkurl|url|href|niveau|definircontribution"
               r"|contribution)\*?(?:\[[^\]]*\])?\{[^{}]*\}", " ", t)
    t = re.sub(r"ch:c\d\d|\bc\d\d\b|egg_\w+|figures/\S+", " ", t)
    t = re.sub(r"-?\d+(?:\.\d+)?\s*(?:cm|mm|pt|em|ex|bp|sp)\b", " ", t)
    t = re.sub(r"![\d.]+", " ", t)  # colour mixes encre!70
    t = re.sub(r"\\(?:textls|fontsize|vspace|hspace|rule|arraystretch|setcounter|addtocounter)\*?(\[[^\]]*\])?"
               r"(\{[^{}]*\})*", " ", t)
    t = re.sub(r"\[[\d.,\s]*\]", " ", t)  # numeric optional args
    t = re.sub(r"\\[a-zA-Z]+", " ", t)  # macro names (keeps the digits that follow, e.g. \div1)
    return t


MATH_RE = re.compile(r"\$[^$]*\$|\\\[.*?\\\]", re.S)


def fr_math(m: re.Match) -> str:
    """In French math a bare comma separates list items; the decimal comma is written {,}."""
    return (m.group(0).replace("\\,", "\x01").replace("{,}", "\x00").replace(",", " , ")
            .replace("\x00", ".").replace("\x01", "\\,"))


def numbers(tex: str, lang: str) -> list[str]:
    t = scrub_for_numbers(tex)
    t = re.sub(r"\(\s*-?[\d.]+\s*,\s*-?[\d.]+\s*\)", " ", t)  # TikZ coordinates (x,y)
    if lang == "fr":
        t = MATH_RE.sub(fr_math, t)
    t = t.replace("{,}", ",").replace("\\,", "").replace("\\thinspace", "").replace("\u202f", "").replace("~", " ")
    t = re.sub(r"(\d)\{\}(\d)", r"\1\2", t)
    if lang == "fr":
        t = re.sub(r"(\d) (\d{3})(?!\d)", r"\1\2", t)  # thousands with a plain space after removing \,
        t = re.sub(r"(\d),(\d)", r"\1.\2", t)
    else:
        t = re.sub(r"(?<![\d.])(\d{1,3}(?:,\d{3})+)(?![\d,])", lambda m: m.group(1).replace(",", ""), t)
    out = []
    for m in re.finditer(r"\d+(?:\.\d+)?", t):
        s = m.group(0)
        out.append(s)
    return out


def percents(tex: str, lang: str) -> list[str]:
    t = scrub_for_numbers(tex).replace("{,}", ",").replace("\\,", "").replace("~", " ")
    if lang == "fr":
        t = re.sub(r"(\d),(\d)", r"\1.\2", t)
    return re.findall(r"(\d+(?:\.\d+)?)\s*(?:\\%|\bpour cent\b|\bper cent\b|\bpercent\b)", t)


def months(tex: str, lang: str) -> list[str]:
    if lang == "fr":
        return [MONTHS_FR[m.lower()] for m in re.findall(r"\b(" + "|".join(MONTHS_FR) + r")\b", tex, re.I)]
    return re.findall(r"\b(" + "|".join(MONTHS_EN) + r")\b", tex)


WORDS_FR = {"dix-sept": 17, "dix-huit": 18, "dix-neuf": 19, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5,
            "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10, "onze": 11, "douze": 12, "treize": 13,
            "quatorze": 14, "quinze": 15, "seize": 16, "vingt": 20, "trente": 30, "cent": 100, "mille": 1000}
WORDS_EN = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
            "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30, "hundred": 100,
            "thousand": 1000}


def number_words(tex: str, lang: str) -> list[str]:
    """Spelled-out cardinals 2..20, 30, 100, 1000 ('un/une/one' excluded: articles). FR 'neuf' may mean 'new'."""
    words = WORDS_FR if lang == "fr" else WORDS_EN
    pat = r"(?<!\w)(" + "|".join(sorted(words, key=len, reverse=True)) + r")(?!\w)"
    return [str(words[m.lower()]) for m in re.findall(pat, tex, re.I)]


def headings(tex: str, lang: str) -> list[str]:
    secs = braced(tex, "section")
    if lang == "fr":
        secs = [HEADINGS.get(s.strip(), "UNMAPPED:" + s.strip()) for s in secs]
    nchap = len(re.findall(r"\\chapter\*?[\[{]", tex))
    return [f"chapter x{nchap}"] + [s.strip() for s in secs]


def compare(a: list[str], b: list[str]) -> dict:
    if a == b:
        return {"status": "ok", "n": len(a)}
    status = "order" if Counter(a) == Counter(b) else "mismatch"
    ops = []
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            ops.append({"op": tag, "fr": a[i1:i2], "en": b[j1:j2], "fr_pos": i1, "en_pos": j1})
    return {"status": status, "n_fr": len(a), "n_en": len(b),
            "only_fr": sorted((Counter(a) - Counter(b)).elements()),
            "only_en": sorted((Counter(b) - Counter(a)).elements()), "diff": ops}


def check_pair(fr_path: Path, en_path: Path, is_chapter: bool) -> dict:
    return check_texts(fr_path.read_text(), en_path.read_text(), is_chapter)


def check_texts(fr_raw: str, en_raw: str, is_chapter: bool) -> dict:
    fr = strip_comments(fr_raw)
    en = strip_comments(en_raw)
    res = {
        "dois": compare(dois(fr), dois(en)),
        "numbers": compare(numbers(fr, "fr"), numbers(en, "en")),
        "percents": compare(percents(fr, "fr"), percents(en, "en")),
        "months": compare(months(fr, "fr"), months(en, "en")),
        "niveau": compare(braced(fr, "niveau"), braced(en, "niveau")),
        "refs": compare(braced(fr, "ref"), braced(en, "ref")),
        "labels": compare(braced(fr, "label"), braced(en, "label")),
        "doi_macro": compare(braced(fr, "doi"), braced(en, "doi")),
        "figures": compare(figures(fr), figures(en)),
        "number_words": compare(number_words(fr, "fr"), number_words(en, "en")),
    }
    if is_chapter:
        res["headings"] = compare(headings(fr, "fr"), headings(en, "en"))
    return res


CONTROL_MUTATIONS = [  # (check that must fire, old text in EN c13, new text)
    ("numbers", "478~seconds", "487~seconds"),
    ("numbers", "$\\lambda\\approx-6.73003$", "$\\lambda\\approx-6.73030$"),
    ("niveau", "The ten lemmas are \\niveau{A}", "The ten lemmas are \\niveau{As}"),
    ("dois", "zenodo.23656804", "zenodo.23656805"),
    ("months", "In September 2026", "In October 2026"),
    ("figures", "figures/c13_reproduction", "figures/c14_etapes"),
    ("headings", "\\section*{Going further}", "\\section*{Further reading}"),
]


NEUTRAL_MUTATIONS = [  # formatting-only changes in EN c14/c15 that must NOT fire (normalisation works)
    ("c14", "$1{,}685{,}129$", "$1685129$"),
    ("c15", "88,400", "88\\,400"),
    ("c13", "478~seconds", "478 seconds"),
]


def controls() -> dict:
    """Negative controls: the unmutated c13 pair and formatting-only edits stay 'ok'.
    Positive controls: each content mutation of EN c13 makes its own check fire."""
    fr = {c: (FR / "chapters" / f"{c}.tex").read_text() for c in ("c13", "c14", "c15")}
    en = {c: (EN / "chapters" / f"{c}.tex").read_text() for c in ("c13", "c14", "c15")}
    base = {k: v["status"] for k, v in check_texts(fr["c13"], en["c13"], True).items()}
    out: dict = {"baseline_c13_all_ok": all(v == "ok" for v in base.values()), "positive": [], "neutral": []}
    for key, old, new in CONTROL_MUTATIONS:
        if en["c13"].count(old) != 1:
            out["positive"].append({"check": key, "mutation": old, "fired": "NOT_APPLIED"})
            continue
        res = check_texts(fr["c13"], en["c13"].replace(old, new), True)
        out["positive"].append({"check": key, "mutation": f"{old} -> {new}", "fired": res[key]["status"] != "ok"})
    for chap, old, new in NEUTRAL_MUTATIONS:
        if en[chap].count(old) < 1:
            out["neutral"].append({"chapter": chap, "mutation": old, "all_ok": "NOT_APPLIED"})
            continue
        ref = {k: v["status"] for k, v in check_texts(fr[chap], en[chap], True).items()}
        res = {k: v["status"] for k, v in check_texts(fr[chap], en[chap].replace(old, new), True).items()}
        out["neutral"].append({"chapter": chap, "mutation": f"{old} -> {new}", "all_ok": res == ref})
    return out


def main() -> int:
    pairs: list[tuple[str, Path, Path, bool]] = [("main.tex", FR / "main.tex", EN / "main.tex", False)]
    for p in sorted((FR / "cadre").glob("*.tex")):
        pairs.append((f"cadre/{p.name}", p, EN / "cadre" / p.name, False))
    for p in sorted((FR / "gen").glob("*.tex")):
        pairs.append((f"gen/{p.name}", p, EN / "gen" / p.name, False))
    for i in range(1, 21):
        n = f"c{i:02d}.tex"
        pairs.append((f"chapters/{n}", FR / "chapters" / n, EN / "chapters" / n, True))
    report: dict[str, dict] = {}
    missing = []
    for name, f, e, chap in pairs:
        if not e.exists() or not f.exists():
            missing.append(name)
            continue
        report[name] = check_pair(f, e, chap)
    summary = {name: {k: v["status"] for k, v in r.items() if v["status"] != "ok"} for name, r in report.items()}
    summary = {k: v for k, v in summary.items() if v}
    ctl = controls()
    out = {"controls": ctl, "missing_files": missing, "non_ok_summary": summary, "details": report}
    (EN / "fidelity_report.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"controls": ctl, "missing_files": missing, "non_ok_summary": summary}, indent=1,
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
