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

# With verbose mode
python run.py --verbose
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

## Interactive Commands

| Command | Description |
|---------|-------------|
| `verbose on/off` | Toggle detailed thinking output showing reasoning, agency decisions, knowledge retrieval |
| `kg stats` | Show knowledge graph statistics (categories, insight counts) |
| `classify <text>` | Test how the system classifies a text input |
| `pdca status` | Show PDCA loop status, reward trends, and improvement metrics |
| `grounding stats` | Show hallucination prevention statistics |
| `personality status` | Show personality traits, emotional state, and behavioral adaptation |
| `exit` | Quit the interactive session |

## Options

| Flag | Description |
|------|-------------|
| `--test` | Run test and exit |
| `--prefer=lmstudio` | Use LM Studio backend |
| `--prefer=ollama` | Use Ollama backend |
| `--prefer=mock` | Testing only |
| `--verbose` | Enable verbose output |

## Understanding the Output

When you submit a task, SL-LLM processes it through:

1. **Sentient Thinking** - Detects emotional context and user needs
2. **Reasoning Engine** - Generates lateral perspectives and first-principles breakdown
3. **Agency Decision** - Selects the best approach strategy
4. **Knowledge Graph RAG** - Retrieves relevant past learnings
5. **LLM Generation** - Produces response with full context
6. **PDCA Loop** (optional) - Iterates to maximize reward until saturation

## Testing

```bash
# Run comprehensive test suite
python test_suite.py

# Run sentient intelligence tests
python test_sentient_intelligence.py

# Run RAG retrieval tests
python test_rag_retrieval.py
```
