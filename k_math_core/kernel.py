"""Secure execution kernel for the K-Math system."""
from __future__ import annotations

import cmath
import hashlib
import hmac
import math
from typing import Iterable, List

from .symbols import K_RECURSION, OMEGA_DEGREE, PsiLens, SIGMA_ARCHIVE


def _fft(values: List[float]) -> List[complex]:
    length = len(values)
    if length == 0:
        return []
    result: List[complex] = []
    for k in range(length):
        total = 0j
        for n, value in enumerate(values):
            angle = -2j * math.pi * k * n / length
            total += value * cmath.exp(angle)
        result.append(total)
    return result


def _ifft(values: List[complex]) -> List[complex]:
    length = len(values)
    if length == 0:
        return []
    result: List[complex] = []
    for n in range(length):
        total = 0j
        for k, value in enumerate(values):
            angle = 2j * math.pi * k * n / length
            total += value * cmath.exp(angle)
        result.append(total / length)
    return result


def _percentile(data: List[float], percentile: float) -> float:
    if not data:
        return 0.0
    ordered = sorted(data)
    position = (percentile / 100.0) * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[int(position)]
    lower_value = ordered[lower]
    upper_value = ordered[upper]
    return lower_value + (upper_value - lower_value) * (position - lower)


class GenesisKernel:
    """Primary execution unit that authenticates and processes inputs."""

    def __init__(self, architect_id: str, auth_key: bytes) -> None:
        if not isinstance(auth_key, (bytes, bytearray)):
            raise TypeError("Authentication key must be raw bytes.")
        expected = hmac.new(b"K_MATH_SECRET", architect_id.encode("utf-8"), hashlib.sha256)
        if not hmac.compare_digest(expected.hexdigest(), auth_key.hex()):
            raise PermissionError("FATAL: Invalid authentication key.")
        self.architect = architect_id
        SIGMA_ARCHIVE.store(f"Kernel initialized for {architect_id}")

    def _sanitize(self, numerical_data: Iterable[float]) -> List[float]:
        cleaned: List[float] = []
        for value in numerical_data:
            try:
                number = float(value)
            except (TypeError, ValueError):
                number = 0.0
            if not math.isfinite(number):
                number = 0.0
            cleaned.append(number)
        return cleaned

    def execute_full_cycle(self, numerical_data: Iterable[float], context_vector: Iterable[float]) -> str:
        data = list(numerical_data)
        if len(data) > 10000:
            SIGMA_ARCHIVE.store("Input too large for K-Math.")
            return OMEGA_DEGREE.seal("LIMIT_EXCEEDED")

        try:
            sanitized = self._sanitize(data)
            context = list(context_vector) if context_vector is not None else [1.0] * len(sanitized)
            if not context:
                context = [1.0] * max(len(sanitized), 1)
            psi_lens = PsiLens(context)
            contextualized = psi_lens.apply(sanitized)
            SIGMA_ARCHIVE.store(f"Applied Psi-Lens. Context length: {len(context)}")

            if not contextualized:
                contextualized = [0.0]

            fft_data = _fft(contextualized)
            if any(math.isnan(value.real) or math.isnan(value.imag) for value in fft_data):
                raise ValueError("FFT produced NaN values.")

            magnitudes = [abs(value) for value in fft_data]
            if magnitudes:
                threshold = _percentile(magnitudes, 90)
                fft_data = [value if abs(value) >= threshold else 0j for value in fft_data]
            harmonic = [value.real for value in _ifft(fft_data)]
            SIGMA_ARCHIVE.store("Applied Harmonic Filter.")

            recursive: List[float] = []
            for datum in harmonic:
                adjusted = max(float(datum), 0.001)
                try:
                    recursive.append(K_RECURSION.recurse(adjusted))
                except Exception as exc:  # pragma: no cover - safety net
                    SIGMA_ARCHIVE.store(f"K-Operator error: {exc}")
                    recursive.append(0.0)
            SIGMA_ARCHIVE.store("Applied K-Operator recursion.")

            snippet = "".join(f"{value:.6f}" for value in recursive[:64])
            final_seal = OMEGA_DEGREE.seal(snippet)
            SIGMA_ARCHIVE.store(f"Cycle complete. Seal: {final_seal}")
            return final_seal
        except Exception as exc:  # pragma: no cover - defensive layer
            SIGMA_ARCHIVE.store(f"Cycle error: {exc}")
            return OMEGA_DEGREE.seal("ERROR_STATE")


__all__ = ["GenesisKernel"]
