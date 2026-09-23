from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
import json
import logging
from anse.core.api_extractor import APIExtractor

logger = logging.getLogger("DeepThinkRedTeam")

class VerificationState(TypedDict):
    math_problem: str
    lean_code: str
    python_metrics: dict
    thoughts: list[str]
    verdict: str

class DeepThinkAuditor:
    def __init__(self, extractor: APIExtractor | None = None):
        self.extractor = extractor or APIExtractor()
        
        workflow = StateGraph(VerificationState)
        workflow.add_node("epistemic_check", self.epistemic_thinker)
        workflow.add_node("physics_check", self.physics_sandbox_thinker)
        workflow.add_node("judge", self.final_judgment)

        workflow.set_entry_point("epistemic_check")
        workflow.add_edge("epistemic_check", "physics_check")
        workflow.add_edge("physics_check", "judge")
        workflow.add_edge("judge", END)

        self.app = workflow.compile()

    def epistemic_thinker(self, state: VerificationState):
        """Étape 1 : Le modèle réfléchit aux failles mathématiques (Junk values, Edge cases)."""
        prompt = f"""Analyse ce théorème Lean 4:
{state['lean_code']}
Cherche des "Junk Values" (ex: division par zéro silencieuse, Nat.card d'un infini).
L'agent a-t-il oublié le typeclass [Nonempty X] ou [Fact p.Prime] ?
Génère ta réflexion dans des balises <think>.
"""
        logger.info("Executing Epistemic Check...")
        try:
            response, _ = self.extractor.extract(
                prompt=prompt, 
                system_prompt="You are a Deep Think Epistemic Red Team auditor. Focus on formal Lean 4 loopholes.",
                temperature=0.2
            )
        except Exception:
            # Fallback simulation if LLM is not responding
            response = "<think>Checking bounds... Nat.card on infinite groups is 0.</think> Missing [Finite G] or fuzzing."
            
        thoughts = state.get("thoughts", [])
        return {"thoughts": thoughts + [response]}

    def physics_sandbox_thinker(self, state: VerificationState):
        """Étape 2 : Vérification des illusions numériques du CAS Python."""
        prompt = f"""Métriques:
{state['python_metrics']}
Le CAS Python a validé avec une erreur < 1e-14. Est-ce une tautologie discrète de la grille (ex: dérivées croisées) ?
L'énergie physique E est-elle réaliste ?
"""
        logger.info("Executing Physics Sandbox Check...")
        try:
            response, _ = self.extractor.extract(
                prompt=prompt, 
                system_prompt="You are a Computational Physics Red Team auditor. Focus on numerical illusions.",
                temperature=0.2
            )
        except Exception:
            response = "<think>Grid derivatives commute. We need polar singularity fuzzing.</think> Needs fuzzing."
            
        thoughts = state.get("thoughts", [])
        return {"thoughts": thoughts + [response]}

    def final_judgment(self, state: VerificationState):
        """Étape 3 : Synthèse et verdict implacable."""
        t1 = state['thoughts'][0].lower() if len(state['thoughts']) > 0 else ""
        t2 = state['thoughts'][1].lower() if len(state['thoughts']) > 1 else ""
        
        # We reject if the model found missing bounds or required fuzzing.
        if "missing" in t1 or "junk" in t1 or "fuzzing" in t2 or "tautology" in t2:
            return {"verdict": "REJECT: INSUFFICIENT HARDNESS"}
        else:
            return {"verdict": "ACCEPT: ATTESTATION VERIFIED"}

    def invoke(self, state: dict) -> dict:
        return self.app.invoke(state)

if __name__ == "__main__":
    auditor = DeepThinkAuditor()
    result = auditor.invoke({
        "math_problem": "Lagrange Index Multiplicativity",
        "lean_code": "theorem lagrange : H.card * H.index = G.card",
        "python_metrics": {"error": 0.0, "latency_ms": 3.15},
        "thoughts": []
    })
    print("Verdict Final de la Red Team :", result['verdict'])
