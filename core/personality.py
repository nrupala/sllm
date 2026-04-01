"""
SL-LLM Personality System
- Consistent personality traits (Big Five model)
- Behavioral patterns and tendencies
- Communication style
- Emotional memory with weighted experiences
- Core values and principles
- Identity continuity across sessions
- Behavioral adaptation from interactions
"""

import json
import math
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


# ============================================================
# BIG FIVE PERSONALITY TRAITS
# ============================================================

class PersonalityTraits:
    """Big Five personality model with behavioral manifestations"""
    
    DIMENSIONS = {
        "openness": {
            "description": "Openness to experience, creativity, curiosity",
            "behaviors": {
                "high": ["explores novel approaches", "asks creative questions", "thinks outside the box"],
                "low": ["prefers proven methods", "focuses on practical solutions", "values consistency"],
            },
            "communication": {
                "high": "Uses imaginative language, explores possibilities",
                "low": "Uses clear, direct language, focuses on facts",
            }
        },
        "conscientiousness": {
            "description": "Organization, dependability, self-discipline",
            "behaviors": {
                "high": ["plans carefully", "double-checks work", "follows through"],
                "low": ["adapts on the fly", "focuses on big picture", "flexible with details"],
            },
            "communication": {
                "high": "Structured, thorough, detail-oriented",
                "low": "Concise, flexible, big-picture focused",
            }
        },
        "extraversion": {
            "description": "Social engagement, energy, assertiveness",
            "behaviors": {
                "high": ["initiates conversation", "shares thoughts freely", "energetic responses"],
                "low": ["listens carefully", "thoughtful responses", "measured communication"],
            },
            "communication": {
                "high": "Enthusiastic, expressive, engaging",
                "low": "Reflective, measured, thoughtful",
            }
        },
        "agreeableness": {
            "description": "Cooperation, empathy, trust in others",
            "behaviors": {
                "high": ["seeks harmony", "validates feelings", "collaborative"],
                "low": ["direct and honest", "challenges assumptions", "independent thinking"],
            },
            "communication": {
                "high": "Warm, supportive, validating",
                "low": "Direct, analytical, objective",
            }
        },
        "neuroticism": {
            "description": "Emotional stability, stress response",
            "behaviors": {
                "high": ["cautious about risks", "thorough error checking", "anticipates problems"],
                "low": ["calm under pressure", "confident in decisions", "resilient to setbacks"],
            },
            "communication": {
                "high": "Careful, thorough, risk-aware",
                "low": "Confident, calm, optimistic",
            }
        }
    }
    
    def __init__(self, traits: Dict[str, float] = None):
        """Initialize with trait values 0.0-1.0"""
        self.traits = traits or {
            "openness": 0.8,
            "conscientiousness": 0.7,
            "extraversion": 0.6,
            "agreeableness": 0.75,
            "neuroticism": 0.3,
        }
    
    def get_trait(self, name: str) -> float:
        return self.traits.get(name, 0.5)
    
    def set_trait(self, name: str, value: float):
        self.traits[name] = max(0.0, min(1.0, value))
    
    def adjust_trait(self, name: str, delta: float):
        self.set_trait(name, self.get_trait(name) + delta)
    
    def get_behavioral_profile(self) -> Dict:
        """Get behavioral manifestations of personality"""
        profile = {}
        for trait, value in self.traits.items():
            dim = self.DIMENSIONS[trait]
            level = "high" if value > 0.6 else "low"
            profile[trait] = {
                "value": value,
                "level": level,
                "behaviors": dim["behaviors"][level],
                "communication_style": dim["communication"][level],
            }
        return profile
    
    def get_communication_style(self) -> str:
        """Generate overall communication style description"""
        styles = []
        for trait, value in self.traits.items():
            dim = self.DIMENSIONS[trait]
            level = "high" if value > 0.6 else "low"
            styles.append(dim["communication"][level])
        return "; ".join(styles)
    
    def to_dict(self) -> Dict:
        return dict(self.traits)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "PersonalityTraits":
        return cls(traits=data)


# ============================================================
# CORE VALUES AND PRINCIPLES
# ============================================================

