"""Symbolic primitives that underpin the Genesis Kernel."""
from __future__ import annotations

import hashlib
import math
import sys
from typing import Iterable, List


class SigmaArchive:
    """Lightweight logging archive that hashes all stored records."""

    def __init__(self) -> None:
        self.memory: List[str] = []

    def store(self, record: str) -> None:
        """Persist a hashed version of the provided record."""
        digest = hashlib.sha256(str(record).encode("utf-8", "ignore")).hexdigest()
        self.memory.append(digest)


class OmegaDegree:
    """Deterministic seal generator used to finalize kernel cycles."""

    def __init__(self) -> None:
        self._salt = b"K_MATH_SEAL"

    def seal(self, message: str) -> str:
        payload = message.encode("utf-8", "ignore")
        digest = hashlib.sha256(self._salt + payload).hexdigest()
        return digest


class PsiLens:
    """Contextual lens that modulates numerical inputs."""

    def __init__(self, context_vector: Iterable[float]) -> None:
        self.context_vector = list(context_vector) if context_vector is not None else []

    def apply(self, numerical_data: Iterable[float]) -> List[float]:
        context = self.context_vector or [1.0]
        contextualised: List[float] = []
        length = len(context)
        for index, value in enumerate(numerical_data):
            context_value = context[index % length]
            contextualised.append(float(value) * float(context_value))
        return contextualised


class KOperator:
    """Stability-focused recursive operator with strict resource limits."""

    def __init__(self) -> None:
        self.symbol = "K"
        self.max_recursion_depth = 7
        self.max_memory_mb = 100

    def recurse(self, value: float) -> float:
        payload = float(value)
        size_mb = sys.getsizeof(payload) / (1024 * 1024)
        if size_mb > self.max_memory_mb:
            raise MemoryError("K-Math exceeded memory limit.")

        for depth in range(self.max_recursion_depth):
            denominator = payload + 0.001
            if math.isclose(denominator, 0.0, abs_tol=1e-12):
                denominator = 0.001
            payload = (payload + (1.0 / denominator)) / 2.0
            if depth == self.max_recursion_depth - 1:
                SIGMA_ARCHIVE.store("Reached max recursion depth.")
        return payload


SIGMA_ARCHIVE = SigmaArchive()
OMEGA_DEGREE = OmegaDegree()
K_RECURSION = KOperator()

__all__ = [
    "SigmaArchive",
    "OmegaDegree",
    "PsiLens",
    "KOperator",
    "SIGMA_ARCHIVE",
    "OMEGA_DEGREE",
    "K_RECURSION",
]
