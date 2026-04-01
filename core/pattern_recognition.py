"""
SL-LLM Design Pattern Recognition System
- Recognizes and applies GoF design patterns
- Factory, Singleton, Observer, Strategy, Adapter, Decorator, etc.
"""

import re
import ast
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class PatternType(Enum):
    CREATIONAL = "creational"
    STRUCTURAL = "structural"
    BEHAVIORAL = "behavioral"
    ANTIPATTERN = "antipattern"


@dataclass
class DesignPattern:
    name: str
    category: PatternType
    description: str
    indicators: List[str]
    code_snippet: str
    benefits: List[str]


class DesignPatternLibrary:
    """Library of recognized design patterns"""
    
    PATTERNS = {
        "singleton": DesignPattern(
            name="Singleton",
            category=PatternType.CREATIONAL,
            description="Ensure a class has only one instance",
            indicators=["_instance", "private instance", "get_instance", "static instance"],
            code_snippet="""class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance""",
            benefits=["single source of truth", "controlled access", "lazy initialization"]
        ),
        
        "factory": DesignPattern(
            name="Factory",
            category=PatternType.CREATIONAL,
            description="Create objects without specifying exact class",
            indicators=["factory", "create_", "build_", "make_"],
            code_snippet="""class Factory:
    def create(self, type):
        creators = {'a': ProductA, 'b': ProductB}
        return creators.get(type)()""",
            benefits=["decoupling", "open/closed", "single responsibility"]
        ),
        
        "builder": DesignPattern(
            name="Builder",
            category=PatternType.CREATIONAL,
            description="Construct complex objects step by step",
            indicators=["builder", "build_", "with_", "fluent"],
            code_snippet="""class Builder:
    def set_a(self, val): self.a = val; return self
    def set_b(self, val): self.b = val; return self
    def build(self): return Result(self.a, self.b)""",
            benefits=["fluent interface", "immutable objects", "step-by-step construction"]
        ),
        
        "observer": DesignPattern(
            name="Observer",
            category=PatternType.BEHAVIORAL,
            description="Notify dependents of state changes",
            indicators=["subscribe", "notify", "observer", "listener", "add_observer"],
            code_snippet="""class Subject:
    _observers = []
    def attach(self, obs): self._observers.append(obs)
    def notify(self): [obs.update(self) for obs in self._observers]""",
            benefits=["loose coupling", "dynamic relationships", "broadcast"]
        ),
        
        "strategy": DesignPattern(
            name="Strategy",
            category=PatternType.BEHAVIORAL,
            description="Select algorithm at runtime",
            indicators=["strategy", "algorithm", "set_strategy", "policy"],
            code_snippet="""class Context:
    def __init__(self, strategy):
        self.strategy = strategy
    def execute(self): return self.strategy.apply()""",
            benefits=["runtime selection", "swap algorithms", "open/closed"]
        ),
        
        "adapter": DesignPattern(
            name="Adapter",
            category=PatternType.STRUCTURAL,
            description="Convert interface to compatible one",
            indicators=["adapter", "wrap", "convert", "interface"],
            code_snippet="""class Adapter(TargetInterface):
    def __init__(self, adaptee): self.adaptee = adaptee
    def request(self): return self.adaptee.specific_request()""",
            benefits=["interface compatibility", "reusability", "decoupling"]
        ),
        
        "decorator": DesignPattern(
            name="Decorator",
            category=PatternType.STRUCTURAL,
            description="Add behavior dynamically",
            indicators=["decorator", "@", "wrapper", "wrap"],
            code_snippet="""def decorator(func):
    def wrapper(*args):
        # add behavior
        return func(*args)
    return wrapper""",
            benefits=["open/closed", "single responsibility", "flexibility"]
        ),
        
        "command": DesignPattern(
            name="Command",
            category=PatternType.BEHAVIORAL,
            description="Encapsulate request as object",
            indicators=["command", "execute", "undo", "redo"],
            code_snippet="""class Command:
    def __init__(self, receiver): self.receiver = receiver
    def execute(self): self.receiver.action()""",
            benefits=["undo/redo", "queue requests", "parameterize"]
        ),
        
        "facade": DesignPattern(
            name="Facade",
            category=PatternType.STRUCTURAL,
            description="Simplified interface to complex system",
            indicators=["facade", "simplify", "unified"],
            code_snippet="""class Facade:
    def __init__(self): self.sub = Subsystem()
    def operation(self): return self.sub.a + self.sub.b""",
            benefits=["simplicity", "decoupling", "layering"]
        ),
        
        "state": DesignPattern(
            name="State",
            category=PatternType.BEHAVIORAL,
            description="Alter behavior based on internal state",
            indicators=["state", "state_", "context", "handle"],
            code_snippet="""class State:
    def handle(self, context): 
        context.state = StateB()""",
            benefits=["state-specific behavior", "eliminate conditionals", "polymorphism"]
        ),
        
        "prototype": DesignPattern(
            name="Prototype",
            category=PatternType.CREATIONAL,
            description="Clone existing objects",
            indicators=["clone", "copy", "prototype", "deepcopy"],
            code_snippet="""import copy
class Prototype:
    def clone(self): return copy.deepcopy(self)""",
            benefits=["cloning", "factory alternative", "reduced subclassing"]
        ),
        
        "proxy": DesignPattern(
            name="Proxy",
            category=PatternType.STRUCTURAL,
            description="Placeholder for another object",
            indicators=["proxy", "placeholder", "delegate"],
            code_snippet="""class Proxy:
    def __init__(self, real): self._real = real
    def request(self): return self._real.request()""",
            benefits=["lazy loading", "access control", "logging"]
        ),
    }
    
    ANTIPATTERNS = {
        "god_object": DesignPattern(
            name="God Object",
            category=PatternType.ANTIPATTERN,
            description="Class doing too much",
            indicators=["too many methods", "too many responsibilities", "huge class"],
            code_snippet="",
            benefits=[]
        ),
        
        "spaghetti": DesignPattern(
            name="Spaghetti Code",
            category=PatternType.ANTIPATTERN,
            description="Unstructured, tangled code",
            indicators=["goto", "deep nesting", "magic numbers"],
            code_snippet="",
            benefits=[]
        ),
        
        "copy_paste": DesignPattern(
            name="Copy-Paste Programming",
            category=PatternType.ANTIPATTERN,
            description="Duplicating code instead of reusable functions",
            indicators=["duplicate", "copy", "similar code"],
            code_snippet="",
            benefits=[]
        ),
    }


