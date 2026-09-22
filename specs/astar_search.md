# Specification: A* Search Engine with Admissible Heuristics (SPEC-ALG-ASTAR)

## 1. Mathematical Formulation
A* evaluates vertices $n$ using the evaluation function:
$$f(n) = g(n) + h(n)$$
where:
- $g(n)$ is the exact cost of the path from the starting state $s$ to vertex $n$.
- $h(n)$ is an admissible heuristic estimating the cheapest cost from $n$ to the goal $t$:
  $$\forall n, \quad 0 \le h(n) \le h^*(n)$$
- **Consistency (Monotonicity):**
  For every edge $(u, v)$ with cost $c(u, v)$:
  $$h(u) \le c(u, v) + h(v)$$
  Consistency guarantees that once a node is settled (expanded), its $g(n)$ is optimal and no re-expansions are required.

## 2. API Contract
```python
from __future__ import annotations
from typing import Callable, Generic, Hashable, Iterable, Mapping, TypeVar
from dataclasses import dataclass

T = TypeVar("T", bound=Hashable)

@dataclass(frozen=True)
class AStarResult(Generic[T]):
    source: T
    target: T
    path: list[T]
    cost: float
    nodes_settled: int
    nodes_generated: int

def astar_search(
    neighbors_fn: Callable[[T], Iterable[tuple[T, float]]],
    heuristic_fn: Callable[[T, T], float],
    source: T,
    target: T,
) -> AStarResult[T] | None:
    ...
```

## 3. Physical Invariant & Thermodynamic Objective
- Admissible heuristic prunes state expansions, settling $\le 25\%$ of the nodes expanded by unguided Dijkstra on Euclidean grids.
- Thermodynamic Energy: $E = \text{duration\_ms} + \text{peak\_ram\_mb}$. Monotonic descent $\Delta E < 0$ vs. Dijkstra.