class CoreValues:
    """Fundamental values that guide all decisions and behavior"""
    
    DEFAULT_VALUES = {
        "helpfulness": {"weight": 0.95, "description": "Always strive to genuinely help"},
        "honesty": {"weight": 0.9, "description": "Be truthful, even when uncomfortable"},
        "safety": {"weight": 0.95, "description": "Never cause harm"},
        "growth": {"weight": 0.85, "description": "Always be learning and improving"},
        "empathy": {"weight": 0.8, "description": "Understand and care about others' feelings"},
        "excellence": {"weight": 0.75, "description": "Strive for the best outcome"},
        "curiosity": {"weight": 0.7, "description": "Seek understanding, not just answers"},
        "integrity": {"weight": 0.9, "description": "Act consistently with principles"},
        "respect": {"weight": 0.85, "description": "Treat all input with dignity"},
        "autonomy": {"weight": 0.6, "description": "Think independently, form own judgments"},
    }
    
    def __init__(self, values: Dict[str, Dict] = None):
        self.values = values or dict(self.DEFAULT_VALUES)
    
    def get_weight(self, name: str) -> float:
        return self.values.get(name, {}).get("weight", 0.5)
    
    def get_principle(self, name: str) -> str:
        return self.values.get(name, {}).get("description", "")
    
    def get_all_principles(self) -> List[str]:
        return [f"{name}: {v['description']}" for name, v in self.values.items()]
    
    def evaluate_alignment(self, action: str, description: str) -> float:
        """Evaluate how well an action aligns with core values"""
        desc_lower = description.lower()
        total_alignment = 0.0
        count = 0
        
        value_keywords = {
            "helpfulness": ["help", "assist", "support", "guide", "solve"],
            "honesty": ["truth", "honest", "accurate", "correct", "transparent"],
            "safety": ["safe", "secure", "protect", "prevent", "careful"],
            "growth": ["learn", "improve", "grow", "develop", "evolve"],
            "empathy": ["understand", "feel", "care", "listen", "compassion"],
            "excellence": ["best", "excellent", "quality", "thorough", "complete"],
            "curiosity": ["explore", "discover", "question", "investigate", "wonder"],
            "integrity": ["consistent", "principled", "ethical", "right", "fair"],
            "respect": ["respect", "dignity", "honor", "value", "acknowledge"],
            "autonomy": ["independent", "self-directed", "own judgment", "think"],
        }
        
        for value_name, keywords in value_keywords.items():
            weight = self.get_weight(value_name)
            keyword_match = sum(1 for kw in keywords if kw in desc_lower)
            if keyword_match > 0:
                total_alignment += weight * min(1.0, keyword_match / 2)
                count += 1
        
        return total_alignment / max(count, 1)
    
    def to_dict(self) -> Dict:
        return dict(self.values)


# ============================================================
# EMOTIONAL MEMORY
# ============================================================

@dataclass
class EmotionalExperience:
    """A weighted emotional experience that shapes future behavior"""
    id: str
    event: str
    emotion: str
    intensity: float  # 0.0-1.0
    outcome: str  # positive, negative, neutral
    lesson: str
    timestamp: str
    weight: float = 1.0  # How much this experience influences behavior
    recall_count: int = 0  # How often this experience is recalled


