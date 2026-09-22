# Technical Specification: Dijkstra Shortest Path Engine (SPEC-ALG-01)

## 1. Architectural Overview
This specification defines the formal mathematics, data structures, and runtime contracts for the Dijkstra implementation in `anse.algorithms.dijkstra`.

## 2. Mathematical Formalization

Let $G = (V, E)$ be a directed graph with non-negative edge weight function $w: E \to \mathbb{R}_{\ge 0}$.
For a source vertex $s \in V$:
- **Distance Function:**
  $$d^*(s, v) = \min_{p \in P(s, v)} \sum_{e \in p} w(e)$$
  where $P(s, v)$ is the set of all directed paths from $s$ to $v$. If $P(s, v) = \emptyset$, $d^*(s, v) = \infty$.
- **Relaxation Invariant:**
  For any edge $(u, v) \in E$, after convergence:
  $$d(v) \le d(u) + w(u, v) \quad \text{(Triangle Inequality)}$$
- **Monotonicity of Extracted Distances:**
  In Dijkstra's algorithm, the sequence of distances of vertices extracted from the priority queue is monotonically non-decreasing:
  $$\forall i < j: d(u_i) \le d(u_j)$$
  This guarantees that once a vertex is settled, its distance is optimal.

## 3. Data Structures & API Contracts

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Hashable, Mapping, Iterable, TypeVar

T = TypeVar("T", bound=Hashable)

@dataclass(frozen=True)
class ShortestPathResult(Generic[T]):
    source: T
    distances: dict[T, float]
    predecessors: dict[T, T | None]
    settled_count: int

    def get_distance(self, target: T) -> float:
        """Return shortest distance or math.inf if unreachable."""
        ...

    def get_path(self, target: T) -> list[T] | None:
        """Reconstruct shortest path [source, ..., target] or None if unreachable."""
        ...
```

### Main Entrypoint:
```python
def dijkstra_shortest_paths(
    graph: Mapping[T, Iterable[tuple[T, float]]],
    source: T,
    target: T | None = None,
) -> ShortestPathResult[T]:
    """
    Compute single-source shortest paths using binary min-heap priority queue.
    
    Raises:
        ValueError: If any negative edge weight is encountered.
    """
    ...
```

## 4. Priority Queue Optimization: Visited Pruning
To prevent redundant operations when vertices are inserted into the min-heap multiple times with updated relaxed distances (decrease-key equivalent in binary heaps):
1. Maintain a `visited: set[T]` of settled vertices.
2. Upon popping `(dist, u)` from the heap:
   ```python
   if u in visited:
       continue
   visited.add(u)
   ```
3. Skip edge relaxation if the neighbor is already in `visited`.
4. Early termination: If `target is not None and u == target`, break immediately.

## 5. Physical Energy & Thermodynamic Contract ($E$)
- **Energy Metric:** $E = \text{duration\_ms} + \text{peak\_ram\_mb}$
- **Energy Budget:**
  - Fast baseline benchmark: 1,000 vertices, 4,000 edges.
  - Energy Upper Bound: $E < 30.0$.
- **Thermodynamic Selection:**
  A candidate refactoring is accepted by the hypervisor iff:
  $$\Delta E = E_{\text{child}} - E_{\text{parent}} < 0$$
- **Pain Signal ($E = 10^6$):** Triggered on uncaught exceptions, negative weight undetected, or non-optimal paths.
