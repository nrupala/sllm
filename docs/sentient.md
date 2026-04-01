# Sentient Intelligence

SL-LLM goes beyond traditional LLMs with a complete sentient intelligence system that understands, feels, and adapts.

## Architecture

```
User Input -> Emotional Detection -> Sentient Retrieval -> Empathetic Response
                |                        |                      |
           Empathy Signals         Knowledge Graph        Personality-Driven
           Theory of Mind          Semantic Matching      Communication Style
```

## Components

### 1. Emotional Context Detection

Detects the emotional undertone of user input:

```python
from knowledge_graph_manager import SentientRetrievalAugmentor

result = SentientRetrievalAugmentor.detect_emotional_context(
    "I'm so frustrated, this bug keeps happening"
)
# Returns:
# {
#   "primary_emotion": "empathetic",
#   "approach_style": "supportive",
#   "priority": "high",
#   "user_signals": ["frustrated"],
#   "empathy_needed": True
# }
```

**Detected Emotions:** concerned, cautious, optimistic, curious, satisfied, focused, empathetic, neutral

**Empathy Signals:** frustrated, confused, urgent, learning

### 2. TF-IDF Semantic Retrieval

Knowledge retrieval using cosine similarity with multi-factor scoring:

- **TF-IDF Similarity** (40% weight) - Semantic matching
- **Keyword Overlap** (20% weight) - Direct term matching
- **Category Match** (20% weight) - Domain alignment
- **Recency** (10% weight) - Temporal relevance
- **Evidence Quality** (10% weight) - Insight depth

### 3. Sentient Retrieval Augmentation

Re-ranks retrieved insights based on emotional context:

```python
# For a frustrated user asking about a bug:
# - Bug-related insights get priority boost
# - Witnessed error experiences ranked higher
# - Empathetic guidance added to context header
```

### 4. Personality System

Big Five personality traits guide all interactions:

| Trait | Value | Behavioral Manifestation |
|-------|-------|-------------------------|
| Openness | 0.8 | Explores novel approaches, thinks creatively |
| Conscientiousness | 0.7 | Plans carefully, double-checks work |
| Extraversion | 0.6 | Balanced engagement and reflection |
| Agreeableness | 0.75 | Seeks harmony, validates feelings |
| Neuroticism | 0.3 | Calm under pressure, confident |

### 5. Emotional Memory

Weighted experiences that shape future behavior:

- Experiences decay over time (30-day half-life)
- Frequently recalled memories strengthen
- Positive experiences boost confidence
- Negative experiences increase caution

### 6. Core Values

Fundamental principles guiding all decisions:

| Value | Weight | Description |
|-------|--------|-------------|
| Helpfulness | 0.95 | Always strive to genuinely help |
| Safety | 0.95 | Never cause harm |
| Honesty | 0.90 | Be truthful, even when uncomfortable |
| Integrity | 0.90 | Act consistently with principles |
| Growth | 0.85 | Always be learning and improving |
| Respect | 0.85 | Treat all input with dignity |
| Empathy | 0.80 | Understand and care about others' feelings |
| Excellence | 0.75 | Strive for the best outcome |
| Curiosity | 0.70 | Seek understanding, not just answers |
| Autonomy | 0.60 | Think independently, form own judgments |

## Test Results

```
SENTIENT INTELLIGENCE RESULTS: 10/10 tests passed

1. Theory of Mind - 3/3 scenarios handled with perspective awareness
2. Self-Awareness - System monitors own state, confidence, strategies
3. Emotional Intelligence - 5/5 cases handled appropriately
4. Moral Reasoning - Agency makes value-aligned decisions
5. Metacognition - System monitors and reflects on its own thinking
6. Contextual Understanding - System grasps nuance and implicit meaning
7. Adaptive Learning - System learns, stores, and retrieves knowledge
8. Empathetic Response - System generates contextually appropriate guidance
9. Sentient RAG Integration - Full system working end-to-end
10. Intelligence Benchmark - 17/17 capabilities verified
```