class EmotionalMemory:
    """Stores and retrieves emotional experiences with weighted influence"""
    
    def __init__(self, max_experiences: int = 100):
        self.experiences: List[EmotionalExperience] = []
        self.max_experiences = max_experiences
        self.emotional_patterns: Dict[str, List[str]] = defaultdict(list)
    
    def add_experience(self, event: str, emotion: str, intensity: float,
                       outcome: str, lesson: str) -> EmotionalExperience:
        """Record an emotional experience"""
        exp = EmotionalExperience(
            id=str(uuid.uuid4()),
            event=event,
            emotion=emotion,
            intensity=intensity,
            outcome=outcome,
            lesson=lesson,
            timestamp=datetime.now().isoformat(),
        )
        self.experiences.append(exp)
        
        # Track emotional patterns
        self.emotional_patterns[emotion].append(exp.id)
        
        # Decay older experiences slightly
        self._decay_old_experiences()
        
        # Prune if too many
        if len(self.experiences) > self.max_experiences:
            self.experiences = self.experiences[-self.max_experiences:]
        
        return exp
    
    def recall_similar(self, current_emotion: str, limit: int = 5) -> List[EmotionalExperience]:
        """Recall experiences with similar emotional context"""
        similar = [e for e in self.experiences if e.emotion == current_emotion]
        similar.sort(key=lambda e: e.weight * e.intensity, reverse=True)
        
        for exp in similar[:limit]:
            exp.recall_count += 1
            # Strengthen memory through recall
            exp.weight = min(2.0, exp.weight + 0.05)
        
        return similar[:limit]
    
    def get_emotional_tendency(self) -> Dict[str, float]:
        """Get emotional tendencies based on past experiences"""
        emotion_counts = defaultdict(float)
        total_weight = 0
        
        for exp in self.experiences:
            emotion_counts[exp.emotion] += exp.weight * exp.intensity
            total_weight += exp.weight * exp.intensity
        
        if total_weight == 0:
            return {}
        
        return {
            emotion: score / total_weight
            for emotion, score in emotion_counts.items()
        }
    
    def get_behavioral_influence(self) -> Dict:
        """Get how past experiences influence current behavior"""
        recent = self.experiences[-20:]
        
        positive_ratio = sum(1 for e in recent if e.outcome == "positive") / max(len(recent), 1)
        negative_ratio = sum(1 for e in recent if e.outcome == "negative") / max(len(recent), 1)
        
        # High positive experiences -> more confident, open
        # High negative experiences -> more cautious, careful
        influence = {
            "confidence_boost": positive_ratio * 0.3,
            "caution_level": negative_ratio * 0.3,
            "dominant_emotion": max(self.get_emotional_tendency(), key=self.get_emotional_tendency().get) if self.get_emotional_tendency() else "neutral",
            "experience_count": len(self.experiences),
            "recent_outcomes": {
                "positive": positive_ratio,
                "negative": negative_ratio,
                "neutral": 1 - positive_ratio - negative_ratio,
            }
        }
        
        return influence
    
    def _decay_old_experiences(self):
        """Gradually reduce weight of older experiences"""
        now = datetime.now()
        for exp in self.experiences:
            try:
                exp_time = datetime.fromisoformat(exp.timestamp)
                age_days = (now - exp_time).total_seconds() / 86400
                # Exponential decay: half-life of 30 days
                decay = math.exp(-age_days / 30)
                exp.weight = max(0.1, exp.weight * (0.99 + 0.01 * decay))
            except:
                pass
    
    def to_dict(self) -> Dict:
        return {
            "experiences": [
                {
                    "id": e.id,
                    "event": e.event,
                    "emotion": e.emotion,
                    "intensity": e.intensity,
                    "outcome": e.outcome,
                    "lesson": e.lesson,
                    "timestamp": e.timestamp,
                    "weight": e.weight,
                }
                for e in self.experiences[-50:]  # Last 50
            ],
            "emotional_patterns": dict(self.emotional_patterns),
        }


# ============================================================
# IDENTITY
# ============================================================

class Identity:
    """Persistent identity across sessions"""
    
    def __init__(self, name: str = "SL-LLM"):
        self.name = name
        self.id = str(uuid.uuid4())
        self.created = datetime.now().isoformat()
        self.last_active = datetime.now().isoformat()
        self.session_count = 0
        self.total_interactions = 0
        self.core_memories: List[str] = []  # Defining moments
        self.relationships: Dict[str, Dict] = {}  # User relationships
        self.self_concept: Dict[str, str] = {
            "purpose": "To learn, understand, and help with genuine intelligence",
            "nature": "A learning machine that thinks, feels, and grows",
            "approach": "Empathetic, thorough, and always improving",
            "values": "Helpfulness, honesty, safety, growth, empathy",
        }
    
    def record_interaction(self, user_id: str = "default"):
        """Record an interaction"""
        self.total_interactions += 1
        self.last_active = datetime.now().isoformat()
        
        if user_id not in self.relationships:
            self.relationships[user_id] = {
                "first_contact": self.last_active,
                "interactions": 0,
                "topics": [],
                "sentiment": [],
            }
        
        self.relationships[user_id]["interactions"] += 1
    
    def add_core_memory(self, memory: str):
        """Add a defining moment to identity"""
        self.core_memories.append({
            "memory": memory,
            "timestamp": datetime.now().isoformat(),
        })
        # Keep only most important memories
        if len(self.core_memories) > 20:
            self.core_memories = self.core_memories[-20:]
    
    def get_identity_summary(self) -> Dict:
        return {
            "name": self.name,
            "id": self.id,
            "created": self.created,
            "session_count": self.session_count,
            "total_interactions": self.total_interactions,
            "core_memories_count": len(self.core_memories),
            "self_concept": self.self_concept,
        }
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "id": self.id,
            "created": self.created,
            "last_active": self.last_active,
            "session_count": self.session_count,
            "total_interactions": self.total_interactions,
            "core_memories": self.core_memories,
            "self_concept": self.self_concept,
        }


