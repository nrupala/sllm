# Copyright (c) 2026 Nrupal Akolkar
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.
"""Compatibility shim: this suite moved to tests/test_rigorous_self_learning.py.

The checks now live in the pytest suite under tests/. This module
re-exports them so existing imports keep working, and running
``python rigorous_self_learning_test.py`` still runs the suite, via pytest.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tests.test_rigorous_self_learning import (
    BASE,
    RESULTS,
    log_step,
    run_test,
    save_results,
)

__all__ = [
    "BASE",
    "RESULTS",
    "log_step",
    "run_test",
    "save_results",
]

if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([str(Path(__file__).parent / "tests/test_rigorous_self_learning.py"), "-v"]))
