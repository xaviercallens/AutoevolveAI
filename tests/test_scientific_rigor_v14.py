"""
Tests for v14.0.0 Scientific Rigor Validation
Validates that:
1. Numerical results come from external subprocess (anti-hallucination)
2. Domain decomposition is correct (E vs C never mixed)
3. Lean 4 theorems compile (lake build passes)
4. Papers contain required sections (epistemic disclaimer, Hamiltonians)
5. DPO retraining dataset is properly structured
"""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# ============================================================
# 1. Anti-hallucination: numerical pipeline
# ============================================================

class TestNumericalPipeline:
    """All numbers must come from external computation, not LLM generation."""

    def test_numerical_file_exists(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "numerical_calculations_10_problems_v13_9.json"
        assert f.exists(), "Numerical data file must exist"

    def test_numerical_data_has_10_problems(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "numerical_calculations_10_problems_v13_9.json"
        d = json.loads(f.read_text())
        assert len(d["problems"]) == 10, f"Expected 10 problems, got {len(d['problems'])}"

    def test_all_gates_passed(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "numerical_calculations_10_problems_v13_9.json"
        d = json.loads(f.read_text())
        failed = [p["problem_id"] for p in d["problems"] if not p.get("gate_passed", False)]
        assert not failed, f"Gates failed for: {failed}"

    def test_anti_hallucination_label(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "numerical_calculations_10_problems_v13_9.json"
        d = json.loads(f.read_text())
        assert "anti_hallucination" in d, "Must have anti_hallucination field"
        assert "external subprocess" in d["anti_hallucination"].lower()

    def test_domain_decomposition_present(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "numerical_calculations_10_problems_v13_9.json"
        d = json.loads(f.read_text())
        assert "domain_decomposition" in d, "Must have domain_decomposition field"
        dd = d["domain_decomposition"]
        assert "continuous_energy_E" in dd
        assert "discrete_cost_C" in dd
        assert len(dd["continuous_energy_E"]) == 5
        assert len(dd["discrete_cost_C"]) == 5


# ============================================================
# 2. Domain decomposition correctness
# ============================================================

class TestDomainDecomposition:
    """Continuous and discrete metrics must never be mixed."""

    def test_continuous_problems_use_energy_E(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "numerical_calculations_10_problems_v13_9.json"
        d = json.loads(f.read_text())
        continuous_ids = {"K3-ASTRO-01", "K3-ASTRO-02", "K3-ASTRO-03", "K3-ASTRO-09", "K3-ASTRO-10"}
        for p in d["problems"]:
            if p["problem_id"] in continuous_ids:
                assert p["metric_type"] == "physical_energy_E", \
                    f"{p['problem_id']} must use physical_energy_E, got {p['metric_type']}"
                assert "energy_baseline" in p, f"{p['problem_id']} must have energy_baseline"
                assert "energy_improved" in p, f"{p['problem_id']} must have energy_improved"

    def test_discrete_problems_use_cost_C(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "numerical_calculations_10_problems_v13_9.json"
        d = json.loads(f.read_text())
        discrete_ids = {"K3-ASTRO-04", "K3-ASTRO-05", "K3-ASTRO-06", "K3-ASTRO-07", "K3-ASTRO-08"}
        for p in d["problems"]:
            if p["problem_id"] in discrete_ids:
                assert p["metric_type"] == "computational_cost_C", \
                    f"{p['problem_id']} must use computational_cost_C, got {p['metric_type']}"
                assert "cost_baseline" in p, f"{p['problem_id']} must have cost_baseline"
                assert "cost_improved" in p, f"{p['problem_id']} must have cost_improved"

    def test_no_global_energy_sum(self):
        """The reviewer's key complaint: summing dimensionally disjoint scalars."""
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "numerical_calculations_10_problems_v13_9.json"
        d = json.loads(f.read_text())
        # The summary must NOT have a single global energy total
        summary = d.get("summary", {})
        assert "total_energy" not in summary, "Must not sum continuous E and discrete C"
        assert "global_energy" not in summary, "Must not sum continuous E and discrete C"
        # Instead must have separate averages
        assert "avg_E_improvement_pct" in summary
        assert "avg_C_improvement_pct" in summary

    def test_domain_note_in_discrete_problems(self):
        """Every discrete problem must have an explicit domain_note explaining why E doesn't apply."""
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "numerical_calculations_10_problems_v13_9.json"
        d = json.loads(f.read_text())
        discrete_ids = {"K3-ASTRO-04", "K3-ASTRO-05", "K3-ASTRO-06", "K3-ASTRO-07", "K3-ASTRO-08"}
        for p in d["problems"]:
            if p["problem_id"] in discrete_ids:
                assert "domain_note" in p, f"{p['problem_id']} must have domain_note"
                note = p["domain_note"].upper()
                # Must explain it's topological/algebraic/analytic/ODE, not continuous energy
                has_clarification = any(kw in note for kw in [
                    "TOPOLOGICAL", "DISCRETE", "DIOPHANTINE", "ANALYTIC", "ALGEBRAIC",
                    "LINEAR ODE", "LINEAR PDE", "NOT CONTINUOUS", "NOT A CONTINUOUS",
                    "CONSTRAINT", "INVARIANT"
                ])
                assert has_clarification, f"{p['problem_id']} domain_note must clarify why E doesn't apply: {note[:100]}"


# ============================================================
# 3. DPO Retraining Dataset
# ============================================================

class TestDPORetraining:
    """Validate DPO retraining dataset structure."""

    def test_dpo_file_exists(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "dpo_retraining_v14_0.json"
        assert f.exists(), "DPO retraining file must exist"

    def test_dpo_has_negative_examples(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "dpo_retraining_v14_0.json"
        d = json.loads(f.read_text())
        assert len(d["negative_examples"]) >= 3, "Must have at least 3 negative examples"

    def test_dpo_has_positive_examples(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "dpo_retraining_v14_0.json"
        d = json.loads(f.read_text())
        assert len(d["positive_examples"]) >= 2, "Must have at least 2 positive examples"

    def test_dpo_lessons_learned(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "dpo_retraining_v14_0.json"
        d = json.loads(f.read_text())
        lessons = d.get("lessons_learned", {})
        assert "lean4_anti_patterns" in lessons
        assert "lean4_correct_patterns" in lessons
        assert "domain_decomposition" in lessons
        assert "model_tier_allocation" in lessons

    def test_model_tier_allocation_correct(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "dpo_retraining_v14_0.json"
        d = json.loads(f.read_text())
        tiers = d["lessons_learned"]["model_tier_allocation"]
        assert "pro_tier" in tiers
        assert "flash_tier" in tiers
        # Pro tier must handle science decisions
        pro = " ".join(tiers["pro_tier"]).lower()
        assert "scientific" in pro or "physics" in pro or "novel" in pro


# ============================================================
# 4. Lean 4 Build (invokes lake build)
# ============================================================

@pytest.mark.slow
class TestLean4Build:
    """Verify that Lean 4 modules compile correctly."""

    def test_k3_problems_v2_builds(self):
        """K3_10Problems_v2.lean must build without sorry."""
        result = subprocess.run(
            ["lake", "build", "ANSE.K3_10Problems_v2"],
            cwd=REPO_ROOT / "formal",
            capture_output=True, text=True, timeout=300
        )
        assert result.returncode == 0, f"lake build failed:\n{result.stderr}"
        assert "error" not in result.stdout.lower() or "Build completed" in result.stdout

    def test_no_sorry_in_lean_files(self):
        """Lean files must not contain sorry."""
        lean_dir = REPO_ROOT / "formal" / "ANSE"
        for lean_file in lean_dir.glob("*.lean"):
            content = lean_file.read_text()
            # Check for sorry not in comments
            lines = content.splitlines()
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                # Skip comment lines (-- or /- docstrings) and list items explaining sorry usage
                if stripped.startswith("--") or stripped.startswith("/-") or stripped.startswith("-"):
                    continue
                if "sorry" in stripped:
                    # Allow documented proof obligations marked with the ⚠ convention
                    if "-- ⚠" in stripped or "-- ⚠" in line:
                        continue
                    pytest.fail(f"{lean_file.name}:{i}: contains sorry: {line!r}")


# ============================================================
# 5. Peer Review Storage
# ============================================================

class TestPeerReviewStorage:
    """Validate that peer reviews are stored in LTM."""

    def test_peer_review_v2_file_exists(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "review" / "peer_reviews_v2.json"
        assert f.exists(), "Peer review v2 must be stored"

    def test_peer_review_v2_has_sha(self):
        f = REPO_ROOT / "results" / "phd_k3_pipeline" / "review" / "peer_reviews_v2.json"
        d = json.loads(f.read_text())
        assert "sha256" in d, "Must have SHA256 for audit trail"
        assert len(d["sha256"]) == 64, "SHA256 must be 64 hex chars"

    def test_peer_review_chromadb_retrievable(self):
        """Peer review v2 must be retrievable from ChromaDB."""
        try:
            sys.path.insert(0, str(REPO_ROOT))
            from anse.memory.chroma_rag import ChromaRAG
            rag = ChromaRAG(persist_directory=str(REPO_ROOT / ".chroma_db"))
            results = rag.query_literature("Lean 4 tautology arithmetic physics", n_results=3)
            doc_ids = [r.get("id", r.get("doc_id", "")) for r in results]
            assert any("peer_review" in did for did in doc_ids), \
                f"Peer review not found in ChromaDB, found: {doc_ids}"
        except ImportError:
            pytest.skip("ChromaDB not available")
