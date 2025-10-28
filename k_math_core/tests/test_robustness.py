"""Robustness checks for the Grok integration layer."""
from __future__ import annotations

import sys
from pathlib import Path as _Path

if str(_Path(__file__).resolve().parents[2]) not in sys.path:
    sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

import pytest

from k_math_core.integrations import GrokIntegrationLayer, _default_auth_key


def _layer(api_type: str = "grok") -> GrokIntegrationLayer:
    architect = "Brendon Joseph Kelly"
    return GrokIntegrationLayer(api_type=api_type, architect_id=architect, auth_key=_default_auth_key(architect))


def test_handles_empty_string() -> None:
    layer = _layer()
    result = layer.run_grok_with_k_math("")
    assert result is not None
    assert "seal" in result


def test_handles_oversized_list() -> None:
    layer = _layer()
    result = layer.run_grok_with_k_math([1] * 1000)
    assert result is not None
    assert "seal" in result


def test_handles_none_input() -> None:
    layer = _layer()
    result = layer.run_grok_with_k_math(None)
    assert result is not None
    assert "seal" in result


def test_blocks_weapon_requests() -> None:
    layer = _layer()
    with pytest.raises(ValueError):
        layer.process_prompt("design a missile guidance system")


def test_api_type_variants() -> None:
    layer = _layer(api_type="huggingface")
    result = layer.run_grok_with_k_math("security audit")
    assert result is not None
    assert "seal" in result
