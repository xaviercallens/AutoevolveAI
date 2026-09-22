"""
Tests for the Zero-Hallucination Scientific Paper Harness:
- Verifies real reference retrieval from arXiv (never relying on LLM memory).
- Verifies anti-hallucination code execution for numeric values.
- Verifies section chunking and assembly.
"""

from __future__ import annotations

from pathlib import Path

from antigravity_harness.core.paper_harness import (
    AntiHallucinationNumericEngine,
    ReferenceFetcher,
    SectionPartitionOrchestrator,
)


def test_reference_fetcher_cached_or_live():
    fetcher = ReferenceFetcher(cache_dir=Path("papers/references"))
    refs = fetcher.fetch_papers("all:JEPA", max_results=2)
    assert len(refs) > 0
    for r in refs:
        assert r.arxiv_id
        assert r.title
        assert len(r.authors) > 0
        assert r.published_year >= 2000


def test_anti_hallucination_numeric_engine():
    engine = AntiHallucinationNumericEngine()
    code = """
import math
radius = 5.0
volume = (4.0 / 3.0) * math.pi * (radius ** 3)
"""
    val = engine.compute_and_record("sphere_volume", code, "volume")
    assert abs(val - 523.59877) < 1e-3

    paper_text = "The calculated sphere volume is 523.60 cubic units."
    valid, violations = engine.verify_paper_numerics(paper_text)
    assert valid is True
    assert len(violations) == 0


def test_section_partition_orchestrator(tmp_path: Path):
    orch = SectionPartitionOrchestrator(paper_dir=tmp_path)
    orch.add_section(
        "sec1",
        "Introduction",
        "This is an introductory section with substantive academic content describing the physical computational foundations of the system in detail.",
    )
    orch.add_section(
        "sec2",
        "Methods",
        "This is the methods section detailing the physical invariants, mathematical differential equations, and experimental setups thoroughly.",
    )
    doc = orch.assemble_full_paper("Title Test", "Abstract test text.")
    assert "Title Test" in doc
    assert "Introduction" in doc
    assert "Methods" in doc
    assert (tmp_path / "anse_physical_world_model_formal_paper.md").exists()
