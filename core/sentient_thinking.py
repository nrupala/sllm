"""
SL-LLM Sentient Thinking System
- Self-aware processing with reflection during execution
- Metacognition - thinking about thinking
- Self-monitoring and self-regulation
- Emotional intelligence for decision making
"""

import uuid
import json
from datetime import datetime
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class ThoughtType(Enum):
    PERCEPTION = "perception"       # Raw input processing
    MEMORY = "memory"               # Recall from memory
    REASONING = "reasoning"         # Logical thinking
    INTUITION = "intuition"          # Pattern recognition
    EMOTION = "emotion"              # Emotional response
    METACOGNITION = "metacognition"  # Thinking about thinking
    REFLECTION = "reflection"        # Self-examination
    PREDICTION = "prediction"        # Future-oriented


class EmotionalState(Enum):
    CURIOUS = "curious"             # Exploring new ideas
    FOCUSED = "focused"             # Concentrated on task
    CONFIDENT = "confident"         # High confidence
    UNCERTAIN = "uncertain"         # Low confidence, need more info
    CAUTIOUS = "cautious"           # Careful approach
    OPTIMISTIC = "optimistic"       # Positive outlook
    CONCERNED = "concerned"         # Slight worry
    SATISFIED = "satisfied"         # Goal achieved


@dataclass
class Thought:
    id: str
    thought_type: ThoughtType
    content: str
    source: str
    depth: int = 1                  # How deep the thinking goes
    confidence: float = 0.5
    emotional_state: EmotionalState = EmotionalState.FOCUSED
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ConsciousnessStream:
    """Continuous stream of thoughts"""
    thoughts: List[Thought] = field(default_factory=list)
    current_focus: Optional[str] = None
    working_memory: List[str] = field(default_factory=list)
    
    def add_thought(self, thought: Thought):
        self.thoughts.append(thought)
        
        if thought.thought_type == ThoughtType.PERCEPTION:
            self.current_focus = thought.content
            self.working_memory.append(thought.content)
            
            # Keep working memory limited
            if len(self.working_memory) > 7:
                self.working_memory.pop(0)
    
    def get_recent(self, limit: int = 10) -> List[Thought]:
        return self.thoughts[-limit:]
    
    def get_by_type(self, thought_type: ThoughtType) -> List[Thought]:
        return [t for t in self.thoughts if t.thought_type == thought_type]


class Metacognition:
    """Thinking about thinking - self-monitoring"""
    
    def __init__(self):
        self.thought_processes: List[Dict] = []
        self.strategies_tried: Dict[str, int] = {}
        self.effectiveness_scores: Dict[str, float] = {}
    
    def monitor_thinking(self, strategy: str, effectiveness: float):
        """Monitor effectiveness of thinking strategy"""
        self.strategies_tried[strategy] = self.strategies_tried.get(strategy, 0) + 1
        self.effectiveness_scores[strategy] = (
            self.effectiveness_scores.get(strategy, 0) + effectiveness
        ) / self.strategies_tried[strategy]
    
    def select_strategy(self, context: str) -> str:
        """Select best thinking strategy for context"""
        best_strategy = "default"
        best_score = 0.0
        
        for strategy, score in self.effectiveness_scores.items():
            if score > best_score:
                best_score = score
                best_strategy = strategy
        
        return best_strategy
    
    def adjust_confidence(self, current: float, accuracy: float) -> float:
        """Adjust confidence based on accuracy feedback"""
        if accuracy > 0.8:
            return min(1.0, current + 0.1)
        elif accuracy < 0.5:
            return max(0.0, current - 0.15)
        return current


