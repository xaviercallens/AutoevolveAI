import json
import pytest
from pathlib import Path
from anse.autoresearch.ar_record import ARRecord
from anse.autoresearch.ratchet import compute_fitness, BenchmarkResult, RatchetGate, RatchetVerdict
from anse.autoresearch.mcts import MCTSNode, MCTSTree, deep_think

def test_mcts_node_ucb1():
    parent = MCTSNode("parent", "prompt", 0, None, [], 0.5, 1.0, 10, None, False, False)
    child1 = MCTSNode("child1", "prompt", 1, parent, [], 0.8, 1.0, 2, None, False, False)
    child2 = MCTSNode("child2", "prompt", 1, parent, [], 0.8, 1.0, 0, None, False, False)
    
    ucb1 = child1.ucb1_laya()
    assert ucb1 > 0.8
    assert child2.ucb1_laya() == float('inf')

def test_mcts_tree_select_best():
    tree = MCTSTree("test")
    tree.root.visits = 10
    c1 = MCTSNode("c1", "test", 1, tree.root, [], 0.2, 1.0, 5, None, False, False)
    c2 = MCTSNode("c2", "test", 1, tree.root, [], 0.9, 1.0, 5, None, False, False)
    tree.root.children.extend([c1, c2])
    tree.nodes.extend([c1, c2])
    
    best = tree.select()
    assert best == c2

class MockPolicy:
    def generate(self, prompt, k=3):
        return [f"def solution_{i}(): return 42" for i in range(k)]

class MockValue:
    def evaluate(self, thoughts):
        return [0.8]*len(thoughts), [0.9]*len(thoughts)

class MockSandbox:
    def run(self, state):
        return True

def test_deep_think_mock():
    policy = MockPolicy()
    value = MockValue()
    sandbox = MockSandbox()
    
    answer, tree, telemetry = deep_think("prompt", policy, value, sandbox, max_depth=1, k=3, timeout_s=5.0)
    assert answer is not None
    assert telemetry["nodes_explored"] == 3
    assert telemetry["sandbox_errors"] == 0

def test_ratchet_gate_accepts():
    gate = RatchetGate(Path("/tmp"))
    base = BenchmarkResult(0.5, 10.0, 100.0)
    arh5 = BenchmarkResult(0.8, 10.0, 100.0)
    verdict = gate.evaluate(base, arh5)
    assert verdict.status == "ACCEPTED"
    assert verdict.delta_fitness > 0

def test_ratchet_gate_rejects():
    gate = RatchetGate(Path("/tmp"))
    base = BenchmarkResult(0.5, 10.0, 100.0)
    arh5 = BenchmarkResult(0.3, 10.0, 100.0)
    verdict = gate.evaluate(base, arh5)
    assert verdict.status == "REJECTED"
    assert verdict.delta_fitness < 0

def test_ar_record_sha256():
    r = ARRecord(
        id="AR-H5", title="test", hypothesis="h", status="PENDING",
        fitness_baseline=0.0, fitness_arh5=0.0, delta_fitness=0.0,
        commit_hash=None, timestamp_start="now", timestamp_end=None,
        benchmark="crux", n_problems=1, n_pass_baseline=0, n_pass_arh5=0,
        vram_peak_gb_baseline=0.0, vram_peak_gb_arh5=0.0,
        tts_s_baseline=0.0, tts_s_arh5=0.0, notes=[], sha256=""
    )
    h1 = r.compute_sha256()
    h2 = r.compute_sha256()
    assert h1 == h2
