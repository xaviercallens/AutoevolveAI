"""
Tests for ANSE vendor-integrated Dichotomy components:
- Aider-style Repo Map & Unified Diff
- Stanford DSPy Programmatic Pipeline & Metric
- SWE-agent AST Localized Navigator
- LangGraph Stateful Cyclical Execution Graph
"""

from pathlib import Path
import tempfile
import pytest

from anse.orchestration.ast_navigator import ASTLocalizedNavigator
from anse.orchestration.dspy_bridge import (
    DichotomyPipelineModule,
    physical_hardness_metric,
)
from anse.orchestration.repo_map import RepoMapGenerator, apply_unified_diff
from anse.orchestration.stateful_graph import StatefulDichotomyGraph


def test_aider_repo_map_generator():
    generator = RepoMapGenerator(max_map_tokens=400)
    repo_map = generator.generate_repo_map(query="Kerr Symplectic Integrator", max_tokens=400)

    assert "# COMPACT REPO MAP" in repo_map
    assert "anse/" in repo_map
    # Verify token footprint is strictly bounded
    estimated_tokens = len(repo_map) // 4
    assert estimated_tokens <= 400


def test_aider_apply_unified_diff():
    original = """def add(a, b):
    return a + b

def sub(a, b):
    return a - b
"""
    patch = """@@ -1,2 +1,2 @@
 def add(a, b):
-    return a + b
+    return (a + b) * 2
"""
    success, patched, msg = apply_unified_diff(original, patch)
    assert success
    assert "return (a + b) * 2" in patched
    assert "def sub(a, b):" in patched


def test_dspy_physical_hardness_metric():
    # Clean verified case with low energy
    high_reward = physical_hardness_metric({"passed": True, "energy_score": 1.5})
    assert high_reward > 0.8

    # Failed or stubbed case with E = 10^6
    zero_reward = physical_hardness_metric({"passed": False, "energy_score": 1e6})
    assert zero_reward == 0.0


def test_dspy_pipeline_forward_execution():
    pipeline = DichotomyPipelineModule()
    result = pipeline.forward(
        goal="Kerr Symplectic Integrator and Formal Banach Contraction",
        total_budget=8000,
        max_depth=1,
        leaf_code_generator=lambda leaf, rmap: "def compute(): return 100",
    )

    assert result["root_task_id"] == "root"
    assert result["total_leaves"] == 2
    assert result["leaves_verified"] == 2
    assert result["root_status"] == "VERIFIED"
    assert result["root_proof_token"] is not None
    assert len(result["execution_trace"]) == 2


def test_swe_agent_ast_localized_navigator():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_file = Path(tmpdir) / "sample_module.py"
        tmp_file.write_text(
            """import math

def calculate_metric(x, y):
    return x * y

def helper_func():
    return 10
""",
            encoding="utf-8",
        )

        nav = ASTLocalizedNavigator(root_dir=Path(tmpdir))
        window = nav.find_symbol(tmp_file, "calculate_metric")

        assert window is not None
        assert window.symbol_name == "calculate_metric"
        assert window.start_line == 3
        assert "return x * y" in window.source_snippet

        # Perform surgical in-place replacement
        replacement = """def calculate_metric(x, y):
    return math.sqrt(x**2 + y**2)"""

        success, msg = nav.replace_symbol(tmp_file, "calculate_metric", replacement)
        assert success
        updated = tmp_file.read_text(encoding="utf-8")
        assert "math.sqrt" in updated
        assert "def helper_func():" in updated  # Preserved surrounding code


def test_langgraph_stateful_cyclical_graph():
    graph = StatefulDichotomyGraph()
    state = graph.run(
        goal="Systolic Array STA and Real SCM_RIGHTS Hot-Swap",
        total_budget=8000,
        max_depth=1,
        leaf_sources={
            "root.L": "def run_l(): return 1",
            "root.R": "def run_r(): return 2",
        },
    )

    assert state.is_finished
    assert len(state.checkpoints) >= 4
    assert len(state.verified_proofs) == 3  # 2 leaves + 1 synthesized root
    assert "root" in state.verified_proofs
    assert len(state.step_history) >= 4
