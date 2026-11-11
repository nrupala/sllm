# Copyright (c) 2026 Nrupal Akolkar
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.
"""Compatibility shim: this suite moved to tests/test_sentient_intelligence.py.

The checks now live in the pytest suite under tests/. This module
re-exports them so existing imports keep working, and running
``python test_sentient_intelligence.py`` still runs the suite, via pytest.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tests.test_sentient_intelligence import (
    test_adaptive_learning,
    test_contextual_understanding,
    test_emotional_intelligence,
    test_empathetic_response,
    test_intelligence_benchmark,
    test_metacognition,
    test_moral_reasoning,
    test_self_awareness,
    test_sentient_rag_integration,
    test_theory_of_mind,
)

__all__ = [
    "test_adaptive_learning",
    "test_contextual_understanding",
    "test_emotional_intelligence",
    "test_empathetic_response",
    "test_intelligence_benchmark",
    "test_metacognition",
    "test_moral_reasoning",
    "test_self_awareness",
    "test_sentient_rag_integration",
    "test_theory_of_mind",
]

if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([str(Path(__file__).parent / "tests/test_sentient_intelligence.py"), "-v"]))
