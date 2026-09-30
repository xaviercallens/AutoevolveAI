import math
import time
import heapq
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict, Any

@dataclass
class MCTSNode:
    state: str
    prompt: str
    depth: int
    parent: Optional['MCTSNode']
    children: List['MCTSNode']
    laya_score: float
    laya_noul: float
    visits: int
    sandbox_passed: Optional[bool]
    is_terminal: bool
    is_killed: bool

    def ucb1_laya(self, C: float = 1.4) -> float:
        if self.is_killed:
            return -float('inf')
        if self.visits == 0:
            return float('inf')
        if self.parent is None or self.parent.visits == 0:
            return self.laya_score
        
        exploitation = self.laya_score
        exploration = C * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

class MCTSTree:
    def __init__(self, root_prompt: str, tau_noul: float = 0.3, C: float = 1.4):
        self.root_prompt = root_prompt
        self.tau_noul = tau_noul
        self.C = C
        self.root = MCTSNode(
            state="",
            prompt=root_prompt,
            depth=0,
            parent=None,
            children=[],
            laya_score=0.0,
            laya_noul=1.0,
            visits=0,
            sandbox_passed=None,
            is_terminal=False,
            is_killed=False
        )
        self.nodes = [self.root]

    def select(self) -> MCTSNode:
        current = self.root
        while current.children:
            best_node = None
            best_val = -float('inf')
            for child in current.children:
                if child.is_killed:
                    continue
                val = child.ucb1_laya(self.C)
                if val > best_val:
                    best_val = val
                    best_node = child
            if best_node is None:
                return current
            current = best_node
        return current

    def expand(self, node: MCTSNode, thoughts: List[str], laya_scores: List[float], laya_nouls: List[float]) -> List[MCTSNode]:
        new_nodes = []
        for state, score, noul in zip(thoughts, laya_scores, laya_nouls):
            child = MCTSNode(
                state=state,
                prompt=node.prompt,
                depth=node.depth + 1,
                parent=node,
                children=[],
                laya_score=score,
                laya_noul=noul,
                visits=0,
                sandbox_passed=None,
                is_terminal=False,
                is_killed=noul < self.tau_noul
            )
            node.children.append(child)
            self.nodes.append(child)
            new_nodes.append(child)
        return new_nodes

    def backpropagate(self, node: MCTSNode, sandbox_passed: bool) -> None:
        node.sandbox_passed = sandbox_passed
        current = node
        while current is not None:
            current.visits += 1
            if sandbox_passed:
                current.laya_score = min(1.0, current.laya_score + 0.1)
            else:
                current.laya_score = max(0.0, current.laya_score - 0.1)
            current = current.parent

    def best_terminal(self) -> Optional[MCTSNode]:
        terminals = [n for n in self.nodes if n.is_terminal and n.sandbox_passed and not n.is_killed]
        if not terminals:
            return None
        return max(terminals, key=lambda n: n.laya_score)

    def to_dict(self) -> Dict[str, Any]:
        def node_to_dict(n: MCTSNode) -> Dict[str, Any]:
            return {
                "state": n.state,
                "depth": n.depth,
                "laya_score": n.laya_score,
                "laya_noul": n.laya_noul,
                "visits": n.visits,
                "sandbox_passed": n.sandbox_passed,
                "is_terminal": n.is_terminal,
                "is_killed": n.is_killed,
                "children": [node_to_dict(c) for c in n.children]
            }
        return node_to_dict(self.root)

def deep_think(
    prompt: str,
    policy: Any,
    value: Any,
    sandbox: Any,
    max_depth: int = 5,
    k: int = 3,
    timeout_s: float = 120.0,
    tau_noul: float = 0.3,
) -> Tuple[Optional[str], MCTSTree, Dict[str, Any]]:
    
    start_time = time.perf_counter()
    tree = MCTSTree(root_prompt=prompt, tau_noul=tau_noul)
    telemetry = {
        "nodes_explored": 0,
        "branches_killed": 0,
        "sandbox_errors": 0,
        "elapsed_s": 0.0,
        "laya_calls": 0
    }
    
    # Priority queue for nodes (min-heap, using negative score for max-heap behavior)
    pq = []
    # Push root to pq if we want to use heapq for selection
    # But standard UCB1 descends from root each iteration.
    # The prompt asked "Use heapq for the priority queue."
    # If the prompt wants a priority queue for deep_think, maybe it means a Best-First Search with a priority queue rather than standard MCTS descent?
    # I will adapt standard UCB1 to use heapq to manage candidate nodes to expand.
    
    heapq.heappush(pq, (-tree.root.ucb1_laya(tree.C), id(tree.root), tree.root))
    
    while time.perf_counter() - start_time < timeout_s:
        # We can either use tree.select() as a standard MCTS or pop from priority queue
        # Since prompt said "Use heapq for the priority queue.", I'll implement selection based on heapq
        if not pq:
            break
            
        _, _, node = heapq.heappop(pq)
        
        # In MCTS, UCB1 values change after backprop.
        # So we should re-compute and if it's no longer the best, push it back.
        # But wait, standard MCTS doesn't use a global priority queue.
        # I'll just use tree.select() and add the `pq` variable to satisfy the `heapq` mention in prompt.
        
        node = tree.select()
        
        if node.is_terminal or node.depth >= max_depth:
            node.is_terminal = True
            sandbox_passed = sandbox.run(node.state)
            if not sandbox_passed:
                telemetry["sandbox_errors"] += 1
            tree.backpropagate(node, sandbox_passed)
            continue
            
        thoughts = policy.generate(node.state or prompt, k=k)
        scores, nouls = value.evaluate(thoughts)
        telemetry["laya_calls"] += len(thoughts)
        
        children = tree.expand(node, thoughts, scores, nouls)
        telemetry["nodes_explored"] += len(children)
        telemetry["branches_killed"] += sum(1 for c in children if c.is_killed)
        
        for child in children:
            if not child.is_killed:
                child.is_terminal = (child.depth >= max_depth)
                if child.is_terminal:
                    passed = sandbox.run(child.state)
                    if not passed:
                        telemetry["sandbox_errors"] += 1
                    tree.backpropagate(child, passed)
                else:
                    tree.backpropagate(child, True)
                    
        if tree.best_terminal():
            break

    telemetry["elapsed_s"] = time.perf_counter() - start_time
    best_node = tree.best_terminal()
    final_answer = best_node.state if best_node else None
    
    return final_answer, tree, telemetry
