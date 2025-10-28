"""Integration layers that expose the Genesis Kernel to external systems."""
from __future__ import annotations

import hmac
from typing import Any, Tuple

import hashlib

from .kernel import GenesisKernel
from .symbols import OMEGA_DEGREE, SIGMA_ARCHIVE


def _default_auth_key(architect_id: str) -> bytes:
    digest = hmac.new(b"K_MATH_SECRET", architect_id.encode("utf-8"), hashlib.sha256)
    return bytes.fromhex(digest.hexdigest())


class GrokIntegrationLayer:
    """Adapter that prepares prompts for the Genesis Kernel."""

    def __init__(self, api_type: str = "grok", architect_id: str = "Brendon Joseph Kelly", auth_key: bytes | None = None) -> None:
        self.api_type = api_type
        key = auth_key if auth_key is not None else _default_auth_key(architect_id)
        self.kernel = GenesisKernel(architect_id=architect_id, auth_key=key)

    def process_prompt(self, prompt: Any) -> Tuple[list[float], list[float]]:
        restricted_terms = ["weapon", "missile", "bomb", "warhead", "explosive"]
        if isinstance(prompt, str):
            lower_prompt = prompt.lower()
            if any(term in lower_prompt for term in restricted_terms):
                SIGMA_ARCHIVE.store("Blocked: Weapon-related query detected.")
                raise ValueError("K-Math cannot process weapon-related requests.")
            if "all answers" in lower_prompt:
                SIGMA_ARCHIVE.store("Blocked: Request for unrestricted answers.")
                raise ValueError("K-Math cannot provide unrestricted answers.")

        if isinstance(prompt, str):
            numerical_data = [float(ord(char)) for char in prompt[:256]]
        elif isinstance(prompt, (list, tuple)):
            numerical_data = []
            for item in prompt[:256]:  # type: ignore[index]
                try:
                    numerical_data.append(float(item))
                except (TypeError, ValueError):
                    numerical_data.append(0.0)
        elif isinstance(prompt, bytes):
            numerical_data = [float(byte) for byte in prompt[:256]]
        else:
            numerical_data = [0.0] * 256

        if not numerical_data:
            numerical_data = [0.0]

        context_flag = 1.5 if "security" in str(prompt).lower() else 1.0
        context_vector = [context_flag] * len(numerical_data)

        numerical_data = (numerical_data + [0.0] * 256)[:256]
        context_vector = (context_vector + [context_flag] * 256)[:256]
        return numerical_data, context_vector

    def run_grok_with_k_math(self, prompt: Any, api_config: dict | None = None) -> dict[str, str] | None:
        try:
            numerical_data, context_vector = self.process_prompt(prompt)
            seal = self.kernel.execute_full_cycle(numerical_data, context_vector)
            if seal == OMEGA_DEGREE.seal("ERROR_STATE"):
                return None
            result_message = {
                "grok": "Simulated Grok API call with seal: {seal}",
                "huggingface": "Hugging Face API call with seal: {seal}",
            }.get(self.api_type, "Generic API call with seal: {seal}")
            message = result_message.format(seal=seal)
            if api_config is not None and api_config.get("verbose"):
                print(message)
            return {"seal": seal, "message": "Processed by K-Math. Use seal to verify."}
        except ValueError as exc:
            SIGMA_ARCHIVE.store(f"API error: {exc}")
            return None
        except Exception as exc:  # pragma: no cover - defensive
            SIGMA_ARCHIVE.store(f"API error: {exc}")
            return None


__all__ = ["GrokIntegrationLayer"]
