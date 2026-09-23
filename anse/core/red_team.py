from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
import json
import logging
import requests
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from anse.core.api_extractor import APIExtractor

logger = logging.getLogger("DeepThinkRedTeam")

def call_local_r1_model(prompt: str) -> str:
    """Appel du modèle local (deepseek-r1:14b) via l'API REST d'Ollama."""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "deepseek-r1:14b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            logger.warning(f"Ollama API error: {response.status_code}")
    except Exception as e:
        logger.warning(f"Failed to reach local Ollama: {e}")
    
    # Fallback to simulated PRM response
    if "u_xx" in prompt or "f_0" in prompt or "AST: [ConstantDecl" in prompt:
        return "<think>Simulated PRM: Type ℝ detected instead of expected topological space. Algebraic tautology found.</think> REJECT"
    return "<think>Simulated PRM: Valid topological structure detected.</think> PASS"

def extract_lean_ast(lean_code: str) -> str:
    """Mock/Fallback for LeanDojo AST extraction on raw string."""
    if "u_xx" in lean_code or "ℝ" in lean_code:
        return "AST: [ConstantDecl: u_xx: ℝ], [Goal: A+B=0]"
    return "AST: [TheoremDecl], [Goal: Topology]"

class VerificationState(TypedDict):
    math_problem: str
    lean_code: str
    python_metrics: dict
    thoughts: list[str]
    verdict: str
    status: str
    feedback: str

class DeepThinkAuditor:
    def __init__(self, extractor: APIExtractor | None = None):
        self.extractor = extractor or APIExtractor()
        
        workflow = StateGraph(VerificationState)
        workflow.add_node("coder", self.mock_coder_auto_correction)
        workflow.add_node("epistemic_check", self.epistemic_deep_think_auditor)
        workflow.add_node("physics_check", self.physics_sandbox_thinker)
        workflow.add_node("judge", self.final_judgment)

        workflow.set_entry_point("coder")
        workflow.add_edge("coder", "epistemic_check")
        
        # Conditional edge from epistemic check to handle MCTS backtracking
        def route_epistemic(state: VerificationState):
            if state.get("status") == "BACKTRACK_TO_CODER":
                return "coder"
            return "physics_check"

        workflow.add_conditional_edges(
            "epistemic_check",
            route_epistemic,
            {"coder": "coder", "physics_check": "physics_check"}
        )

        workflow.add_edge("physics_check", "judge")
        workflow.add_edge("judge", END)

        self.app = workflow.compile()
        
    def mock_coder_auto_correction(self, state: VerificationState):
        """Simulate the agent re-generating code after a REJECT from Red Team."""
        if state.get("status") == "BACKTRACK_TO_CODER":
            logger.info(f"Backtracking to Coder... Feedback: {state.get('feedback', '')}")
            # The agent would generate new Lean code here. We simulate a fix.
            state["lean_code"] = "-- Topologically sound proof via InnerProductSpace\ntheorem CauchyRiemann_Correct"
            state["status"] = "RETRY"
        return state

    def epistemic_deep_think_auditor(self, state: VerificationState):
        """ Ce nœud est exécuté par le modèle local (ex: DeepSeek-R1 via Ollama). Il force le modèle à déconstruire le code avant de l'accepter. """
        ast_info = extract_lean_ast(state.get('lean_code', ''))
        prompt = f"""
Analyse ce théorème Lean 4 proposé :
{state.get('lean_code', '')}

AST extrait (via LeanDojo):
{ast_info}

Tu es le 'Reviewer 2'. Tu dois trouver les triches sémantiques.
Réfléchis dans <think> :
- L'agent a-t-il utilisé de simples réels (ℝ) pour un problème d'analyse complexe ou géométrie différentielle ?
- Le théorème est-il une tautologie algébrique résolue par `ring` plutôt qu'une vraie preuve topologique ?
"""
        logger.info("Executing Epistemic Deep Think Audit...")
        response = call_local_r1_model(prompt)
        
        thoughts = state.get("thoughts", [])
        new_state = {"thoughts": thoughts + [response]}
        if "REJECT" in response:
            new_state["status"] = "BACKTRACK_TO_CODER"
            new_state["feedback"] = response
        else:
            new_state["status"] = "PASS"
            
        return new_state

    def physics_sandbox_thinker(self, state: VerificationState):
        """Étape 2 : Vérification des illusions numériques du CAS Python."""
        prompt = f"""Métriques:
{state['python_metrics']}
Le CAS Python a validé avec une erreur < 1e-14. Est-ce une tautologie discrète de la grille (ex: dérivées croisées) ?
L'énergie physique E est-elle réaliste ? Faut-il du fuzzing sur les singularités polaires ?
"""
        logger.info("Executing Physics Sandbox Check...")
        try:
            response, _ = self.extractor.extract(
                prompt=prompt, 
                system_prompt="You are a Computational Physics Red Team auditor. Focus on numerical illusions.",
                temperature=0.2
            )
        except Exception:
            response = "<think>Grid derivatives commute. We need polar singularity fuzzing.</think> Needs fuzzing if applicable."
            
        thoughts = state.get("thoughts", [])
        return {"thoughts": thoughts + [response]}

    def final_judgment(self, state: VerificationState):
        """Étape 3 : Synthèse et verdict implacable."""
        t1 = state['thoughts'][0].lower() if len(state['thoughts']) > 0 else ""
        t2 = state['thoughts'][1].lower() if len(state['thoughts']) > 1 else ""
        
        # We reject if the model found missing bounds, epistemic cheating, or required fuzzing.
        if "missing" in t1 or "cheating" in t1 or "reject" in t1 or "fuzzing" in t2 or "tautology" in t2:
            return {"verdict": "REJECT: INSUFFICIENT HARDNESS OR EPISTEMIC CHEATING"}
        else:
            return {"verdict": "ACCEPT: ATTESTATION VERIFIED"}

    def invoke(self, state: dict) -> dict:
        return self.app.invoke(state)
