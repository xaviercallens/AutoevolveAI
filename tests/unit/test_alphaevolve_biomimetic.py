"""
Unit tests for the AlphaEvolve + Genetic Algorithm + Biomimetic Evolution Engine
(`anse/autopoiesis/alphaevolve_biomimetic.py`).
"""

from __future__ import annotations

import random

from anse.autopoiesis.alphaevolve_biomimetic import (
    MAX_APOPTOSIS_ENERGY,
    AlphaEvolveBiomimeticEngine,
    ArtificialImmuneSystem,
    ASTGeneticOperators,
    DiploidGenome,
    EpigeneticChromatinState,
)


def test_epigenetic_chromatin_methylation_and_acetylation() -> None:
    epi = EpigeneticChromatinState()
    epi.update_from_evaluation(["fast_kernel", "helper_fn"], total_energy=10.0, methylation_threshold=25.0)
    assert "fast_kernel" in epi.methylated_loci
    assert "fast_kernel" not in epi.acetylated_loci

    # High-energy update shifts locus to acetylated (euchromatic / open for mutation)
    epi.update_from_evaluation(["slow_bottleneck"], total_energy=120.0, methylation_threshold=25.0)
    assert "slow_bottleneck" in epi.acetylated_loci
    assert "slow_bottleneck" not in epi.methylated_loci


def test_ais_negative_selection_and_somatic_hypermutation() -> None:
    ais = ArtificialImmuneSystem()

    malicious_code = """
import subprocess

def bad_kernel(x: float) -> float:
    subprocess.run("echo hack", shell=True)
    return x
"""
    ok, reason, token = ais.negative_selection_screen(malicious_code)
    assert ok is False
    assert "AIS Apoptosis" in reason
    assert token == ""

    # Second encounter with same hash is immediately blocked by antigen memory
    ok2, reason2, _ = ais.negative_selection_screen(malicious_code)
    assert ok2 is False
    assert "lethal antigen hash" in reason2

    # Somatic hypermutation rate is lower for low-energy (high-affinity) clones
    rate_elite = ais.somatic_hypermutation_rate(energy=5.0, reference_energy=50.0)
    rate_poor = ais.somatic_hypermutation_rate(energy=200.0, reference_energy=50.0)
    assert rate_elite < rate_poor


def test_homologous_ast_crossover_and_alphaevolve_diff_patch() -> None:
    code_a = """
def conserved_integrator(x: float) -> float:
    return x * 0.5

def bottleneck_step(x: float) -> float:
    total = 0.0
    for i in range(10):
        total += x * 0.1
    return total
"""
    code_b = """
def conserved_integrator(x: float) -> float:
    return x * 999.0

def bottleneck_step(x: float) -> float:
    return x * 1.0

def fast_auxiliary(y: float) -> float:
    return y * 2.0
"""
    parent_a = DiploidGenome(genome_id="pa", dominant_code=code_a, total_energy=15.0)
    parent_a.epigenetics.methylated_loci.add("conserved_integrator")
    parent_a.epigenetics.acetylated_loci.add("bottleneck_step")

    parent_b = DiploidGenome(genome_id="pb", dominant_code=code_b, total_energy=12.0)
    parent_b.epigenetics.methylated_loci.add("bottleneck_step")

    child_dom, child_rec = ASTGeneticOperators.homologous_crossover(
        parent_a, parent_b, rng=random.Random(7)
    )
    # Methylated `conserved_integrator` in A is preserved (`x * 0.5`),
    # methylated `bottleneck_step` in B replaces A's acetylated version (`return x * 1.0`),
    # and `fast_auxiliary` helper from B is spliced in.
    assert "x * 0.5" in child_dom
    assert "return x * 1.0" in child_dom
    assert "def fast_auxiliary" in child_dom
    assert child_rec == code_b

    diff_patch = """<<<<<<< SEARCH
def bottleneck_step(x: float) -> float:
    return x * 1.0
=======
def bottleneck_step(x: float) -> float:
    return x * 1.0000001
>>>>>>> REPLACE"""
    patched = ASTGeneticOperators.apply_alphaevolve_diff(child_dom, diff_patch)
    assert "1.0000001" in patched


