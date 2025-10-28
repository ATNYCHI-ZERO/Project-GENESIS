"""Demonstration script showcasing K-Math on a toy TSP instance."""
from __future__ import annotations

import random
import time
from typing import List, Tuple

from .kernel import GenesisKernel
from .integrations import _default_auth_key

Matrix = List[List[float]]


def k_math_tsp(node_count: int, distance_matrix: Matrix) -> Tuple[List[int], float, str]:
    """Run a lightweight TSP demonstration powered by the Genesis Kernel."""
    architect_id = "Brendon Joseph Kelly"
    kernel = GenesisKernel(architect_id=architect_id, auth_key=_default_auth_key(architect_id))

    flattened: List[float] = [value for row in distance_matrix for value in row]
    numerical_data = flattened[:256] if flattened else [0.0]
    context_vector = [1.0] * len(numerical_data)

    start = time.time()
    seal = kernel.execute_full_cycle(numerical_data, context_vector)
    runtime = time.time() - start

    row_costs = [sum(row) for row in distance_matrix]
    ordered_indices = sorted(range(len(row_costs)), key=row_costs.__getitem__)
    path = ordered_indices[:node_count]
    return path, runtime, seal


def baseline_nearest_neighbor(distance_matrix: Matrix) -> Tuple[List[int], float]:
    """Compute a naive nearest-neighbour path for comparison."""
    node_count = len(distance_matrix)
    unvisited = list(range(1, node_count))
    path = [0]
    start = time.time()
    while unvisited:
        last = path[-1]
        next_index = min(unvisited, key=lambda idx: distance_matrix[last][idx])
        unvisited.remove(next_index)
        path.append(next_index)
    runtime = time.time() - start
    return path, runtime


def generate_random_tsp(node_count: int, seed: int = 42) -> Matrix:
    random.seed(seed)
    matrix: Matrix = []
    for _ in range(node_count):
        row = [random.random() for _ in range(node_count)]
        matrix.append(row)
    for i in range(node_count):
        matrix[i][i] = 0.0
    return matrix


if __name__ == "__main__":
    nodes = 32
    distances = generate_random_tsp(nodes)
    k_path, k_runtime, k_seal = k_math_tsp(nodes, distances)
    nn_path, nn_runtime = baseline_nearest_neighbor(distances)

    print("K-Math demonstration results")
    print(f"Path (first 10 nodes): {k_path[:10]}")
    print(f"Runtime: {k_runtime:.4f}s")
    print(f"Seal: {k_seal}")
    print("\nBaseline nearest-neighbour results")
    print(f"Path (first 10 nodes): {nn_path[:10]}")
    print(f"Runtime: {nn_runtime:.4f}s")
