# Getting Started

## Requirements

- Python 3.8+
- LM Studio or Ollama
- GPU (recommended)

## Installation

```bash
git clone https://github.com/nrupala/sllm.git
cd sllm
pip install -r requirements.txt
```

## Running

```bash
# Interactive CLI
python run.py

# Or start GUI
python gui.py
```

## Backend Setup

### LM Studio (Recommended)
1. Open LM Studio
2. Load `qwen2.5-coder` model
3. Start server at localhost:1234

### Ollama
```bash
ollama pull qwen2.5-coder
ollama serve
```

## Options

| Flag | Description |
|------|-------------|
| `--test` | Run test and exit |
| `--prefer=lmstudio` | Use LM Studio |
| `--prefer=ollama` | Use Ollama |
| `--prefer=mock` | Testing only |