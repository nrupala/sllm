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

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SLLLM_MODEL` | qwen2.5-coder | Model name |
| `SLLLM_BACKEND` | auto | lmstudio/ollama/mock |
| `SLLLM_TIMEOUT` | 120 | LLM response timeout |

### Command Line Options

```bash
python run.py --test                    # Test mode
python run.py --prefer=lmstudio         # Force backend
python run.py --prefer=ollama           # Use Ollama
python run.py --prefer=mock             # No LLM
python gui.py                           # Start GUI
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