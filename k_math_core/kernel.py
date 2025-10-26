"""Secure execution kernel for the K-Math framework."""
from __future__ import annotations

import cmath
import hmac
import hashlib
import math
from typing import Iterable

from .symbols import (
    ERROR_SEAL,
    LIMIT_SEAL,
    OMEGA_DEGREE,
    K_RECURSION,
    PsiLens,
    SIGMA_ARCHIVE,
)

_AUTH_SECRET = b"K_MATH_SECRET"


def generate_auth_key(architect_id: str) -> bytes:
    """Generate an authentication key for an architect identifier."""
    if not isinstance(architect_id, str) or not architect_id:
        raise ValueError("architect_id must be a non-empty string")
    return hmac.new(_AUTH_SECRET, architect_id.encode("utf-8"), hashlib.sha256).digest()


class GenesisKernel:
    """Authenticated execution core applying the K-Math pipeline."""

    def __init__(self, architect_id: str, auth_key: bytes) -> None:
        expected = generate_auth_key(architect_id)
        if not hmac.compare_digest(expected, auth_key):
            raise PermissionError("FATAL: Invalid authentication key.")
        self.architect = architect_id

    def execute_full_cycle(
        self, numerical_data: Iterable[float], context_vector: Iterable[float]
    ) -> str:
        """Execute the harmonized K-Math pipeline and return a sealed result."""
        try:
            data_list = [float(x) for x in numerical_data]
        except (TypeError, ValueError):
            data_list = [0.0]

        try:
            context_list = [float(x) for x in context_vector]
        except (TypeError, ValueError):
            context_list = [1.0] * len(data_list)

        if len(data_list) != len(context_list):
            min_len = min(len(data_list), len(context_list))
            if min_len == 0:
                data_list = (data_list or [0.0])[:1]
                context_list = (context_list or [1.0])[:1]
            else:
                data_list = data_list[:min_len]
                context_list = context_list[:min_len]

        if len(data_list) > 10000:
            SIGMA_ARCHIVE.store("Input too large for K-Math.")
            return LIMIT_SEAL

        try:
            lens = PsiLens(context_list)
            contextualized = lens.apply(data_list)
            SIGMA_ARCHIVE.store("Applied Psi-Lens.")

            fft_data = _discrete_fourier_transform(contextualized)
            magnitudes = [abs(value) for value in fft_data]
            if any(math.isnan(magnitude) for magnitude in magnitudes):
                raise ValueError("FFT produced NaN values")
            threshold = _percentile(magnitudes, 90)
            filtered_fft = [value if abs(value) >= threshold else 0j for value in fft_data]
            harmonic_data = _inverse_discrete_fourier_transform(filtered_fft)
            SIGMA_ARCHIVE.store("Applied Harmonic Filter.")

            recursive_data = []
            for datum in harmonic_data:
                safe_value = max(float(datum), 0.001)
                recursive_data.append(K_RECURSION.recurse(safe_value))
            SIGMA_ARCHIVE.store("Applied K-Operator recursion.")

            final_string = "".join(f"{value:.6f}" for value in recursive_data)
            final_seal = OMEGA_DEGREE.seal(final_string)
            SIGMA_ARCHIVE.store(f"Cycle complete. Seal: {final_seal}")
            return final_seal
        except Exception as exc:  # pragma: no cover - defensive path
            SIGMA_ARCHIVE.store(f"Cycle error: {exc}")
            return ERROR_SEAL


def _discrete_fourier_transform(values: Iterable[float]) -> list[complex]:
    sequence = [float(value) for value in values]
    length = len(sequence)
    result: list[complex] = []
    if length == 0:
        return result
    factor = -2j * math.pi / length
    for frequency in range(length):
        total = 0j
        for time_index, value in enumerate(sequence):
            total += value * cmath.exp(factor * frequency * time_index)
        result.append(total)
    return result


def _inverse_discrete_fourier_transform(spectrum: Iterable[complex]) -> list[float]:
    spectrum_list = [complex(value) for value in spectrum]
    length = len(spectrum_list)
    result: list[float] = []
    if length == 0:
        return result
    factor = 2j * math.pi / length
    for time_index in range(length):
        total = 0j
        for frequency, value in enumerate(spectrum_list):
            total += value * cmath.exp(factor * frequency * time_index)
        result.append((total / length).real)
    return result


def _percentile(values: Iterable[float], percentile: float) -> float:
    series = sorted(float(value) for value in values)
    if not series:
        return 0.0
    percentile = max(0.0, min(100.0, percentile))
    index = (percentile / 100.0) * (len(series) - 1)
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return series[int(index)]
    lower_value = series[lower]
    upper_value = series[upper]
    weight = index - lower
    return lower_value + (upper_value - lower_value) * weight
