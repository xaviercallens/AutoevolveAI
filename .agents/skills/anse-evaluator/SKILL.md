---
name: anse-evaluator
description: >-
  Evaluate candidate algorithms, PyTorch neural architectures, or self-refactored code
  in the deterministic sandbox against physical energy metrics (latency, RAM, tensor dimensions,
  parameter count, and loss). Use this skill when benchmarking, measuring speedups, or evaluating
  System 2 reasoning feedback.
---

# ANSE Evaluator Skill

This skill guides the agent in benchmarking and evaluating code candidates using the ANSE deterministic sandbox and physical energy scoring engine.

## 1. Quick Verification Commands

Run algorithmic performance benchmarks:
```bash
uv run pytest tests/performance/test_algorithmic_benchmark.py -v
```

Run automata physics and complexity explorer benchmarks:
```bash
uv run pytest tests/performance/test_automata_and_complexity.py -v
```

Run Micro-ML architecture evaluations:
```bash
uv run pytest tests/phase2/test_ml_sandbox.py tests/phase2/test_ml_evaluator.py -v
```

## 2. Programmatic Sandbox Usage

To execute arbitrary candidate code inside the sandbox in Python:

```python
from anse.symbolic.sandbox import SandboxExecutor
from anse.symbolic.performance_evaluator import PerformanceEnergyEvaluator

sandbox = SandboxExecutor()
evaluator = PerformanceEnergyEvaluator()

# Execute code candidate
res = sandbox.execute(code_str)

# Calculate physical energy
energy_res = evaluator.evaluate(res)
print(f"Energy: {energy_res.score:.2f}, Valid: {energy_res.is_valid}")
if not energy_res.is_valid:
    print(f"Pain Signal: {energy_res.pain_signal}")
```

## 3. Interpreting Energy Signals

- **$E \ge 10^6$ (Maximum Pain):** The code crashed, raised a SyntaxError, timed out, or failed an assertion. Check `energy_res.pain_signal` for the traceback and reason.
- **$E \ge 1000$ (Micro-ML Mismatch):** PyTorch tensor shape mismatch or memory dimension error. Traces linear and conv dimensions.
- **$E = \text{Params} - 50,000$ (Parameter Exceedance):** Network has too many weights to meet the VRAM budget. Suggests narrower hidden dimensions, depth, or LayerNorm/GELU.
- **$E = \text{Duration (ms)} + \text{Peak RAM (MB)}$:** Valid physical execution. Lower is strictly superior.
