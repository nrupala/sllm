"""Make the repository root importable for the test modules.

These suites began as root-level scripts that import the project
packages (core, tools, eval, knowledge_graph_manager, ...) from the
repository root. Now that the modules live in tests/, put the root
back on sys.path so the same imports keep working no matter where
pytest is invoked from.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