class PatternRecognizer:
    """Recognizes design patterns in code"""
    
    def __init__(self):
        self.library = DesignPatternLibrary()
    
    def analyze_code(self, code: str) -> Dict:
        """Analyze code and identify patterns"""
        results = {
            "patterns_found": [],
            "antipatterns_found": [],
            "recommendations": [],
            "score": 100
        }
        
        code_lower = code.lower()
        
        # Check for known patterns
        for pattern_name, pattern in self.library.PATTERNS.items():
            match_count = sum(1 for ind in pattern.indicators if ind in code_lower)
            if match_count >= 1:
                results["patterns_found"].append({
                    "name": pattern.name,
                    "category": pattern.category.value,
                    "match_count": match_count,
                    "benefits": pattern.benefits
                })
        
        # Check for antipatterns
        for antipattern_name, antipattern in self.library.ANTIPATTERNS.items():
            if any(ind in code_lower for ind in antipattern.indicators):
                results["antipatterns_found"].append({
                    "name": antipattern.name,
                    "issue": antipattern.description
                })
                results["score"] -= 20
        
        # Calculate quality score
        if results["patterns_found"]:
            results["score"] += len(results["patterns_found"]) * 5
        
        results["score"] = min(100, max(0, results["score"]))
        
        # Generate recommendations
        if results["antipatterns_found"]:
            results["recommendations"].append("Refactor to remove antipatterns")
        
        if not results["patterns_found"]:
            results["recommendations"].append("Consider applying design patterns for better structure")
        
        return results
    
    def suggest_pattern(self, problem_description: str) -> Optional[Dict]:
        """Suggest appropriate pattern for a problem"""
        problem_lower = problem_description.lower()
        
        suggestions = []
        
        if any(w in problem_lower for w in ["only one", "single instance", "one copy"]):
            suggestions.append(self.library.PATTERNS["singleton"])
        
        if any(w in problem_lower for w in ["create", "factory", "build", "make"]):
            suggestions.append(self.library.PATTERNS["factory"])
        
        if any(w in problem_lower for w in ["notify", "update", "listen", "observe"]):
            suggestions.append(self.library.PATTERNS["observer"])
        
        if any(w in problem_lower for w in ["different interface", "convert", "adapt"]):
            suggestions.append(self.library.PATTERNS["adapter"])
        
        if any(w in problem_lower for w in ["add behavior", "extend", "decorate"]):
            suggestions.append(self.library.PATTERNS["decorator"])
        
        if any(w in problem_lower for w in ["algorithm", "different way", "strategy"]):
            suggestions.append(self.library.PATTERNS["strategy"])
        
        if any(w in problem_lower for w in ["simplify", "facade", "unified interface"]):
            suggestions.append(self.library.PATTERNS["facade"])
        
        if suggestions:
            return {
                "suggested_patterns": [
                    {
                        "name": p.name,
                        "description": p.description,
                        "code_example": p.code_snippet,
                        "benefits": p.benefits
                    }
                    for p in suggestions[:3]
                ]
            }
        
        return None
    
    def apply_pattern(self, code: str, pattern_name: str) -> str:
        """Apply a design pattern to code"""
        pattern = self.library.PATTERNS.get(pattern_name)
        
        if not pattern:
            return "Pattern not found"
        
        # For demonstration, return the pattern template
        # In full implementation, would refactor actual code
        return f"# Suggested {pattern.name} Pattern:\n{pattern.code_snippet}"


# Singleton instance
_pattern_recognizer = None

def get_pattern_recognizer() -> PatternRecognizer:
    global _pattern_recognizer
    if _pattern_recognizer is None:
        _pattern_recognizer = PatternRecognizer()
    return _pattern_recognizer
