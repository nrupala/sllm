# Copyright (c) 2026 Nrupal Akolkar
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.
"""Compatibility shim: this suite moved to tests/test_tool_suite.py.

The checks now live in the pytest suite under tests/. This module
re-exports them so existing imports keep working, and running
``python test_suite.py`` still runs the suite, via pytest.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tests.test_tool_suite import (
    test_1_basic_tool_execution,
    test_2_reflection_capability,
    test_3_self_modification_engine,
    test_4_memory_and_learning,
    test_5_version_control,
    test_6_evaluation_benchmark,
    test_7_gpu_detection,
    test_8_agent_integration,
    test_9_self_improvement_cycle,
)

__all__ = [
    "test_1_basic_tool_execution",
    "test_2_reflection_capability",
    "test_3_self_modification_engine",
    "test_4_memory_and_learning",
    "test_5_version_control",
    "test_6_evaluation_benchmark",
    "test_7_gpu_detection",
    "test_8_agent_integration",
    "test_9_self_improvement_cycle",
]

if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([str(Path(__file__).parent / "tests/test_tool_suite.py"), "-v"]))