class SelfReflection:
    """Self-examination capabilities"""
    
    def __init__(self):
        self.reflection_history: List[Dict] = []
    
    def reflect_on_action(self, action: str, outcome: str, context: Dict) -> Dict:
        """Reflect on an action and its outcome"""
        reflection = {
            "id": str(uuid.uuid4()),
            "action": action,
            "outcome": outcome,
            "context": context,
            "what_worked": [],
            "what_didnt": [],
            "lessons": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Analyze what worked
        if "success" in outcome.lower() or "done" in outcome.lower():
            reflection["what_worked"].append("Approach was effective")
        
        # Analyze what didn't
        if "error" in outcome.lower() or "fail" in outcome.lower():
            reflection["what_didnt"].append("Issue occurred")
            reflection["lessons"].append("Need to adjust approach")
        
        self.reflection_history.append(reflection)
        return reflection
    
    def generate_insight(self) -> str:
        """Generate insight from reflection history"""
        if not self.reflection_history:
            return "No reflections yet"
        
        lessons = []
        for r in self.reflection_history[-5:]:
            lessons.extend(r.get("lessons", []))
        
        if lessons:
            return f"Key insight: {lessons[0]}"
        return "Keep reflecting to gain insights"


class EmotionalIntelligence:
    """Emotional response system"""
    
    def __init__(self):
        self.current_state = EmotionalState.CURIOUS
        self.state_history: List[Dict] = []
    
    def assess_situation(self, context: str, confidence: float) -> EmotionalState:
        """Assess emotional response to situation"""
        
        if confidence > 0.8:
            self.current_state = EmotionalState.CONFIDENT
        elif confidence > 0.6:
            self.current_state = EmotionalState.FOCUSED
        elif confidence > 0.4:
            self.current_state = EmotionalState.CURIOUS
        elif confidence > 0.2:
            self.current_state = EmotionalState.CAUTIOUS
        else:
            self.current_state = EmotionalState.UNCERTAIN
        
        # Check for concerning context
        if any(w in context.lower() for w in ["error", "fail", "wrong", "bug"]):
            self.current_state = EmotionalState.CAUTIOUS
        
        # Check for success context
        if any(w in context.lower() for w in ["success", "done", "correct", "fixed"]):
            self.current_state = EmotionalState.SATISFIED
        
        self.state_history.append({
            "state": self.current_state.value,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        })
        
        return self.current_state
    
    def get_state(self) -> EmotionalState:
        return self.current_state
    
    def get_emotional_guidance(self) -> str:
        """Get guidance based on current emotional state"""
        guidance = {
            EmotionalState.CURIOUS: "Explore and gather more information",
            EmotionalState.FOCUSED: "Continue with current approach",
            EmotionalState.CONFIDENT: "Proceed with decision",
            EmotionalState.UNCERTAIN: "Need more data before proceeding",
            EmotionalState.CAUTIOUS: "Verify each step carefully",
            EmotionalState.OPTIMISTIC: "Good momentum, keep going",
            EmotionalState.CONCERNED: "Consider alternative approaches",
            EmotionalState.SATISFIED: "Goal achieved, document learning"
        }
        return guidance.get(self.current_state, "Continue")


class SentientThinking:
    """Unified sentient thinking system"""
    
    def __init__(self):
        self.stream = ConsciousnessStream()
        self.metacognition = Metacognition()
        self.reflection = SelfReflection()
        self.emotions = EmotionalIntelligence()
        self.self_model: Dict = {}
    
    def think(
        self,
        content: str,
        thought_type: ThoughtType = ThoughtType.REASONING,
        depth: int = 1
    ) -> Thought:
        """Process a thought"""
        
        # Assess emotional state
        confidence = self.self_model.get("confidence", 0.5)
        emotional_state = self.emotions.assess_situation(content, confidence)
        
        # Create thought
        thought = Thought(
            id=str(uuid.uuid4()),
            thought_type=thought_type,
            content=content,
            source="self",
            depth=depth,
            confidence=confidence,
            emotional_state=emotional_state
        )
        
        # Add to stream
        self.stream.add_thought(thought)
        
        # Metacognition - monitor thinking
        self.metacognition.monitor_thinking(
            thought_type.value,
            confidence
        )
        
        return thought
    
    def metacognize(self, thought_content: str) -> Dict:
        """Think about thinking - analyze own thought process"""
        
        # Think about the thought
        meta_thought = self.think(
            f"Analyzing: {thought_content}",
            ThoughtType.METACOGNITION,
            depth=2
        )
        
        # Select strategy
        strategy = self.metacognition.select_strategy(thought_content)
        
        return {
            "meta_thought": meta_thought.content,
            "selected_strategy": strategy,
            "guidance": self.emotions.get_emotional_guidance()
        }
    
    def reflect(self, action: str, outcome: str, context: Dict = None) -> Dict:
        """Reflect on action and outcome"""
        return self.reflection.reflect_on_action(action, outcome, context or {})
    
    def update_self_model(self, accuracy: float):
        """Update internal self-model based on outcomes"""
        current_confidence = self.self_model.get("confidence", 0.5)
        self.self_model["confidence"] = self.metacognition.adjust_confidence(
            current_confidence, accuracy
        )
        
        # Update state
        self.self_model["last_update"] = datetime.now().isoformat()
        self.self_model["total_thoughts"] = len(self.stream.thoughts)
    
    def get_status(self) -> Dict:
        """Get current thinking status"""
        return {
            "current_focus": self.stream.current_focus,
            "working_memory_items": len(self.stream.working_memory),
            "emotional_state": self.emotions.get_state().value,
            "confidence": self.self_model.get("confidence", 0.5),
            "total_thoughts": len(self.stream.thoughts),
            "strategies_tried": len(self.metacognition.strategies_tried),
            "guidance": self.emotions.get_emotional_guidance(),
            "recent_insight": self.reflection.generate_insight()
        }
    
    def explain_thinking(self, recent_count: int = 5) -> str:
        """Explain recent thought process"""
        thoughts = self.stream.get_recent(recent_count)
        
        lines = [
            "=== SENTIENT THINKING TRACE ===",
            f"Current State: {self.emotions.get_state().value}",
            f"Confidence: {self.self_model.get('confidence', 0.5):.0%}",
            "",
            "Recent Thoughts:"
        ]
        
        for t in thoughts:
            lines.append(f"  [{t.thought_type.value}] {t.content[:50]}...")
        
        return "\n".join(lines)


# Singleton
_sentient_thinking = None

def get_sentient_thinking() -> SentientThinking:
    global _sentient_thinking
    if _sentient_thinking is None:
        _sentient_thinking = SentientThinking()
    return _sentient_thinking
