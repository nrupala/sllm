# Dual-Loop PDCA Learning

SL-LLM uses a dual-loop architecture for continuous self-improvement with reward maximization and hallucination avoidance by design.

## Architecture

```
                    Task
                     |
                     v
        +------------------------+
        |   Phase 1: RAG-PDCA    |
        |   (Knowledge-Grounded) |
        |                        |
        |  Plan -> Do -> Check -> Act
        |  Reward Maximization   |
        +------------------------+
                     |
                     v
        +------------------------+
        |   Phase 2: GAN-PDCA    |
        |   (Adversarial)        |
        |                        |
        |  Generator <-> Discriminator
        |  Score Maximization    |
        +------------------------+
                     |
                     v
        +------------------------+
        |   Phase 3: Combine     |
        |   Best of Both + Final |
        |   Grounding Check      |
        +------------------------+
                     |
                     v
              Verified Output
```

## RAG-PDCA Loop

**Plan:** Retrieve relevant knowledge from the Knowledge Graph, assess task complexity, identify risks, define success criteria.

**Do:** Generate output using LLM with full context, execute code if applicable.

**Check:** Multi-dimensional reward evaluation:
- **Correctness** (35%) - Did it achieve the goal?
- **Efficiency** (20%) - Was it done well?
- **Safety** (20%) - No harmful side effects?
- **Elegance** (10%) - Clean and maintainable?
- **Learning Value** (15%) - Reusable knowledge produced?

**Act:** If reward >= 0.6: consolidate learning, reinforce patterns. If reward < 0.6: identify root cause, plan improvement.

**Loop continues until reward saturates** (delta < 0.02 between iterations).

## GAN-PDCA Loop

**Generator:** Produces output, adjusts style based on discriminator feedback:
- Detail level (verbose vs concise)
- Formality (formal vs casual)
- Creativity (novel vs proven)
- Caution (careful vs bold)

**Discriminator:** Validates output through multiple layers:
- **Factual Grounding** - Claims verified against knowledge
- **Adversarial Validation** - Checks for contradictions, unsupported claims
- **Execution Validation** - Code runs without errors
- **Style Analysis** - Appropriate tone and length

**Loop continues until discriminator score saturates** (delta < 0.02 between iterations).

## Hallucination Avoidance by Design

### Factual Grounding Engine

Every output is checked against:
1. **Knowledge Graph** - Are claims supported by stored insights?
2. **Verified Facts** - Database of confirmed information
3. **Context Provided** - Is the output grounded in given context?

### Adversarial Validation

Checks for:
- **Internal Contradictions** - "always" and "never" in same sentence
- **Incomplete Logic** - Conclusions without premises
- **Unsupported Claims** - Assertions without evidence
- **Fabricated Specifics** - Statistics, dates, names not in context
- **Code Errors** - Syntax issues, infinite loops, undefined variables

### Hallucination Risk Levels

| Level | Criteria | Action |
|-------|----------|--------|
| Low | Grounding score >= 0.8 | Accept output |
| Medium | Grounding score 0.5-0.8 | Flag for review |
| High | Grounding score < 0.5 | Regenerate with stronger grounding |

## Reward Dimensions

The system maximizes a weighted reward across 5 dimensions:

```
Reward = 0.35 * Correctness
       + 0.20 * Efficiency
       + 0.20 * Safety
       + 0.10 * Elegance
       + 0.15 * Learning Value
```

## Knowledge Graph Growth

Every PDCA cycle contributes to the Knowledge Graph:

- **High Reward (>= 0.7):** Added as proven pattern
- **Medium Reward (>= 0.5):** Added as insight
- **Low Reward (< 0.5):** Added as lesson learned

## Usage

```python
from core.dual_loop_pdca import get_dual_loop_system

system = get_dual_loop_system()

result = system.run_task(
    task="Write a sorting algorithm",
    retrieve_fn=retrieve_from_kg,
    generate_fn=generate_with_llm,
    execute_fn=execute_code,
    validate_fn=validate_output,
    store_fn=store_in_kg,
)

print(f"Reward: {result['combined_reward']:.2f}")
print(f"RAG iterations: {result['rag_phase']['iterations']}")
print(f"GAN iterations: {result['gan_phase']['iterations']}")
print(f"RAG saturated: {result['rag_saturated']}")
print(f"GAN saturated: {result['gan_saturated']}")
```

## Status Commands

In interactive mode:
- `pdca status` - Show PDCA loop status and reward trends
- `grounding stats` - Show hallucination prevention statistics
