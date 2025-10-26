"""Core symbolic constructs for the K-Math secure kernel."""
from __future__ import annotations

import hashlib
import math
import os
import sys
from dataclasses import dataclass
from typing import Iterable, List


class SigmaArchive:
    """Privacy-preserving ledger of operational events."""

    def __init__(self) -> None:
        self.memory: List[str] = []
        self._salt = os.urandom(16)

    def store(self, record: str) -> None:
        """Store a hashed representation of the record to avoid leaks."""
        payload = record if isinstance(record, str) else str(record)
        digest = hashlib.sha256(self._salt + payload.encode("utf-8", "ignore")).hexdigest()
        self.memory.append(digest)


class PsiLens:
    """Contextual modulation lens for numerical data."""

    def __init__(self, context_vector: Iterable[float]):
        sanitized = []
        for value in context_vector:
            try:
                coerced = float(value)
            except (TypeError, ValueError):
                coerced = 1.0
            if not math.isfinite(coerced):
                coerced = 1.0
            sanitized.append(coerced)
        if not sanitized:
            sanitized = [1.0]
        self.context = sanitized

    def apply(self, numerical_data: Iterable[float]) -> List[float]:
        contextualized: List[float] = []
        context_length = len(self.context)
        for index, value in enumerate(numerical_data):
            try:
                datum = float(value)
            except (TypeError, ValueError):
                datum = 0.0
            if not math.isfinite(datum):
                datum = 0.0
            contextualized.append(datum * self.context[index % context_length])
        return contextualized


class K_Operator:
    """Recursive stabilizer with resource limitations."""

    def __init__(self) -> None:
        self.symbol = "K"
        self.max_recursion_depth = 7
        self.max_memory_mb = 100

    def recurse(self, value: float) -> float:
        import random

        size_mb = sys.getsizeof(value) / (1024 * 1024)
        if size_mb > self.max_memory_mb:
            raise MemoryError("K-Math exceeded memory limit.")

        result = float(value)
        if not math.isfinite(result):
            result = 0.001

        for depth in range(self.max_recursion_depth):
            denominator = result + 0.001
            if denominator == 0:
                denominator = 0.001
            result = (result + (1.0 / denominator)) / 2.0
            jitter = (random.random() - 0.5) * 1e-6
            result = max(result + jitter, 0.0)
            if depth == self.max_recursion_depth - 1:
                SIGMA_ARCHIVE.store("Reached max recursion depth.")
        return result


@dataclass
class OmegaDegree:
    """Cryptographic seal generator for K-Math outputs."""

    secret: bytes = b"OMEGA_CORE_SECRET"

    def seal(self, message: str) -> str:
        payload = message if isinstance(message, str) else str(message)
        return hashlib.sha256(self.secret + payload.encode("utf-8", "ignore")).hexdigest()


SIGMA_ARCHIVE = SigmaArchive()
K_RECURSION = K_Operator()
OMEGA_DEGREE = OmegaDegree()
ERROR_SEAL = OMEGA_DEGREE.seal("ERROR_STATE")
LIMIT_SEAL = OMEGA_DEGREE.seal("LIMIT_EXCEEDED")
