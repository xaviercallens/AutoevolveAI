"""
Paper Ingestion Engine for ANSE Community Engine
Fetches, parses, and scores research papers from arXiv, Zenodo, and local user papers (papers/).
Inspired by HarborYuan/paper_agent and VikParuchuri/marker extraction patterns.
"""

import re
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
from defusedxml import ElementTree

from anse.community.config import DOMAIN_KEYWORDS, CommunityConfig, ResearchDomain


@dataclass
class PaperItem:
    title: str
    abstract: str
    authors: list[str] = field(default_factory=list)
    source_url: str = ""
    doi: str = ""
    source_type: str = "arxiv"  # 'arxiv', 'zenodo', 'local'
    published_date: str = ""
    local_path: str = ""
    matched_domains: list[ResearchDomain] = field(default_factory=list)
    relevance_score: float = 0.0
    key_findings: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "abstract": self.abstract[:300] + "..." if len(self.abstract) > 300 else self.abstract,
            "authors": self.authors,
            "source_url": self.source_url,
            "doi": self.doi,
            "source_type": self.source_type,
            "published_date": self.published_date,
            "local_path": self.local_path,
            "matched_domains": [d.value for d in self.matched_domains],
            "relevance_score": round(self.relevance_score, 3),
            "key_findings": self.key_findings,
            "limitations": self.limitations,
        }


def _get_xml_text(elem: Any | None, default: str = "") -> str:
    """Helper to safely extract stripped text from XML element."""
    if elem is not None and getattr(elem, "text", None):
        return elem.text.replace("\n", " ").strip()
    return default


def _parse_arxiv_entry(entry: Any, ns: dict[str, str]) -> PaperItem:
    """Helper to parse a single arXiv Atom XML entry."""
    title = _get_xml_text(entry.find("atom:title", ns))
    abstract = _get_xml_text(entry.find("atom:summary", ns))
    source_url = _get_xml_text(entry.find("atom:id", ns))
    pub_date = _get_xml_text(entry.find("atom:published", ns))

    authors: list[str] = []
    for a in entry.findall("atom:author", ns):
        name = _get_xml_text(a.find("atom:name", ns))
        if name:
            authors.append(name)

    return PaperItem(
        title=title,
        abstract=abstract,
        authors=authors,
        source_url=source_url,
        source_type="arxiv",
        published_date=pub_date,
    )


def _extract_tex_meta(content: str) -> tuple[str, str]:
    title_match = re.search(r"\\title\{([^}]+)\}", content)
    title = title_match.group(1).replace("\n", " ").strip() if title_match else ""
    abstract_match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", content, re.DOTALL)
    abstract = abstract_match.group(1).replace("\n", " ").strip() if abstract_match else ""
    return title, abstract


def _extract_md_meta(content: str) -> tuple[str, str]:
    title = ""
    abstract = ""
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    for line in lines:
        if line.startswith("# "):
            title = line.replace("# ", "").strip()
            break
    for line in lines:
        if not line.startswith("#") and len(line) > 60:
            abstract = line
            break
    return title, abstract


def _parse_local_paper_file(filepath: Path) -> PaperItem | None:
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        if filepath.suffix == ".tex":
            title, abstract = _extract_tex_meta(content)
        elif filepath.suffix == ".md":
            title, abstract = _extract_md_meta(content)
        else:
            title, abstract = "", ""

        if not title:
            title = filepath.stem.replace("_", " ").title()

        pdf_path = filepath.with_suffix(".pdf")
        has_pdf = pdf_path.exists()

        return PaperItem(
            title=title,
            abstract=abstract or f"ANSE research paper in {filepath.name}",
            authors=["ANSE Research Team / Xavier Callens"],
            source_url=f"local://papers/{filepath.name}",
            source_type="local",
            local_path=str(pdf_path if has_pdf else filepath),
        )
    except Exception:
        return None


