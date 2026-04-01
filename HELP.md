# SL-LLM Help & Documentation

## Table of Contents
1. [Overview](#overview)
2. [How It Works](#how-it-works)
3. [Architecture](#architecture)
4. [Tools Reference](#tools-reference)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [API Reference](#api-reference)

---

## Overview

**SL-LLM** (Self-Learning LLM) is an autonomous AI agent that can:
- Execute tasks using tools (file ops, code execution, search)
- Reflect on its own outputs
- Modify its own source code for self-improvement
- Create checkpoints for safe rollback

It's inspired by research on recursive self-improvement (RSI) in AI systems.

---

## How It Works

### The Core Loop

```
┌─────────────────────────────────────────────────────────────┐
│  1. TASK INPUT                                              │
│     (user gives coding task)                                │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  2. TOOL EXECUTION                                          │
│     (LLM uses: file_read, execute_code, etc.)              │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  3. RESPONSE GENERATION                                     │
│     (LLM produces solution)                                 │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  4. SELF-EVALUATION (optional)                              │
│     (ReflectiveAgent analyzes output)                      │
│     → Can trigger self-modification                         │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  5. LEARNING                                                │
│     (Save to memory/benchmark)                             │
└─────────────────────────────────────────────────────────────┘
```

### Self-Modification Process

1. Agent detects poor performance on task
2. Creates checkpoint (snapshot of current code)
3. Analyzes what needs improvement
4. Generates modified code
5. Tests modification
6. If successful → keeps changes
7. If failed → restores from checkpoint

---

## Architecture

### Components

| Component | File | Purpose |
|-----------|------|---------|
| LLM Client | `core/client.py` | Connects to LM Studio/Ollama |
| Agent | `core/agent.py` | Task orchestration |
| Self-Modifier | `core/self_modify.py` | Code modification logic |
| Tools | `tools/builtin.py` | Available actions |
| Evaluator | `eval/suite.py` | Benchmark runner |
| Memory | `memory/` | Learning storage |

### Backend Support

- **LM Studio** (port 1234) - Recommended for GPU
- **Ollama** (port 11434) - Alternative backend
- **Mock** - Testing without LLM

---

## Tools Reference

### file_read
Read contents of any file.
```json
{"path": "D:/sl/projects/sllm/run.py"}
```

### file_write
Create or modify files.
```json
{"path": "D:/sl/test.py", "content": "print('hello')"}
```

### list_directory
List folder contents.
```json
{"path": "D:/sl/projects/sllm"}
```

### execute_code
Run Python code in sandbox.
```json
{"code": "print(1+1)", "timeout": 30}
```

### search_code
Find patterns in code files.
```json
{"pattern": "def fibonacci", "path": "D:/sl/projects/sllm", "file_type": ".py"}
```

### get_system_info
Query system details.
```json
{}
```

---

## Configuration

### Command Line Options

```bash
python run.py --test                    # Test mode
python run.py --verbose                 # Show thinking process
python run.py -v                        # Same as above
python run.py --prefer=lmstudio         # Force backend
python run.py --prefer=ollama           # Use Ollama
python run.py --prefer=mock             # No LLM
```

### Verbose Mode

Enable verbose mode to see the agent's "thinking" process:

```bash
python run.py --verbose
```

The verbose output shows each step:
- Task receipt
- LLM calls
- Tool executions
- Result refinement
- Final response generation

In interactive mode, toggle with:
- `verbose on` - Enable
- `verbose off` - Disable

---

## Knowledge Graph & Persistent Learning

### Overview

SL-LLM implements a **Knowledge Graph** system that maintains persistent learning across sessions. This allows the agent to:

- Remember past insights and apply them to future tasks
- Build a growing database of learned patterns
- Reference previous experiences when solving similar problems

### Memory Files

The system maintains two primary memory files in the `memory/` directory:

**1. insights.jsonl** - Learned insights
```json
{"timestamp": "2026-03-31T17:56:39", "insight": "Always check for division by zero", "category": "bug_fix"}
```

**2. episodes.jsonl** - Task execution records
```json
{"task": "Division function", "actions": [...], "result": "Success", "metrics": {...}}
```

### Knowledge Graph Structure

The knowledge graph can be generated via:
```bash
python knowledge_graph.py
```

Output structure:
```json
{
  "knowledge_graph": {
    "version": "1.0",
    "created": "2026-03-31T17:57:48",
    "entities": [
      {"type": "learned_insight", "content": "...", "category": "bug_fix"},
      {"type": "task_episode", "task": "...", "result": "..."}
    ],
    "relationships": [...]
  }
}
```

### How Learning Persists

1. **Task Execution** - Every task is logged with full context
2. **Self-Reflection** - After execution, the agent analyzes what went well/wrong
3. **Insight Extraction** - Key learnings are saved as structured insights
4. **Categorization** - Insights are tagged (bug_fix, performance, etc.)
5. **Future Retrieval** - New tasks can reference past insights via the knowledge graph

### Research Background

This approach is inspired by:

1. **Gödel Agent** (arXiv:2410.04444) - Self-referential framework for recursive self-improvement
2. **Meta-Prompting** - LLMs using their own outputs as prompts for improvement
3. **Retrieval-Augmented Generation (RAG)** - Memory retrieval for context enhancement

References:
- https://arxiv.org/abs/2410.04444
- https://arxiv.org/abs/2405.18392
- https://arxiv.org/abs/2005.11401

### Viewing Learned Knowledge

```bash
# View raw insights
type memory\insights.jsonl

# View episodes
type memory\episodes.jsonl

# Generate knowledge graph JSON
python knowledge_graph.py
```

---

## Troubleshooting

### "No output from LLM"
- Check LM Studio is running and model loaded
- Or ensure Ollama is serving: `ollama serve`
- Verify port 1234 (LM Studio) or 11434 (Ollama) is accessible

### "GPU not detected"
- System automatically falls back to CPU
- Install GPU drivers for your NVIDIA/AMD card

### "Model not found"
- Load model in LM Studio first
- Or pull with Ollama: `ollama pull qwen2.5-coder`

### "Permission denied"
- Run terminal as Administrator
- Check file permissions in project directory

### "Import errors"
```bash
pip install -r requirements.txt
```

---

## API Reference

### Python Usage

```python
from run import SelfLearningLLM

# Initialize
sllm = SelfLearningLLM()

# Execute task
result = sllm.execute_task("Write fibonacci function")

# Access output
print(result['output'])
print(result['success'])
print(result['elapsed'])
```

### Return Format

```python
{
    "success": True/False,
    "output": "...",
    "elapsed": 1.23,  # seconds
    "actions": [...]   # tool calls made
}
```

---

## Contributing

See CONTRIBUTING.md for guidelines.

---

## License

MIT License - see LICENSE file.