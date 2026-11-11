# Copyright (c) 2026 Nrupal Akolkar
# SPDX-License-Identifier: MIT
# See LICENSE for the full license text.
"""Compatibility shim: this suite moved to tests/test_rag_retrieval.py.

The checks now live in the pytest suite under tests/. This module
re-exports them so existing imports keep working, and running
``python test_rag_retrieval.py`` still runs the suite, via pytest.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tests.test_rag_retrieval import (
    test_cross_category_fusion,
    test_full_pipeline_with_scoring,
    test_multi_factor_scoring,
    test_retrieval_quality_comparison,
    test_semantic_episode_retrieval,
    test_tfidf_similarity,
)

__all__ = [
    "test_cross_category_fusion",
    "test_full_pipeline_with_scoring",
    "test_multi_factor_scoring",
    "test_retrieval_quality_comparison",
    "test_semantic_episode_retrieval",
    "test_tfidf_similarity",
]

if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([str(Path(__file__).parent / "tests/test_rag_retrieval.py"), "-v"]))
