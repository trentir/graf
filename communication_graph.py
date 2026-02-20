"""Utilities for validating and classifying communication graphs.

A communication graph is represented as:
    Neighborhood = dict[int, set[int]]
where keys are process identifiers (vertices), and values are sets of outgoing
neighbors for each process.
"""

from __future__ import annotations

from collections import deque
from typing import TypeAlias

Neighborhood: TypeAlias = dict[int, set[int]]


def isNeighborhoodCorrect(neighborhood: Neighborhood) -> bool:
    """Return True if ``neighborhood`` is a correctly represented graph.

    Rules used in this implementation (minimal + explicit assumptions):
    1. ``neighborhood`` must be a ``dict``.
    2. Every key (vertex id) must be an ``int``.
    3. Every value must be a ``set`` of ``int`` neighbor ids.
    4. Every referenced neighbor must also be present as a key in the dict.
       (Closed vertex set: no edges to unknown vertices.)
    5. Self-loops ``p -> p`` are not allowed.

    Notes:
    - Empty graph is considered correctly represented.
    - Multiple edges are naturally impossible due to the ``set`` container.
    """
    if not isinstance(neighborhood, dict):
        return False

    vertices = set(neighborhood.keys())

    for vertex, neighbors in neighborhood.items():
        if not isinstance(vertex, int):
            return False
        if not isinstance(neighbors, set):
            return False

        for nbr in neighbors:
            if not isinstance(nbr, int):
                return False
            if nbr not in vertices:
                return False
            if nbr == vertex:
                return False

    return True


def isUndirected(neighborhood: Neighborhood) -> bool:
    """Return True if the graph is correctly represented and undirected.

    Undirected here means edge symmetry:
    if ``v in N[u]``, then ``u in N[v]``.
    """
    if not isNeighborhoodCorrect(neighborhood):
        return False

    for u, neighbors in neighborhood.items():
        for v in neighbors:
            if u not in neighborhood[v]:
                return False

    return True


def isTree(neighborhood: Neighborhood) -> bool:
    """Return True if the graph is a correctly represented undirected tree.

    Criteria used:
    - graph is correct,
    - graph is undirected,
    - graph is connected,
    - number of undirected edges is ``n - 1``.

    Assumption: empty graph is NOT a tree.
    """
    if not isNeighborhoodCorrect(neighborhood):
        return False
    if not isUndirected(neighborhood):
        return False

    n = len(neighborhood)
    if n == 0:
        return False

    # Count undirected edges (each appears twice in adjacency sets).
    edges_twice = sum(len(neighbors) for neighbors in neighborhood.values())
    if edges_twice % 2 != 0:
        return False
    edges = edges_twice // 2

    if edges != n - 1:
        return False

    # Connectivity check via BFS.
    start = next(iter(neighborhood))
    visited: set[int] = set()
    queue: deque[int] = deque([start])

    while queue:
        u = queue.popleft()
        if u in visited:
            continue
        visited.add(u)
        for v in neighborhood[u]:
            if v not in visited:
                queue.append(v)

    return len(visited) == n


def _run_self_tests() -> None:
    """Small built-in test suite with plain asserts."""

    # 1) Invalid types.
    assert isNeighborhoodCorrect([]) is False
    assert isNeighborhoodCorrect({1: [2]}) is False  # neighbors must be a set
    assert isNeighborhoodCorrect({"1": {2}, 2: {1}}) is False

    # 2) Edge to non-existing vertex.
    assert isNeighborhoodCorrect({1: {2}, 2: {1, 3}}) is False

    # 3) Directed (non-symmetric) graph.
    directed = {1: {2}, 2: set()}
    assert isNeighborhoodCorrect(directed) is True
    assert isUndirected(directed) is False
    assert isTree(directed) is False

    # 4) Correct tree.
    tree = {
        1: {2, 3},
        2: {1, 4},
        3: {1},
        4: {2},
    }
    assert isNeighborhoodCorrect(tree) is True
    assert isUndirected(tree) is True
    assert isTree(tree) is True

    # 5) Undirected graph with cycle (not a tree).
    cycle_graph = {
        1: {2, 3},
        2: {1, 3},
        3: {1, 2},
    }
    assert isNeighborhoodCorrect(cycle_graph) is True
    assert isUndirected(cycle_graph) is True
    assert isTree(cycle_graph) is False

    # 6) Edge cases: 0 and 1 vertex.
    empty: Neighborhood = {}
    single: Neighborhood = {7: set()}
    assert isNeighborhoodCorrect(empty) is True
    assert isUndirected(empty) is True
    assert isTree(empty) is False
    assert isNeighborhoodCorrect(single) is True
    assert isUndirected(single) is True
    assert isTree(single) is True


if __name__ == "__main__":
    _run_self_tests()
    print("All self-tests passed.")