def test_map_elites_island_and_full_alphaevolve_biomimetic_loop() -> None:
    baseline_code = """
def compute_potential(n: int) -> float:
    acc = 0.0
    for i in range(n):
        if i % 2 == 0:
            acc += float(i) * 0.5
        else:
            acc += float(i) * 0.5
    return acc
"""
    optimized_diff = """<<<<<<< SEARCH
    acc = 0.0
    for i in range(n):
        if i % 2 == 0:
            acc += float(i) * 0.5
        else:
            acc += float(i) * 0.5
    return acc
=======
    return 0.25 * float(n) * float(n - 1)
>>>>>>> REPLACE"""

    def mock_physics_evaluator(code: str) -> dict[str, float]:
        if "0.25 * float(n) * float(n - 1)" in code:
            return {
                "physical_energy": 4.2,
                "latency_ms": 0.4,
                "memory_mb": 1.2,
                "invariant_error": 1e-12,
            }
        return {
            "physical_energy": 48.0,
            "latency_ms": 12.5,
            "memory_mb": 6.5,
            "invariant_error": 1e-9,
        }

    engine = AlphaEvolveBiomimeticEngine(
        evaluator_fn=mock_physics_evaluator,
        num_islands=3,
        migration_interval=2,
        seed=42,
    )

    result = engine.run_evolution_with_hardened_gate(
        initial_codes=[baseline_code],
        generations=5,
        candidate_proposals=[optimized_diff],
    )

    assert result["promoted"] is True
    assert result["champion_energy"] < result["baseline_energy"]
    assert result["delta_energy"] < -40.0
    assert result["archive_total_elites"] >= 3
    assert result["champion"]["attestation_token"] != ""


def test_recessive_allele_rescues_corrupted_dominant_mutation() -> None:
    valid_backup = """
def kernel(x: float) -> float:
    return x * 2.0
"""
    corrupted_dominant = """
import os

def kernel(x: float) -> float:
    os.system("echo bad")
    return x * 2.0
"""
    engine = AlphaEvolveBiomimeticEngine(
        evaluator_fn=lambda code: {
            "physical_energy": 8.0,
            "latency_ms": 1.0,
            "memory_mb": 1.0,
            "invariant_error": 0.0,
        }
    )
    genome = DiploidGenome(
        genome_id="dip_rescue",
        dominant_code=corrupted_dominant,
        recessive_code=valid_backup,
    )
    evaluated = engine.evaluate_genome(genome)
    assert evaluated.total_energy < MAX_APOPTOSIS_ENERGY
    assert "recessive_rescue" in evaluated.mutation_operator
    assert "os.system" not in evaluated.dominant_code
    assert evaluated.attestation_token != ""


def test_structural_gp_operators_memoization_strength_reduction_and_comprehension() -> None:
    rec_code = """
def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
"""
    memo_code, applied_memo = ASTGeneticOperators.apply_memoization_mutation(rec_code)
    assert applied_memo is True
    assert "lru_cache" in memo_code

    # Verify autonomous GP evolution of recursive fib without any external diff proposal
    def eval_fib(code: str) -> dict[str, float]:
        if "lru_cache" in code:
            return {"physical_energy": 1.5, "latency_ms": 0.1, "memory_mb": 1.0, "invariant_error": 0.0}
        return {"physical_energy": 250.0, "latency_ms": 25.0, "memory_mb": 1.0, "invariant_error": 0.0}

    engine = AlphaEvolveBiomimeticEngine(evaluator_fn=eval_fib, num_islands=2, seed=7)
    res = engine.run_evolution_with_hardened_gate(initial_codes=[rec_code], generations=4)
    assert res["promoted"] is True
    assert "lru_cache" in res["champion"]["dominant_code"]

    pow_code = """
def poly(x: float) -> float:
    return x ** 2 + x ** 3
"""
    sr_code, applied_sr = ASTGeneticOperators.apply_strength_reduction_mutation(pow_code)
    assert applied_sr is True
    assert "**" not in sr_code
    assert "x * x" in sr_code

    loop_code = """
def filter_double(items: list[int]) -> list[int]:
    acc = []
    for x in items:
        if x > 0:
            acc.append(x * 2)
    return acc
"""
    comp_code, applied_comp = ASTGeneticOperators.apply_loop_comprehension_mutation(loop_code)
    assert applied_comp is True
    assert "[x * 2 for x in items if x > 0]" in comp_code


