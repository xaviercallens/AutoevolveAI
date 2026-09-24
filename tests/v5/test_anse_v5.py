"""
tests/v5/test_anse_v5.py - Verification & Validation Suite for ANSE Phase V5.

Validates:
  1. Laya System 1 Non-Autoregressive Decision Engine running on local CPU.
  2. Rosetta Stone Triplet Cross-Domain Verification (Lean 4 + Python + Rust).
  3. GRPO Test-Time Compute Group Exploration and Relative Advantage Normalization.
  4. Autonomous Scientific Curriculum Generation and E2E Science Pipeline.
"""

from __future__ import annotations

import pytest
from anse.v5 import (
    ANSEEngineV5,
    AutonomousCurriculumEngine,
    GRPOExplorer,
    LayaSystemOneDecisionEngine,
    RosettaStoneEngine,
    RosettaTriplet,
)


class TestLayaSystemOne:

    @pytest.fixture(scope="class")
    def laya_engine(self) -> LayaSystemOneDecisionEngine:
        return LayaSystemOneDecisionEngine(device="cpu")

    def test_laya_model_loaded_on_cpu(self, laya_engine: LayaSystemOneDecisionEngine):
        assert laya_engine.device == "cpu"
        assert laya_engine.is_loaded is True

    def test_laya_triage_choice(self, laya_engine: LayaSystemOneDecisionEngine):
        res = laya_engine.triage_hypothesis(
            "Theorem: Given a closed differential 2-form omega on a symplectic manifold M, d(omega) = 0.",
            choices=["sound", "unsound", "needs_proof"],
        )
        assert res["decision_type"] == "choice"
        assert res["choice"] in ["sound", "unsound", "needs_proof"]
        assert "probabilities" in res
        assert res["latency_ms"] > 0
        assert res["device"] == "cpu"

    def test_laya_score_ordered_scale(self, laya_engine: LayaSystemOneDecisionEngine):
        res = laya_engine.score_hypothesis(
            "Vectorized SIMD cache-blocked stencil evaluation achieving zero memory allocation."
        )
        assert res["decision_type"] == "score"
        assert isinstance(res["score"], float)
        assert "legend" in res

    def test_laya_verify_truth_noul(self, laya_engine: LayaSystemOneDecisionEngine):
        res = laya_engine.verify_truth_noul(
            "Conservation of total momentum in closed Hamiltonian system.",
            "Energy is conserved within tolerance epsilon = 1e-4",
        )
        assert res["decision_type"] == "noul"
        assert 0.0 <= res["probability_true"] <= 1.0


class TestRosettaStone:

    @pytest.fixture
    def rosetta(self) -> RosettaStoneEngine:
        return RosettaStoneEngine()

    def test_rosetta_sound_triplet(self, rosetta: RosettaStoneEngine):
        curriculum = AutonomousCurriculumEngine()
        hypo = curriculum.get_hypothesis("kdv_soliton_momentum")
        assert hypo is not None
        res = rosetta.verify_triplet(hypo.triplet)

        assert res.triplet_aligned is True
        assert res.lean4_sound is True
        assert res.python_invariant_holds is True
        assert res.rust_speedup_achieved is True
        assert res.numerical_parity is True
        assert res.delta_energy < 0
        assert res.speedup > 1.0
        assert len(res.proof_token) == 32
        assert len(res.pipeline_stages) == 5

    def test_rosetta_rejects_lean4_sorry(self, rosetta: RosettaStoneEngine):
        triplet = RosettaTriplet(
            task_id="broken_lean",
            name="Broken Lean Proof",
            domain="Mathematics",
            lean4_code="theorem broken_proof (x : Nat) : x = x := by\n  sorry\n",
            python_code="result = 42\ninvariant_verified = True\noutput = result\n",
            rust_code="result = 42\noutput = result\n",
            invariant_target="Equality",
        )
        res = rosetta.verify_triplet(triplet)
        assert res.triplet_aligned is False
        assert res.lean4_sound is False
        assert res.proof_token == ""
        assert res.child_energy == 1_000_000.0

    def test_rosetta_rejects_python_stub(self, rosetta: RosettaStoneEngine):
        triplet = RosettaTriplet(
            task_id="broken_py",
            name="Broken Python Stub",
            domain="Physics",
            lean4_code="theorem sound_theorem : True := by trivial\n",
            python_code="def solve():\n    pass # TODO: implement\n",
            rust_code="result = 42\noutput = result\n",
            invariant_target="Conservation",
        )
        res = rosetta.verify_triplet(triplet)
        assert res.triplet_aligned is False
        assert res.python_invariant_holds is False
        assert res.proof_token == ""

    def test_rosetta_rejects_numerical_disparity(self, rosetta: RosettaStoneEngine):
        triplet = RosettaTriplet(
            task_id="disparity",
            name="Numerical Disparity",
            domain="Physics",
            lean4_code="theorem sound_theorem : True := by trivial\n",
            python_code="result = 100.0\ninvariant_verified = True\noutput = result\n",
            rust_code="result = 50.0\noutput = result\n",  # Mismatch!
            invariant_target="Numerical Parity",
            tolerance=1e-4,
        )
        res = rosetta.verify_triplet(triplet)
        assert res.triplet_aligned is False
        assert res.numerical_parity is False


class TestGRPOExplorer:

    def test_grpo_evaluation_and_advantage_normalization(self):
        grpo = GRPOExplorer(group_size=8)
        res = grpo.evaluate_group("Optimize Hamiltonian Symplectic Integrator")

        assert res.group_size == 8
        assert len(res.trajectories) == 8
        assert res.best_candidate_id in range(1, 9)
        assert res.best_reward > 0.0
        assert len(res.proof_token) == 32

        # Check that stubs were flagged and assigned penalty
        stub_trajectories = [t for t in res.trajectories if not t.is_clean]
        assert len(stub_trajectories) >= 1
        for st in stub_trajectories:
            assert st.reward == -1.0
            assert st.energy == 1_000_000.0
            assert "PRUNED" in st.status

        # Check advantages sum close to 0 (mean normalized)
        adv_sum = sum(t.advantage for t in res.trajectories)
        assert abs(adv_sum) < 0.5


class TestAutonomousCurriculumAndMasterEngine:

    def test_curriculum_catalog(self):
        engine = AutonomousCurriculumEngine()
        curricula = engine.list_curricula()
        assert len(curricula) >= 3
        ids = [c.hypothesis_id for c in curricula]
        assert "kdv_soliton_momentum" in ids
        assert "yang_mills_instanton" in ids
        assert "chern_number_quantum_hall" in ids

    def test_master_engine_v5_e2e_pipeline(self):
        v5 = ANSEEngineV5(device="cpu")
        res = v5.run_e2e_science_pipeline("kdv_soliton_momentum")

        assert res["status"] == "success"
        assert res["all_aligned"] is True
        assert len(res["proof_token"]) == 32
        assert res["rosetta_verification"]["triplet_aligned"] is True
        assert res["system_one_triage"]["decision_type"] == "choice"
        assert res["grpo_exploration"]["group_size"] == 8
