# SL-LLM - Self-Learning LLM

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
</p>

A self-evolving AI agent system with recursive self-improvement capabilities.

## Features

- **Self-Learning** - Can improve its own code through reflection
- **GPU Acceleration** - Runs on NVIDIA/AMD GPUs via LM Studio
- **Tool Execution** - File ops, code execution, search capabilities
- **Knowledge Graph** - Persistent learning across sessions
- **Offline** - Runs entirely locally
- **Web GUI** - Browser-based control panel

## Self-Learning Demonstration

SL-LLM demonstrates true self-learning through:

1. **Code Generation** - Write code based on task
2. **Error Detection** - Execute and identify bugs
3. **Self-Reflection** - Analyze what went wrong
4. **Code Fix** - Generate corrected code
5. **Verification** - Test the fix works
6. **Knowledge Retention** - Save learning to Knowledge Graph

See [test_run_samples/knowledge_graph.json](../test_run_samples/knowledge_graph.json) for proof of persistent learning.

## Quick Start

```bash
pip install -r requirements.txt
python run.py
```

## Documentation

- [Getting Started](getting-started.md)
- [Tools Reference](tools.md)
- [API Reference](api.md)

## Links

- [GitHub](https://github.com/nrupala/sllm)
- [Issues](https://github.com/nrupala/sllm/issues)