"""Demonstration script showcasing a secure K-Math optimization cycle."""
from __future__ import annotations

import random
import time
from itertools import chain
from typing import List, Tuple

from .kernel import GenesisKernel, generate_auth_key


def _generate_distance_matrix(nodes: int, seed: int | None = None) -> List[List[float]]:
    rng = random.Random(seed)
    matrix: List[List[float]] = [[0.0 for _ in range(nodes)] for _ in range(nodes)]
    for i in range(nodes):
        for j in range(i + 1, nodes):
            distance = rng.uniform(1.0, 100.0)
            matrix[i][j] = matrix[j][i] = distance
    return matrix


def _heuristic_path(matrix: List[List[float]]) -> List[int]:
    nodes = list(range(len(matrix)))
    if not nodes:
        return []
    visited = [nodes[0]]
    remaining = set(nodes[1:])
    while remaining:
        last = visited[-1]
        next_node = min(remaining, key=lambda node: matrix[last][node])
        visited.append(next_node)
        remaining.remove(next_node)
    return visited


def k_math_tsp(nodes: int = 32, seed: int | None = None) -> Tuple[List[int], float, str]:
    """Run a simple traveling salesman heuristic and return the sealed result."""
    architect_id = "Brendon Joseph Kelly"
    kernel = GenesisKernel(architect_id=architect_id, auth_key=generate_auth_key(architect_id))
    matrix = _generate_distance_matrix(nodes, seed=seed)
    data = list(chain.from_iterable(matrix))[:256]
    context = [1.0] * len(data)
    start_time = time.time()
    seal = kernel.execute_full_cycle(data, context)
    path = _heuristic_path(matrix)
    runtime = time.time() - start_time
    return path, runtime, seal


if __name__ == "__main__":  # pragma: no cover - manual demonstration
    path, runtime, seal = k_math_tsp(32, seed=42)
    print(f"Heuristic path length: {len(path)} nodes")
    print(f"Runtime: {runtime:.4f} seconds")
    print(f"Seal: {seal}")
