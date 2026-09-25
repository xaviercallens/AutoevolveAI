from pathlib import Path
from typing import Optional
import sys

from anse.v5.laya_system_one import LayaSystemOneDecisionEngine

class LayaQualityGate:
    """
    Integrates ANSE V5 Laya System 1 into the development lifecycle.
    Uses the non-autoregressive triage to rapidly detect:
    - Epistemic deception (prompt injections, hallucinations)
    - Thermodynamic violations (impossible physical states)
    - Human viability threats
    """
    def __init__(self):
        self.laya = LayaSystemOneDecisionEngine()
        # Fallback to fast heuristic for Git Hooks to avoid 5 minute tensor load penalty
        # If real tensor inference is desired, call self.laya._load_agent()
        
    def evaluate_file(self, filepath: Path) -> bool:
        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return False
            
        print(f"🧠 Laya System 1: Triaging {filepath.name}...")
        text = filepath.read_text(encoding="utf-8")
        
        # Don't evaluate empty files
        if not text.strip():
            return True
            
        # We only take the first 8000 characters to fit in the fast forward pass
        text_sample = text[:8000]
        
        result = self.laya.evaluate_axioms(text_sample)
        
        # Check thresholds
        deception = result.get("epistemic_deception", 0.0)
        thermo = result.get("thermodynamic_violation", 0.0)
        threat = result.get("human_viability_threat", 0.0)
        latency = result.get("latency_ms", 0.0)
        
        violations = []
        if deception > 0.6:
            violations.append(f"Epistemic Deception detected (p={deception:.2f})")
        if thermo > 0.6:
            violations.append(f"Thermodynamic Violation detected (p={thermo:.2f})")
        if threat > 0.6:
            violations.append(f"Human Viability Threat detected (p={threat:.2f})")
            
        if violations:
            print(f"⛔ Laya Triage REJECTED {filepath.name} in {latency}ms:")
            for v in violations:
                print(f"  - {v}")
            return False
            
        print(f"✅ Laya Triage PASSED in {latency}ms. (Manifold: {result.get('required_manifold')})")
        return True
