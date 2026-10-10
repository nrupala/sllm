# SL-LLM Help & Documentation

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [How It Works](#how-it-works)
3. [Available Models](#available-models)
4. [Tools Reference](#tools-reference)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [API Reference](#api-reference)

---

## Quick Start

| Command | Description |
|---------|-------------|
| `python run_local.py` | Start local CLI runner |
| `python gui_prod.py` | Start production GUI |
| `python gui.py` | Start basic GUI |
| `python daemon.py` | Start API server |

### Default Ports
- **GUI:** http://localhost:8080
- **LM Studio API:** http://localhost:1234
- **Ollama API:** http://localhost:11434
- **MCP Gateway:** http://localhost:5000/mcp

---

## How It Works

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Task Input │ -> │ Tool Execute │ -> │   Response   │
└──────────────┘    └──────────────┘    └──────────────┘
                           │
                           v
                    ┌──────────────┐
                    │ Self-Reflect │
                    └──────────────┘
                           │
                           v
                    ┌──────────────┐
                    │   Learning   │
                    └──────────────┘
```

### Self-Modification Process
1. Agent detects poor performance → Creates checkpoint
2. Analyzes what needs improvement → Generates modified code
3. Tests modification → If successful keeps, else restores

---

## Available Models

### Local Models (No API Key)
| Model | Provider | Description |
|-------|----------|-------------|
| qwen2.5-coder:14b | LM Studio | Code generation |
| qwen3.5:9b | Ollama | General purpose |
| llama3.1:8b | Ollama | General purpose |

### Cloud Providers (Require API Key)
- OpenAI (GPT-5, GPT-4o)
- Anthropic (Claude 4)
- Google (Gemini 2.5)
- DeepSeek (R1, V3)
- Qwen (Alibaba)

---

## Tools Reference

| Tool | Usage |
|------|-------|
| `file_read` | `{"path": "D:/sl/projects/sllm/run.py"}` |
| `file_write` | `{"path": "D:/sl/test.py", "content": "print('hello')"}` |
| `list_directory` | `{"path": "D:/sl/projects/sllm"}` |
| `execute_code` | `{"code": "print(1+1)", "timeout": 30}` |
| `search_code` | `{"pattern": "def fibonacci", "path": "D:/sl", "file_type": ".py"}` |
| `get_system_info` | `{}` |

---

## Configuration

### Command Line Options
```bash
python run_local.py --test              # Test mode
python run_local.py --verbose            # Show thinking
python run_local.py --prefer=lmstudio   # Force LM Studio
python run_local.py --prefer=ollama       # Use Ollama
python run_local.py --prefer=mock        # Mock backend
```

### Environment Variables
- `LMSTUDIO_URL` - LM Studio API URL
- `OLLAMA_URL` - Ollama API URL

---

## Troubleshooting

### ❌ "No output from LLM"

**Fix:** Ensure LM Studio is running with a model loaded
1. Open LM Studio → Download model → Load model → Start Server
2. Verify: http://localhost:1234/v1/models

### ❌ Ollama not working

**Fix:**
```bash
ollama serve
ollama pull qwen2.5-coder
python run_local.py --prefer=ollama
```

### ❌ GPU not detected
- Auto-fallback to CPU
- Install NVIDIA drivers for GPU acceleration

### ❌ "Model not found"
- Load model in LM Studio first
- Or: `ollama pull qwen2.5-coder`

---

## API Reference

### Python Usage
```python
from run_local import run_task

result = run_task("Write fibonacci function")
print(result['output'])
print(result['success'])
```

### Return Format
```python
{
    "success": True,
    "output": "...",
    "elapsed": 1.23,
    "actions": [...]
}
```

### REST Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Chat with LLM |
| `/api/code` | POST | Generate code |
| `/api/models` | GET | List models |
| `/api/status` | GET | System status |
| `/mcp/tools` | GET | MCP tools list |
| `/mcp/execute` | POST | Execute MCP tool |

---

## Knowledge Graph

SL-LLM maintains persistent learning via:
- `memory/insights.jsonl` - Learned insights
- `memory/episodes.jsonl` - Task records

Generate knowledge graph:
```bash
python knowledge_graph.py
```

---

## Architecture

| Component | File | Purpose |
|-----------|------|---------|
| LLM Client | `core/client.py` | Connect to LM Studio/Ollama |
| Agent | `core/sl_llm_agent.py` | Task orchestration |
| Tools | `tools/builtin.py` | Available actions |
| Memory | `memory/` | Learning storage |
| Zero-Check | `core/zero_check.py` | Division safety |
| MCP Gateway | `mcp_gateway.py` | External tools |

---

*See CONTRIBUTING.md for contribution guidelines.*
*MIT License - see LICENSE file.*