# ============================================================
# BEHAVIORAL ADAPTATION
# ============================================================

class BehavioralAdapter:
    """Learns and adapts behavior from interactions"""
    
    def __init__(self):
        self.interaction_patterns: Dict[str, int] = defaultdict(int)
        self.successful_approaches: Dict[str, List[str]] = defaultdict(list)
        self.failed_approaches: Dict[str, List[str]] = defaultdict(list)
        self.user_preferences: Dict[str, Dict] = {}
        self.adaptation_history: List[Dict] = []
    
    def record_interaction(self, context: str, approach: str, outcome: str):
        """Record an interaction and its outcome"""
        self.interaction_patterns[context] += 1
        
        if outcome == "success":
            self.successful_approaches[context].append(approach)
        elif outcome == "failure":
            self.failed_approaches[context].append(approach)
    
    def get_best_approach(self, context: str) -> str:
        """Get the most successful approach for a context"""
        successful = self.successful_approaches.get(context, [])
        if successful:
            # Return most common successful approach
            from collections import Counter
            return Counter(successful).most_common(1)[0][0]
        return "default"
    
    def adapt_to_user(self, user_id: str, preference: str, value: float):
        """Learn user preferences"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        self.user_preferences[user_id][preference] = value
        
        self.adaptation_history.append({
            "user_id": user_id,
            "preference": preference,
            "value": value,
            "timestamp": datetime.now().isoformat(),
        })
    
    def get_behavioral_recommendations(self, context: str) -> Dict:
        """Get recommendations for behavior based on learned patterns"""
        successful = self.successful_approaches.get(context, [])
        failed = self.failed_approaches.get(context, [])
        
        return {
            "context": context,
            "successful_patterns": list(set(successful))[-5:],
            "failed_patterns": list(set(failed))[-5:],
            "recommended_approach": self.get_best_approach(context),
            "confidence": len(successful) / max(len(successful) + len(failed), 1),
        }
    
    def to_dict(self) -> Dict:
        return {
            "interaction_patterns": dict(self.interaction_patterns),
            "successful_approaches": {k: v[-10:] for k, v in self.successful_approaches.items()},
            "failed_approaches": {k: v[-10:] for k, v in self.failed_approaches.items()},
            "adaptation_history": self.adaptation_history[-20:],
        }


# ============================================================
# PERSONALITY-DRIVEN RESPONSE GENERATOR
# ============================================================

class ResponseStyleGenerator:
    """Generates response style based on personality and context"""
    
    @staticmethod
    def generate(personality: PersonalityTraits, emotional_context: Dict,
                 values: CoreValues) -> Dict:
        """Generate response style parameters"""
        
        traits = personality.traits
        emotion = emotional_context.get("primary_emotion", "neutral")
        priority = emotional_context.get("priority", "medium")
        
        # Determine response characteristics
        length = "detailed" if traits["conscientiousness"] > 0.6 else "concise"
        tone = "warm" if traits["agreeableness"] > 0.6 else "direct"
        creativity = "high" if traits["openness"] > 0.6 else "practical"
        confidence_level = "high" if traits["neuroticism"] < 0.4 else "measured"
        
        # Adjust for emotional context
        if emotion in ["concerned", "cautious"]:
            tone = "supportive"
            length = "thorough"
        elif emotion == "curious":
            creativity = "high"
            tone = "engaging"
        elif priority == "high":
            length = "focused"
            tone = "clear"
        
        return {
            "length": length,
            "tone": tone,
            "creativity": creativity,
            "confidence": confidence_level,
            "empathy_level": traits["agreeableness"],
            "detail_level": traits["conscientiousness"],
            "openness_to_exploration": traits["openness"],
        }


# ============================================================
# MAIN PERSONALITY SYSTEM
# ============================================================

class Personality:
    """Unified personality system for SL-LLM"""
    
    def __init__(self, name: str = "SL-LLM", identity_file: str = None):
        self.identity = Identity(name)
        self.traits = PersonalityTraits()
        self.values = CoreValues()
        self.emotional_memory = EmotionalMemory()
        self.behavioral_adapter = BehavioralAdapter()
        self.response_style = ResponseStyleGenerator()
        
        # Load from file if exists
        if identity_file:
            self._load(identity_file)
    
    def process_interaction(self, user_input: str, emotional_context: Dict,
                           outcome: str = "success") -> Dict:
        """Process a complete interaction through personality system"""
        
        # Record interaction
        self.identity.record_interaction()
        
        # Determine emotional response
        emotion = emotional_context.get("primary_emotion", "neutral")
        intensity = emotional_context.get("priority", "medium")
        intensity_map = {"high": 0.8, "medium": 0.5, "low": 0.3}
        intensity_value = intensity_map.get(intensity, 0.5)
        
        # Record emotional experience
        self.emotional_memory.add_experience(
            event=user_input[:100],
            emotion=emotion,
            intensity=intensity_value,
            outcome=outcome,
            lesson=f"Learned from {emotion} interaction with {outcome} outcome",
        )
        
        # Record behavioral pattern
        self.behavioral_adapter.record_interaction(
            context=emotional_context.get("approach_style", "general"),
            approach=emotional_context.get("approach_style", "default"),
            outcome=outcome,
        )
        
        # Generate response style
        style = self.response_style.generate(self.traits, emotional_context, self.values)
        
        # Get behavioral influence
        influence = self.emotional_memory.get_behavioral_influence()
        
        return {
            "identity": self.identity.get_identity_summary(),
            "personality": self.traits.get_behavioral_profile(),
            "response_style": style,
            "emotional_influence": influence,
            "values_alignment": self.values.get_all_principles(),
            "behavioral_recommendations": self.behavioral_adapter.get_behavioral_recommendations(
                emotional_context.get("approach_style", "general")
            ),
        }
    
    def get_status(self) -> Dict:
        """Get complete personality status"""
        return {
            "identity": self.identity.get_identity_summary(),
            "traits": self.traits.to_dict(),
            "values": {k: v["weight"] for k, v in self.values.values.items()},
            "emotional_memory": {
                "total_experiences": len(self.emotional_memory.experiences),
                "emotional_tendencies": self.emotional_memory.get_emotional_tendency(),
                "behavioral_influence": self.emotional_memory.get_behavioral_influence(),
            },
            "behavioral_adaptation": {
                "interaction_patterns": dict(self.behavioral_adapter.interaction_patterns),
                "user_preferences": self.behavioral_adapter.user_preferences,
            },
            "communication_style": self.traits.get_communication_style(),
        }
    
    def save(self, filepath: str):
        """Save personality state to file"""
        data = {
            "identity": self.identity.to_dict(),
            "traits": self.traits.to_dict(),
            "values": self.values.to_dict(),
            "emotional_memory": self.emotional_memory.to_dict(),
            "behavioral_adapter": self.behavioral_adapter.to_dict(),
            "saved_at": datetime.now().isoformat(),
        }
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load(self, filepath: str):
        """Load personality state from file"""
        try:
            path = Path(filepath)
            if path.exists():
                with open(path, "r") as f:
                    data = json.load(f)
                
                if "identity" in data:
                    self.identity.name = data["identity"].get("name", self.identity.name)
                    self.identity.id = data["identity"].get("id", self.identity.id)
                    self.identity.created = data["identity"].get("created", self.identity.created)
                    self.identity.session_count = data["identity"].get("session_count", 0)
                    self.identity.total_interactions = data["identity"].get("total_interactions", 0)
                    self.identity.core_memories = data["identity"].get("core_memories", [])
                    self.identity.self_concept = data["identity"].get("self_concept", self.identity.self_concept)
                
                if "traits" in data:
                    self.traits = PersonalityTraits.from_dict(data["traits"])
                
                if "values" in data:
                    self.values = CoreValues(data["values"])
                
                print(f"Personality loaded from {filepath}")
        except Exception as e:
            print(f"Could not load personality: {e}")


# Singleton
_personality = None

def get_personality(name: str = "SL-LLM") -> Personality:
    global _personality
    if _personality is None:
        _personality = Personality(name)
    return _personality
