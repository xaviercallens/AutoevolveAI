# Specification: Tarjan's SCC & DAG Condenser Engine (SPEC-ALG-TARJAN)

## 1. Mathematical Formulation
Given a directed graph $G = (V, E)$:

1. **Strongly Connected Component (SCC):**
   A maximal subset $C \subseteq V$ such that every pair of vertices in $C$ are mutually reachable.
2. **Tarjan's DFS Invariant:**
   During a depth-first search, each vertex $v$ maintains:
   - $\text{disc}[v]$: DFS discovery timestamp.
   - $\text{low}[v]$: Minimum discovery timestamp reachable from $v$ via tree edges and cross/back edges to vertices currently on the active stack $S$.
   $$\text{low}[v] = \min \begin{cases} \text{disc}[v] \\ \text{low}[w] & \text{for tree edge } (v, w) \\ \text{disc}[w] & \text{for back/cross edge } (v, w) \text{ with } w \in S \end{cases}$$
3. **Root of Component:**
   $\text{low}[v] == \text{disc}[v] \iff v$ is the root of an SCC.
4. **Quotient DAG Condensation:**
   Contracting each SCC $C_i$ into a single node produces a guaranteed Directed Acyclic Graph $G^{\text{SCC}} = (V_{\text{SCC}}, E_{\text{SCC}})$.
   Topological ordering of $G^{\text{SCC}}$ provides a deadlock-free execution order for agent microservice swarms.

## 2. API Contract
```python
from __future__ import annotations
from typing import Generic, Hashable, Iterable, Mapping, TypeVar
from dataclasses import dataclass

T = TypeVar("T", bound=Hashable)

@dataclass(frozen=True)
class SCCResult(Generic[T]):
    components: list[list[T]]
    node_to_component: dict[T, int]
    is_dag: bool
    cyclic_components: list[list[T]]
    condensed_dag: dict[int, list[int]]
    topological_order: list[int]

def find_strongly_connected_components(
    graph: Mapping[T, Iterable[T]],
) -> SCCResult[T]:
    ...
```
