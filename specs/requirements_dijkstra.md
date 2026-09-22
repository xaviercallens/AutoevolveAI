# Requirements Document: Dijkstra's Shortest Path Algorithm (REQ-ALG-01)

## 1. Problem Statement
Implement a production-grade, highly performant, deterministic implementation of **Dijkstra's Algorithm** for single-source shortest paths on weighted directed or undirected graphs.

## 2. Functional Requirements
- **REQ-01 (Graph Representation):** Accept graphs represented as an adjacency mapping `Mapping[T, Iterable[tuple[T, float]]]` where `T` is any hashable vertex identifier (e.g., `str`, `int`, `tuple`).
- **REQ-02 (Single-Source Shortest Distances):** Given a source vertex $s \in V$, compute the exact shortest distance $d(s, v)$ for all reachable vertices $v \in V$. The distance to the source itself must be $d(s, s) = 0.0$.
- **REQ-03 (Path Reconstruction):** Provide efficient path reconstruction $s \rightsquigarrow v$ returning the ordered sequence of vertices along the shortest path.
- **REQ-04 (Target Early-Termination):** When an optional `target` vertex is provided, terminate search immediately once the target node is extracted from the priority queue, avoiding unnecessary graph traversal.
- **REQ-05 (Unreachable Vertices):** If a vertex $v$ is unreachable from $s$, its distance must be `math.inf` and its reconstructed path must be `None`.

## 3. Negative Weights & Error Handling
- **REQ-06 (Negative Weight Rejection):** If any visited edge has a negative weight ($w(u, v) < 0$), the algorithm must immediately raise `ValueError("Negative edge weights are not supported in Dijkstra's algorithm; use Bellman-Ford.")`. Silent corruption or infinite loops are strictly prohibited.
- **REQ-07 (Invalid Source / Empty Graph):** If the source vertex is not in the graph, return a result where only the source has distance 0.0 (or empty graph handling with distance 0.0 to itself).

## 4. Performance & Computational Physics Targets
- **REQ-08 (Algorithmic Complexity):**
  - Time complexity: $O((|V| + |E|) \log |V|)$ using a binary min-heap (`heapq`).
  - Auxiliary space complexity: $O(|V| + |E|)$.
- **REQ-09 (Thermodynamic Energy Function):**
  - Physical Energy $E = \text{duration\_ms} + \text{peak\_ram\_mb}$.
  - Performance target: For a graph of $|V| = 1,000$ vertices and $|E| = 5,000$ edges, execution duration must be $< 25$ ms, peak RAM $< 5$ MB, yielding energy $E < 30$.
  - Maximum Pain $E = 10^6$ applied if code crashes, produces invalid shortest paths, or times out ($> 2,000$ ms).

## 5. Engineering Quality & Anti-Stub Invariants
- **REQ-10 (Zero-Stub Guarantee):** Strict AST compliance: no `pass`, `...`, `TODO`, or mock fallbacks in production code.
- **REQ-11 (Type Safety & Immutability):** Full type annotations under Python 3.10+ strict typing (`from __future__ import annotations`). Result returned as an immutable or strongly typed dataclass `ShortestPathResult[T]`.
