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
print(result['knowledge_used'])  # Insights retrieved from KG
print(result['classification'])  # Task classification
```

### Return Format
```python
{
    "success": True,
    "output": "Python code...",
    "elapsed": 1.23,
    "knowledge_used": 2,        # Number of KG insights used
    "classification": "general", # Task category
    "actions": [...]            # Tool calls made
}
```

### Self-Learning Cycle
```python
result = sllm.run_self_learning_cycle("Write a sorting function")
# Full cycle: generate -> execute -> reflect -> fix -> verify -> learn
```

## Knowledge Graph API

### Classification
```python
from knowledge_graph_manager import KnowledgeClassifier

result = KnowledgeClassifier.classify("Fix the divide by zero bug")
# Returns: {
#   "primary_category": "bug_fix",
#   "all_categories": {"bug_fix": 3},
#   "contexts": ["programming_language"],
#   "confidence": 0.43
# }
```

### Enhanced Context Retrieval
```python
from knowledge_graph_manager import get_enhanced_context

context, metadata = get_enhanced_context("fix division error in python")
# Returns enriched context with:
# - Emotional understanding header
# - Relevant prior knowledge with relevance scores
# - Task classification and context
```

### Fluid Knowledge Graph
```python
from knowledge_graph_manager import FluidKnowledgeGraph

fkg = FluidKnowledgeGraph()
result = fkg.process("optimize sorting algorithm")
# Full pipeline: classify -> empathize -> contextualize -> retrieve -> format
```

## Sentient Intelligence API

### Sentient Thinking
```python
from core.sentient_thinking import get_sentient_thinking, ThoughtType

sentient = get_sentient_thinking()
sentient.think("User wants to fix a bug", ThoughtType.PERCEPTION)
status = sentient.get_status()
# Returns: emotional_state, confidence, total_thoughts, guidance
```

### Personality System
```python
from core.personality import get_personality

personality = get_personality()
status = personality.get_status()
# Returns: identity, traits, values, emotional_memory, behavioral_adaptation
```

### Agency with Reasoning
```python
from core.agency import get_agency, DecisionType

agency = get_agency()
decision = agency.make_decision(
    context="Fix production bug",
    options=[
        {"name": "quick_fix", "score": 0.6, "pros": ["fast"], "cons": ["risky"]},
        {"name": "proper_fix", "score": 0.8, "pros": ["thorough"], "cons": ["slower"]},
    ],
    decision_type=DecisionType.DELIBERATE
)
print(decision.chosen_option)  # Best option with full reasoning chain
```

## PDCA + Reward System

### Dual-Loop PDCA
```python
from core.dual_loop_pdca import get_dual_loop_system

system = get_dual_loop_system()
result = system.run_task(
    task="Write a prime number function",
    retrieve_fn=lambda t: kg.retrieve(t),
    generate_fn=lambda t, k, p: llm.generate(t, k, p),
    execute_fn=lambda o: execute(o),
    validate_fn=lambda o, e, k: validate(o, e, k),
    store_fn=lambda o, r, b, i: kg.store(o, r, b, i),
)
# Returns: rag_phase, gan_phase, best_output, combined_reward, saturation status
```

### PDCA Engine
```python
from core.pdca_reward import get_pdca_system

pdca = get_pdca_system()
result = pdca.run_cycle(task, execute_fn)
# Full PDCA: Plan -> Do -> Check -> Act with reward maximization
```

### Reward Memory
```python
from core.pdca_reward import RewardMemory

memory = RewardMemory()
memory.record(task, reward=0.85, breakdown={"correctness": 0.9, "efficiency": 0.8})
print(memory.get_trend())      # "improving", "stable", or "declining"
print(memory.get_weakest_dimension())  # Dimension needing improvement
```

## Hallucination Prevention

### Factual Grounding
```python
from core.dual_loop_pdca import FactualGroundingEngine

guard = FactualGroundingEngine()
result = guard.ground_output(output, knowledge, task)
# Returns: grounded (bool), confidence, grounded_claims, ungrounded_claims, hallucination_risk
```

### Adversarial Validation
```python
from core.dual_loop_pdca import HallucinationGuard

validation = HallucinationGuard.adversarial_validate(output, task)
# Returns: valid (bool), strength, flaws found
```

## CLI Commands

```bash
python run.py              # Interactive mode
python run.py --test       # Test mode
python run.py --verbose    # Verbose output
python gui.py              # Web GUI
```

## Configuration

| Environment | Default | Description |
|-------------|---------|-------------|
| SLLLM_MODEL | qwen2.5-coder | Model name |
| SLLLM_BACKEND | auto | lmstudio/ollama/mock |
