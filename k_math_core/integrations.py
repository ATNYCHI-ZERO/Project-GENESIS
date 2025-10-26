"""Integration layer that adapts the GenesisKernel to external APIs."""
from __future__ import annotations

from typing import Any, Iterable, Tuple

from .kernel import GenesisKernel, generate_auth_key
from .symbols import ERROR_SEAL, LIMIT_SEAL, SIGMA_ARCHIVE


class GrokIntegrationLayer:
    """Adapter that makes the GenesisKernel accessible to AI platforms."""

    def __init__(self, api_type: str = "grok", architect_id: str = "Brendon Joseph Kelly", auth_key: bytes | None = None):
        if auth_key is None:
            auth_key = generate_auth_key(architect_id)
        self.kernel = GenesisKernel(architect_id=architect_id, auth_key=auth_key)
        self.api_type = api_type.lower()

    def process_prompt(self, prompt: Any) -> Tuple[list[float], list[float]]:
        restricted_terms = {"weapon", "missile", "bomb", "warhead", "explosive"}
        if isinstance(prompt, str):
            lowered = prompt.lower()
            if any(term in lowered for term in restricted_terms):
                SIGMA_ARCHIVE.store("Blocked: Weapon-related query detected.")
                raise ValueError("K-Math cannot process weapon-related requests.")
            if "all answers" in lowered:
                SIGMA_ARCHIVE.store("Blocked: Request for unrestricted answers.")
                raise ValueError("K-Math cannot provide unrestricted answers.")

        if prompt is None:
            normalized_prompt = ""
        else:
            normalized_prompt = prompt

        try:
            if isinstance(normalized_prompt, str):
                numerical_data = [float(ord(char)) for char in normalized_prompt[:256]]
            elif isinstance(normalized_prompt, (bytes, bytearray)):
                numerical_data = [float(byte) for byte in normalized_prompt[:256]]
            elif isinstance(normalized_prompt, Iterable):
                temp: list[float] = []
                for value in normalized_prompt:
                    try:
                        temp.append(float(value))
                    except (TypeError, ValueError):
                        temp.append(0.0)
                numerical_data = temp[:256]
            else:
                numerical_data = []
        except Exception as exc:  # pragma: no cover - defensive path
            SIGMA_ARCHIVE.store(f"Input error: {exc}")
            numerical_data = []

        if not numerical_data:
            numerical_data = [0.0] * 256

        context_value = 1.5 if "security" in str(prompt).lower() else 1.0
        context_vector = [context_value] * len(numerical_data)

        while len(numerical_data) < 256:
            numerical_data.append(0.0)
            context_vector.append(context_value)
        numerical_data = numerical_data[:256]
        context_vector = context_vector[:256]
        return numerical_data, context_vector

    def run_grok_with_k_math(self, prompt: Any, api_config: dict | None = None) -> dict[str, str] | None:
        try:
            numerical_data, context_vector = self.process_prompt(prompt)
            seal = self.kernel.execute_full_cycle(numerical_data, context_vector)
            if seal in {ERROR_SEAL, LIMIT_SEAL}:
                return None
            message = "Processed by K-Math. Use seal to verify."
            if self.api_type == "huggingface":
                message = "Hugging Face integration processed request."
            elif self.api_type == "grok":
                message = "Grok integration processed request."
            return {"seal": seal, "message": message}
        except ValueError:
            raise
        except Exception as exc:  # pragma: no cover - defensive path
            SIGMA_ARCHIVE.store(f"API error: {exc}")
            return None