class PaperIngestionEngine:
    def __init__(self, config: CommunityConfig | None = None) -> None:
        self.config = config or CommunityConfig()

    def search_arxiv(self, query: str, max_results: int = 5) -> list[PaperItem]:
        """
        Query arXiv API and parse Atom XML entries.
        """
        encoded_query = urllib.parse.quote(query)
        url = f"{self.config.arxiv_api_base}?search_query=all:{encoded_query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"

        try:
            with httpx.Client(timeout=15.0, headers={"User-Agent": self.config.reddit_user_agent}) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    return []
                data = resp.content

            root = ElementTree.fromstring(data)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items: list[PaperItem] = []

            for entry in root.findall("atom:entry", ns):
                paper = _parse_arxiv_entry(entry, ns)
                self.score_paper(paper)
                items.append(paper)

            return items
        except Exception:
            return []

    def search_zenodo(self, query: str, max_results: int = 5) -> list[PaperItem]:
        """
        Query Zenodo REST API for scientific publications and datasets.
        """
        params: dict[str, str | int] = {
            "q": query,
            "size": max_results,
            "sort": "mostrecent",
            "status": "published",
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.get(self.config.zenodo_api_base, params=params)
                if resp.status_code != 200:
                    return []
                data = resp.json()

            hits = data.get("hits", {}).get("hits", [])
            items: list[PaperItem] = []

            for hit in hits:
                meta = hit.get("metadata", {})
                title = meta.get("title", "")
                abstract = meta.get("description", "")
                # Clean html tags from abstract
                clean_abstract = re.sub(r"<[^>]+>", " ", abstract).replace("\n", " ").strip()
                doi = hit.get("doi", "") or meta.get("doi", "")
                doi_url = hit.get("links", {}).get("doi", f"https://doi.org/{doi}" if doi else "")
                pub_date = meta.get("publication_date", "")

                creators = [c.get("name", "") for c in meta.get("creators", []) if c.get("name")]

                paper = PaperItem(
                    title=title,
                    abstract=clean_abstract,
                    authors=creators,
                    source_url=doi_url,
                    doi=doi,
                    source_type="zenodo",
                    published_date=pub_date,
                )
                self.score_paper(paper)
                items.append(paper)

            return items
        except Exception:
            return []

    def parse_local_paper(self, filepath: Path) -> PaperItem | None:
        """Parses and scores a single local paper file."""
        paper = _parse_local_paper_file(filepath)
        if paper is not None:
            self.score_paper(paper)
        return paper

    def scan_local_papers(self, papers_dir: str | None = None) -> list[PaperItem]:
        """
        Scans local ANSE papers/ directory for PDFs, LaTeX, and Markdown preprints.
        Enables grounded dissemination of author's own research.
        """
        base_dir = Path(papers_dir or self.config.papers_dir)
        if not base_dir.exists():
            return []

        discovered: list[PaperItem] = []

        for filepath in base_dir.glob("**/*"):
            if filepath.suffix in [".tex", ".md"] and not filepath.name.startswith("."):
                paper = _parse_local_paper_file(filepath)
                if paper is not None:
                    self.score_paper(paper)
                    discovered.append(paper)

        return discovered

    def score_paper(self, paper: PaperItem) -> float:
        """
        Scores paper relevance against the 7 target domains.
        Inspired by HarborYuan/paper_agent novelty and keyword scoring.
        """
        text = f"{paper.title} {paper.abstract}".lower()
        matched: list[ResearchDomain] = []
        domain_hits: dict[ResearchDomain, int] = {}

        for domain, keywords in DOMAIN_KEYWORDS.items():
            hits = sum(1 for kw in keywords if re.search(r"\b" + re.escape(kw) + r"\b", text))
            if hits > 0:
                domain_hits[domain] = hits
                matched.append(domain)

        paper.matched_domains = matched

        if not domain_hits:
            paper.relevance_score = 0.05
            return 0.05

        total_hits = sum(domain_hits.values())
        # Normalized score between 0.2 and 1.0 based on keyword density
        score = min(1.0, 0.2 + (total_hits * 0.12))
        paper.relevance_score = score
        return score

    def extract_paper_markdown(self, file_path: str) -> str:
        """
        High-fidelity text extractor.
        Preserves equations and structure, following Marker patterns.
        """
        path = Path(file_path)
        if not path.exists():
            return ""

        if path.suffix in [".tex", ".md", ".txt"]:
            return path.read_text(encoding="utf-8", errors="ignore")

        if path.suffix == ".pdf":
            try:
                import pypdf
                reader = pypdf.PdfReader(str(path))
                text_parts = []
                for i, page in enumerate(reader.pages[:10]):  # First 10 pages
                    extracted = page.extract_text()
                    if extracted:
                        text_parts.append(f"--- Page {i+1} ---\n{extracted}")
                return "\n\n".join(text_parts)
            except Exception as e:
                return f"[PDF extraction fallback: {e}]"

        return ""
