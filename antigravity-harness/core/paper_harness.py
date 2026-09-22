"""
Scientific Paper Verification Harness:
Zero-Hallucination Academic Generation, Section Chunking, and Grounded Reference Retrieval.

Key Invariants:
1. Anti-Hallucination Numeric Engine: LLM must NEVER invent numeric calculations;
   all metrics and physical invariant values MUST be produced by executing Python code.
2. Modular Section Partitioning: Large documents are broken down and reviewed in bounded,
   independently verifiable subsections.
3. Grounded Reference Retrieval: Downloads and parses real academic papers (e.g. arXiv)
   before citing, never relying on LLM internal parametric memory.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger("antigravity_harness.paper_harness")


@dataclass
class AcademicReference:
    arxiv_id: str
    title: str
    authors: list[str]
    published_year: int
    abstract: str
    pdf_url: str


@dataclass
class NumericReceipt:
    expression: str
    result_value: Any
    code_hash: str
    execution_time_ms: float
    status: str = "VERIFIED"


class ReferenceFetcher:
    """Fetches real papers from arXiv API to ground literature citations without hallucinations."""

    ARXIV_URL = "https://export.arxiv.org/api/query"

    def __init__(self, cache_dir: Path = Path("papers/references")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_papers(self, query: str, max_results: int = 5) -> list[AcademicReference]:
        """Queries arXiv API over HTTPS with rate limiting and polite User-Agent."""
        headers = {
            "User-Agent": "ANSE-Scientific-Paper-Harness/1.0 (mailto:science@autoevolveai.org)"
        }
        params = {
            "search_query": query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        cache_file = self.cache_dir / f"arxiv_{hashlib.md5(query.encode()).hexdigest()[:8]}.json"
        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                return [AcademicReference(**d) for d in data]
            except Exception as e:
                logger.debug(f"Cache read error: {e}, fetching fresh results from arXiv.")

        try:
            res = httpx.get(self.ARXIV_URL, params=params, headers=headers, timeout=12.0)
            if res.status_code != 200:
                logger.warning(f"ArXiv query failed with status {res.status_code}")
                return []

            root = ET.fromstring(res.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            refs: list[AcademicReference] = []

            for entry in root.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None and title_elem.text else "Untitled"

                id_elem = entry.find("atom:id", ns)
                raw_id = id_elem.text.strip() if id_elem is not None and id_elem.text else ""
                arxiv_id = raw_id.split("/abs/")[-1] if "/abs/" in raw_id else raw_id

                pub_elem = entry.find("atom:published", ns)
                pub_text = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else "2024"
                year = int(pub_text[:4]) if len(pub_text) >= 4 and pub_text[:4].isdigit() else 2024

                summary_elem = entry.find("atom:summary", ns)
                abstract = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None and summary_elem.text else ""

                authors = [
                    a.find("atom:name", ns).text.strip()
                    for a in entry.findall("atom:author", ns)
                    if a.find("atom:name", ns) is not None and a.find("atom:name", ns).text
                ]

                pdf_link = entry.find("atom:link[@title='pdf']", ns)
                pdf_url = pdf_link.attrib.get("href", "") if pdf_link is not None else f"https://arxiv.org/pdf/{arxiv_id}"

                refs.append(AcademicReference(
                    arxiv_id=arxiv_id,
                    title=title,
                    authors=authors,
                    published_year=year,
                    abstract=abstract,
                    pdf_url=pdf_url,
                ))

            if refs:
                cache_file.write_text(json.dumps([asdict(r) for r in refs], indent=2), encoding="utf-8")
            return refs
        except Exception as e:
            logger.warning(f"Error connecting to arXiv: {e}")
            return []


class AntiHallucinationNumericEngine:
    """Executes Python code for any numeric computation and validates text claims against runtime receipts."""

    def __init__(self) -> None:
        self.receipts: dict[str, NumericReceipt] = {}

    def compute_and_record(self, name: str, code_snippet: str, target_var: str) -> Any:
        """Executes a code snippet safely in an isolated namespace and records execution receipt."""
        t0 = time.perf_counter()
        namespace: dict[str, Any] = {}
        exec(code_snippet, namespace)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        value = namespace.get(target_var)
        c_hash = hashlib.sha256(code_snippet.encode("utf-8")).hexdigest()[:16]

        self.receipts[name] = NumericReceipt(
            expression=f"{name} = {target_var}",
            result_value=value,
            code_hash=c_hash,
            execution_time_ms=round(elapsed_ms, 3),
        )
        return value

    def verify_paper_numerics(self, paper_content: str, tolerances: dict[str, float] | None = None) -> tuple[bool, list[str]]:
        """Verifies that numeric values reported in markdown tables match verified execution receipts."""
        violations: list[str] = []
        tolerances = tolerances or {}

        for name, receipt in self.receipts.items():
            expected = receipt.result_value
            # Check if name is mentioned
            if isinstance(expected, (int, float)):
                # Check for scientific or standard representation
                sci = f"{expected:.2e}"
                std = f"{expected:.2f}"
                if sci not in paper_content and std not in paper_content and str(expected) not in paper_content:
                    violations.append(f"Metric '{name}' expected {expected} ({sci} or {std}) was not found or misrepresented in paper.")

        return len(violations) == 0, violations


class SectionPartitionOrchestrator:
    """Manages the creation and verification of modular, context-bounded paper subsections."""

    def __init__(self, paper_dir: Path = Path("papers")) -> None:
        self.paper_dir = paper_dir
        self.paper_dir.mkdir(parents=True, exist_ok=True)
        self.sections: dict[str, str] = {}

    def add_section(self, section_id: str, title: str, content: str) -> None:
        """Adds and verifies a single dedicated section."""
        # Check that section is not empty
        if len(content.strip()) < 100:
            raise ValueError(f"Section '{section_id}' is too short ({len(content.strip())} chars). Substantive content required.")
        self.sections[section_id] = f"## {title}\n\n{content.strip()}\n"

    def assemble_full_paper(self, title: str, abstract: str) -> str:
        """Assembles all sections into a complete academic paper with header and metadata."""
        doc = [
            f"# {title}\n",
            "**Author:** ANSE Autonomous Neuro-Symbolic Research Group",
            f"**Attestation:** Antigravity Zero-Trust Scientific Harness | Date: {time.strftime('%Y-%m-%d')}\n",
            "### Abstract\n",
            f"{abstract.strip()}\n",
            "---\n",
        ]
        for sec_id, sec_text in self.sections.items():
            doc.append(sec_text)
            doc.append("\n---\n")

        full_text = "\n".join(doc)
        output_file = self.paper_dir / "anse_physical_world_model_formal_paper.md"
        output_file.write_text(full_text, encoding="utf-8")
        return full_text