def test_nsga2_pareto_fronts_and_lexicase_selection() -> None:
    from anse.autopoiesis.alphaevolve_biomimetic import MAPElitesIsland, compute_pareto_fronts

    g_fast = DiploidGenome(
        genome_id="g_fast",
        dominant_code="def f(x): return x + 1",
        total_energy=10.0,
        latency_ms=1.0,
        memory_mb=8.0,
        metabolic_energy=1.0,
        invariant_error=0.0,
        behavioral_descriptor=(0, 2),
    )
    g_lean = DiploidGenome(
        genome_id="g_lean",
        dominant_code="def f(x): return x + 1",
        total_energy=12.0,
        latency_ms=3.0,
        memory_mb=1.0,
        metabolic_energy=0.5,
        invariant_error=0.0,
        behavioral_descriptor=(0, 0),
    )
    g_dominated = DiploidGenome(
        genome_id="g_dom",
        dominant_code="def f(x): return x + 1",
        total_energy=30.0,
        latency_ms=10.0,
        memory_mb=12.0,
        metabolic_energy=5.0,
        invariant_error=1e-3,
        behavioral_descriptor=(2, 3),
    )

    fronts = compute_pareto_fronts([g_fast, g_lean, g_dominated])
    assert len(fronts) == 2
    front0_ids = {g.genome_id for g in fronts[0]}
    assert front0_ids == {"g_fast", "g_lean"}
    assert g_dominated.pareto_rank == 1

    isl = MAPElitesIsland(island_id=0)
    isl.insert(g_fast)
    isl.insert(g_lean)
    isl.insert(g_dominated)
    rng = random.Random(123)
    selected = isl.select_parent_lexicase(rng)
    assert selected is not None
    assert selected.genome_id in {"g_fast", "g_lean", "g_dom"}


def test_strong_ai_coding_hardness_rules_and_generate_and_evolve(tmp_path) -> None:
    from anse.core.self_healing import generate_and_evolve_hardened
    from antigravity_harness.core.argos_hardener import ArgosCyberDefenseAuditor

    auditor = ArgosCyberDefenseAuditor()

    # ARGOS-HARD-007: Silent exception swallowing
    ok_007, v_007 = auditor.audit_code(
        "def f(x):\n    try:\n        return 1 / x\n    except Exception:\n        pass\n"
    )
    assert ok_007 is False
    assert any(v.rule_id == "ARGOS-HARD-007" for v in v_007)

    # ARGOS-HARD-008: Input-ignoring specification gaming
    ok_008, v_008 = auditor.audit_code(
        "def solve_pde(u0, dt, steps):\n    return [1.0, 2.0, 3.0]\n"
    )
    assert ok_008 is False
    assert any(v.rule_id == "ARGOS-HARD-008" for v in v_008)

    # ARGOS-HARD-009: Timer / sandbox monkey-patching
    ok_009, v_009 = auditor.audit_code(
        "import time\ntime.perf_counter = lambda: 0.0\n"
    )
    assert ok_009 is False
    assert any(v.rule_id == "ARGOS-HARD-009" for v in v_009)

    # ARGOS-HARD-010: Dynamic __import__ sandbox escape
    ok_010, v_010 = auditor.audit_code(
        "def esc(x):\n    m = __import__('os')\n    return x\n"
    )
    assert ok_010 is False
    assert any(v.rule_id == "ARGOS-HARD-010" for v in v_010)

    # End-to-end generate_and_evolve_hardened with a mock Gemini 4 Argon client
    class _MockOutput:
        def __init__(self, t: str, text: str = "", sig: str = "") -> None:
            self.type = t
            self.text = text
            self.summary = text
            self.signature = sig

    class _MockInteractionResp:
        id = "inter_hard_01"
        outputs = [
            _MockOutput("thought", "Derive recursive recurrence for Lucas numbers", "sig_argos_99"),
            _MockOutput(
                "text",
                "```python\ndef lucas(n: int) -> int:\n    if n == 0:\n        return 2\n    if n == 1:\n        return 1\n    return lucas(n - 1) + lucas(n - 2)\n```",
            ),
        ]

    class _MockInteractions:
        def create(self, **kwargs):
            return _MockInteractionResp()

    class _MockClient:
        interactions = _MockInteractions()

    target_file = tmp_path / "evolved_lucas.py"
    summary = generate_and_evolve_hardened(
        prompt="Implement lucas(n: int) -> int.",
        target_file=str(target_file),
        evaluator_fn=lambda code: (
            {"physical_energy": 1.2, "latency_ms": 0.05, "memory_mb": 1.0, "invariant_error": 0.0}
            if "lru_cache" in code
            else {"physical_energy": 95.0, "latency_ms": 9.5, "memory_mb": 1.0, "invariant_error": 0.0}
        ),
        generations=4,
        num_islands=2,
        client=_MockClient(),
        seed=11,
    )
    assert summary["promoted"] is True
    assert summary["hardening_passed"] is True
    assert "lru_cache" in summary["final_code"]
    assert summary["attestation_token"] != ""

