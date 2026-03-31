# API Reference

## Python Usage

### Initialize Agent
```python
from run import SelfLearningLLM

sllm = SelfLearningLLM()
```

### Execute Task
```python
result = sllm.execute_task("Write a fibonacci function")

print(result['output'])     # The response
print(result['success'])   # True/False
print(result['elapsed'])   # Time in seconds
```

### Return Format
```python
{
    "success": True,
    "output": "Python code...",
    "elapsed": 1.23,
    "actions": [...]  # Tool calls made
}
```

## CLI Commands

```bash
python run.py              # Interactive mode
python run.py --test       # Test mode
python gui.py              # Web GUI
```

## Configuration

| Environment | Default | Description |
|-------------|---------|-------------|
| SLLLM_MODEL | qwen2.5-coder | Model name |
| SLLLM_BACKEND | auto | lmstudio/ollama/mock |