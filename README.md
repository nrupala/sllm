# Self-Learning LLM (SL-LLM)

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/AI-Self%20Improving-orange" alt="AI">
</p>

A self-evolving AI agent system that can recursively improve its own code through reflection and modification. Built on top of local LLMs (Qwen2.5-coder, CodeLlama, etc.) via LM Studio or Ollama.

## 🚀 What is SL-LLM?

SL-LLM is an autonomous agent framework that combines:
- **Local LLM Integration** - Runs entirely offline using your own GPU
- **Tool Execution** - File operations, code execution, search capabilities  
- **Self-Reflection** - Analyzes its own outputs for improvement
- **Code Modification** - Can modify its own source code when needed
- **Checkpoint System** - Safe rollback on failures

Think of it as an AI that doesn't just answer questions - it can improve itself.

## 🎯 Capabilities

### Core Features
- **Task Execution** - Complete coding tasks using available tools
- **Self-Evaluation** - Reflect on outputs and identify improvements
- **Code Modification** - Rewrite its own Python modules
- **Version Control** - Create snapshots before changes, restore on failure
- **GPU Acceleration** - Runs on NVIDIA/AMD GPUs via LM Studio

### Available Tools
| Tool | Description |
|------|-------------|
| `file_read` | Read any file from filesystem |
| `file_write` | Create/modify files |
| `list_directory` | Browse directory contents |
| `execute_code` | Run Python in sandbox |
| `search_code` | Pattern search in code files |
| `get_system_info` | Query hardware/OS info |

### Self-Improvement Loop
```
Task → Execute → Evaluate → Modify → Verify → Learn
```

## 📋 Requirements

- **Python 3.8+**
- **GPU** (recommended) or CPU fallback
- **LM Studio** or **Ollama** running locally
- A local LLM model loaded (qwen2.5-coder recommended)

## 🔧 Installation

```bash
# Clone the repository
git clone <repo-url>
cd sllm

# Install dependencies
pip install -r requirements.txt
```

## 🚦 Quick Start

### 1. Start your LLM server
**Option A: LM Studio**
- Open LM Studio
- Load `qwen2.5-coder` (7B recommended)
- Start server at localhost:1234

**Option B: Ollama**
```bash
ollama pull qwen2.5-coder
ollama serve
```

### 2. Run SL-LLM

```bash
# Interactive mode
python run.py

# Test a specific task
python run.py --test
```

### 3. Or start the GUI
```bash
python gui.py
# Open http://localhost:8080
```

## 💻 Usage Examples

### CLI Interaction
```
>> Write a quicksort function
[Returns Python quicksort implementation]

>> Improve that code to be more memory efficient
[Self-analyzes and suggests improvements]
```

### Python API
```python
from run import SelfLearningLLM

sllm = SelfLearningLLM()
result = sllm.execute_task("Write a binary search")
print(result['output'])
```

## ⚙️ Configuration

| Flag | Description |
|------|-------------|
| `--test` | Run test query and exit |
| `--prefer=lmstudio` | Use LM Studio backend |
| `--prefer=ollama` | Use Ollama backend |
| `--prefer=mock` | No LLM (testing only) |

## 🛡️ Safety Features

- **Path Validation** - Only modifies files within project directory
- **Checkpoints** - Auto-snapshot before any self-modification
- **Sandbox Execution** - Code runs in isolated temp files
- **Iteration Limits** - Prevents infinite self-improvement loops

## 📁 Project Structure

```
sllm/
├── core/           # LLM client & agent logic
│   ├── agent.py    # Core agent implementation
│   ├── client.py   # Multi-backend LLM client
│   └── self_modify.py  # Self-modification logic
├── tools/          # Tool definitions
│   └── builtin.py  # Built-in tools (file, exec, etc.)
├── eval/           # Evaluation & benchmarks
├── memory/         # Learning storage
├── sandbox/        # Safe code execution
├── run.py          # Main CLI entry
├── gui.py          # Web GUI
├── HELP.md         # Full documentation
└── README.md       # This file
```

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 License

MIT License - see [LICENSE](LICENSE).

## 🔗 Links

- [Documentation](HELP.md)
- [Issues](https://github.com/<repo>/issues)
- [Discussions](https://github.com/<repo>/discussions)