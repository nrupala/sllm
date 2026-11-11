# Copyright (c) 2026 Nrupal Akolkar
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.
"""Compatibility shim: this suite moved to tests/test_phase123.py.

The checks now live in the pytest suite under tests/. This module
re-exports them so existing imports keep working, and running
``python test_phase123.py`` still runs the suite, via pytest.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tests.test_phase123 import (
    test_full_integration,
    test_phase1_cross_instance_sync,
    test_phase1_persistent_memory,
    test_phase1_strategic_planning,
    test_phase2_hallucination_prevention,
    test_phase2_parallel_execution,
    test_phase2_web_access,
    test_phase3_scalability,
    test_phase3_security,
    test_phase3_verification,
)

__all__ = [
    "test_full_integration",
    "test_phase1_cross_instance_sync",
    "test_phase1_persistent_memory",
    "test_phase1_strategic_planning",
    "test_phase2_hallucination_prevention",
    "test_phase2_parallel_execution",
    "test_phase2_web_access",
    "test_phase3_scalability",
    "test_phase3_security",
    "test_phase3_verification",
]

if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([str(Path(__file__).parent / "tests/test_phase123.py"), "-v"]))
