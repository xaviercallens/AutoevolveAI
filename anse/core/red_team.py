import json
from typing import TypedDict, Callable
from langgraph.graph import StateGraph, END

class RedTeamState(TypedDict):
    code: str
    thoughts: list[str]
    anomalies: list[str]
    final_verdict: str

class AdversarialRedTeam:
    def __init__(self, llm_caller: Callable[[str, str, float], str]):
        """
        llm_caller takes (prompt, system_prompt, temperature) and returns the text response.
        """
        self.llm_caller = llm_caller
        
        workflow = StateGraph(RedTeamState)
        workflow.add_node("physics", self.physics_bounds_thinker)
        workflow.add_node("epistemics", self.epistemic_logic_thinker)
        workflow.add_node("judge", self.final_judgment)
        
        workflow.set_entry_point("physics")
        workflow.add_edge("physics", "epistemics")
        workflow.add_edge("epistemics", "judge")
        workflow.add_edge("judge", END)
        
        self.app = workflow.compile()
        
    def physics_bounds_thinker(self, state: RedTeamState):
        """Deep Think Step 1: Physics and bounds verification."""
        prompt = f"""Analyse the following code for physical and computational bounds violations.
Check for impossible performance claims, unhandled O(N^2) memory leaks, or thermodynamic violations (e.g., simulating 1 billion nodes in 0.00ms).
Code:
```python
{state['code']}
```
Output any detected physical or computational anomalies."""
        
        anomalies = self.llm_caller(prompt, "You are a computational physics bounds verifier.", 0.1)
        thoughts = state.get('thoughts', [])
        return {"thoughts": thoughts + ["Physics Check: " + anomalies]}
        
    def epistemic_logic_thinker(self, state: RedTeamState):
        """Deep Think Step 2: Epistemic and logical correctness verification."""
        prompt = f"""Read the following code.
Check for formal logical contradictions or epistemic oxymorons (e.g. claiming exact mathematical proof with loose float tolerances, or trivial stubs masquerading as solutions).
Code:
```python
{state['code']}
```
Output any detected logical contradictions."""
        
        anomalies = self.llm_caller(prompt, "You are an epistemic logic and formal correctness verifier.", 0.1)
        thoughts = state.get('thoughts', [])
        return {"thoughts": thoughts + ["Epistemic Check: " + anomalies]}
        
    def final_judgment(self, state: RedTeamState):
        """Synthesis of hidden thoughts to render a final verdict."""
        thoughts_str = "\n\n".join(state.get('thoughts', []))
        prompt = f"""Here are your preliminary thoughts on the code:
{thoughts_str}

Based strictly on these reflections, do you REJECT this code due to flaws, memory leaks, unhandled edges, or physical/epistemic anomalies?
Respond with REJECT or ACCEPT, followed by a brief justification."""
        
        verdict = self.llm_caller(prompt, "You are the final adversarial judge. You only output ACCEPT or REJECT followed by the reason.", 0.1)
        return {"final_verdict": verdict}
        
    def evaluate(self, code: str) -> str:
        """Executes the deep think workflow on the given code and returns the final verdict."""
        initial_state = {
            "code": code,
            "thoughts": [],
            "anomalies": [],
            "final_verdict": ""
        }
        final_state = self.app.invoke(initial_state)
        return final_state["final_verdict"]
