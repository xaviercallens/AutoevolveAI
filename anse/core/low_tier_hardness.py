import ast
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class HardnessMetrics:
    pass_at_1: float = 0.0
    false_convergence: float = 0.0
    rescue_efficiency: float = 0.0
    energy_monotonicity: float = 0.0

class ComponentRegistry:
    """D8: Autopoietic Prompt Strategy Registry."""
    def __init__(self):
        self._strategies: Dict[str, Dict[str, Any]] = {}
        self._active_version: Dict[str, str] = {}

    def register_strategy(self, component_name: str, version: str, prompt_template: str):
        if component_name not in self._strategies:
            self._strategies[component_name] = {}
        self._strategies[component_name][version] = prompt_template
        # Auto-activate if first
        if component_name not in self._active_version:
            self._active_version[component_name] = version

    def get_active_strategy(self, component_name: str) -> str:
        version = self._active_version.get(component_name)
        if not version:
            raise ValueError(f"No active strategy for {component_name}")
        return self._strategies[component_name][version]

    def rollback(self, component_name: str, version: str):
        if version in self._strategies.get(component_name, {}):
            self._active_version[component_name] = version
        else:
            raise ValueError("Version not found.")

class LowTierHardnessPolicy:
    """Phase 4: Low-Tier Model Hardness implementation for sub-3B models."""
    
    def __init__(self, dpo_export_path: str = "results/dpo_preference_pairs.jsonl"):
        self.dpo_export_path = Path(dpo_export_path)
        self.dpo_export_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry = ComponentRegistry()

    def apply_d1_prompt_budget(self, stderr: str, max_length: int = 200) -> str:
        """D1: Compresses failing code & stderr to <200 chars to avoid attention dilution."""
        if not stderr:
            return ""
        if len(stderr) <= max_length:
            return stderr
        
        # Keep the most critical parts: the beginning (error type) and the very end (traceback root)
        half = (max_length - 5) // 2
        return stderr[:half] + " ... " + stderr[-half:]

    def apply_d2_capacity_gating(self, model_size_params: int) -> bool:
        """D2: Disables repetitive retry branches on sub-3B models."""
        return model_size_params > 3_000_000_000

    def apply_d3_energy_monotonic_abort(self, e1: float, e2: float) -> bool:
        """D3: Aborts retry branches immediately if E1 > 60 or E2 > E1 (diverging energy)."""
        if e1 > 60.0:
            return True
        if e2 > e1:
            return True
        return False

    def apply_d4_skeleton_lessons(self, source_code: str) -> str:
        """D4: Extracts AST function signatures and docstrings, omitting full code."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return "SyntaxError: Could not parse code for skeleton extraction."
        
        skeleton = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                prefix = "def" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class"
                signature = f"{prefix} {node.name}(...):"
                skeleton.append(signature)
                docstring = ast.get_docstring(node)
                if docstring:
                    skeleton.append(f'    """{docstring.split(chr(10))[0]}..."""')
                else:
                    skeleton.append("    pass")
        
        return "\n".join(skeleton)

    def apply_d5_triage(self, energy: float) -> str:
        """D5: Categorizes tasks into trivial, fixable, and hard based on physical energy."""
        if energy <= 1.0:
            return "trivial"
        elif energy <= 10.0:
            return "fixable"
        else:
            return "hard"

    def apply_d6_live_dpo_export(self, prompt: str, chosen: str, rejected: str, e_chosen: float, e_rejected: float):
        """D6: Automatically exports pairwise preference data when dE >= 10."""
        if (e_rejected - e_chosen) >= 10.0:
            pair = {
                "prompt": prompt,
                "chosen": chosen,
                "rejected": rejected,
                "energy_chosen": e_chosen,
                "energy_rejected": e_rejected,
                "delta_e": e_rejected - e_chosen
            }
            with open(self.dpo_export_path, "a") as f:
                f.write(json.dumps(pair) + "\n")
            logger.info(f"DPO pair exported. Delta E: {pair['delta_e']}")
            return True
        return False

    def evaluate_d7_gates(self, metrics: HardnessMetrics) -> bool:
        """D7: Low-tier pass@1 >= 0.30, false convergence < 0.50, rescue efficiency >= 0.10, energy monotonicity >= 0.30."""
        g1 = metrics.pass_at_1 >= 0.30
        g2 = metrics.false_convergence < 0.50
        g3 = metrics.rescue_efficiency >= 0.10
        g4 = metrics.energy_monotonicity >= 0.30
        return all([g1, g2, g3, g4])

