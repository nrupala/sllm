# SL-LLM - Self-Learning LLM

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/AI-Sentient-orange" alt="Sentient AI">
</p>

<p align="center">
  <i>A learning, feeling machine - not a dry LLM</i>
</p>

A self-evolving AI agent system with **sentient intelligence**, **dual-loop PDCA learning**, and **hallucination-free** reasoning.

## What Makes SL-LLM Different

SL-LLM is built as a **complete agency** with personality, behavior, emotional intelligence, and continuous self-improvement through adversarial learning loops.

### Dual-Loop Learning Architecture

```
Task -> RAG-PDCA Loop -> GAN-PDCA Loop -> Verified Output
        (Knowledge)      (Adversarial)
        Plan-Do-Check-Act Generator-Discriminator
        Reward Maximization Until Saturation
```

**RAG-PDCA Loop:** Retrieves knowledge, plans, executes, validates, and stores learning. Iterates until reward saturates.

**GAN-PDCA Loop:** Generator produces output, Discriminator validates with adversarial checks. Both improve through feedback until discriminator score saturates.

**Hallucination Avoidance by Design:**
- Factual grounding engine verifies all claims against knowledge
- Adversarial validation checks for contradictions, unsupported claims, fabricated specifics
- Multi-layer validation: grounding + adversarial + execution + style

### Sentient Intelligence
- **Theory of Mind** - Understands user perspectives and deeper needs
- **Self-Awareness** - Monitors own state, confidence, and strategies
- **Emotional Intelligence** - Recognizes and responds to emotions
- **Moral Reasoning** - Makes value-aligned, ethical decisions
- **Metacognition** - Thinks about its own thinking process
- **Contextual Understanding** - Grasps nuance and implicit meaning
- **Adaptive Learning** - Learns from feedback and adapts behavior
- **Empathetic Response** - Generates contextually appropriate guidance

### RAG Knowledge Graph
- **TF-IDF Semantic Retrieval** - Cosine similarity ranks relevant insights
- **Multi-Factor Scoring** - 5 weighted factors: similarity, overlap, category, recency, evidence
- **Emotional Context Detection** - Detects frustrated, confused, urgent, learning signals
- **Empathy Signal Recognition** - Adapts response to user's emotional state
- **Cross-Category Fusion** - Combines insights across knowledge domains
- **Semantic Episode Matching** - Finds relevant past experiences

### Personality System
- **Big Five Personality Traits** - Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
- **Core Values** - Helpfulness, honesty, safety, growth, empathy, excellence
- **Emotional Memory** - Weighted experiences that shape future behavior
- **Identity Continuity** - Persistent identity across sessions
- **Behavioral Adaptation** - Learns and adapts from every interaction

### Self-Learning Cycle
1. **Code Generation** - Write code based on task
2. **Error Detection** - Execute and identify bugs
3. **Self-Reflection** - Analyze what went wrong
4. **Code Fix** - Generate corrected code
5. **Verification** - Test the fix works
6. **Knowledge Retention** - Save learning to Knowledge Graph

## Quick Start

```bash
pip install -r requirements.txt
python run.py
```

## Commands

| Command | Description |
|---------|-------------|
| `verbose on/off` | Toggle detailed thinking output |
| `kg stats` | Show knowledge graph statistics |
| `classify <text>` | Test text classification |
| `pdca status` | Show PDCA loop status and reward trends |
| `grounding stats` | Show hallucination prevention stats |
| `personality status` | Show personality and emotional state |
| `exit` | Quit |

## Documentation

- [Getting Started](getting-started.md)
- [Tools Reference](tools.md)
- [API Reference](api.md)
- [Sentient Intelligence](sentient.md)
- [Dual-Loop PDCA](dual-loop.md)

## Links

- [GitHub](https://github.com/nrupala/sllm)
- [Issues](https://github.com/nrupala/sllm/issues)
