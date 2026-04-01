"""
SL-LLM Thinking Engine
Integrates: Psychology, Critical Thinking, Logic, Graph Theory, 
            String Theory, Financial Mathematics, Calculus
"""

import re
import math
import json
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict
from datetime import datetime


class ThinkingToolbox:
    """Human thinking methodologies for AI reasoning"""
    
    @staticmethod
    def lateral_thinking(problem: str) -> List[str]:
        """Generate alternative perspectives (psychology-based)"""
        perspectives = [
            f"What if {problem} is actually the opposite?",
            f"What would a child ask about {problem}?",
            f"How would a competitor solve {problem}?",
            f"What constraints am I assuming that might be false?",
            f"What would happen if I reversed the sequence?",
        ]
        return perspectives
    
    @staticmethod
    def first_principles(problem: str) -> Dict:
        """Break down to fundamental truths"""
        return {
            "core_question": f"What is the essential nature of {problem}?",
            "assumptions": [],
            "reducible_elements": problem.split(),
            "fundamental_truths": []
        }
    
    @staticmethod
    def inversion_thinking(goal: str) -> List[str]:
        """Think backwards from failure"""
        return [
            f"How would I definitely FAIL at {goal}?",
            f"What would make {goal} impossible?",
            f"What worst-case scenarios exist?",
        ]


class CriticalThinking:
    """Logic and reasoning framework"""
    
    @staticmethod
    def evaluate_evidence(claim: str, evidence: List[str]) -> Dict:
        """Evaluate claim strength"""
        strength = len(evidence)
        logical_connections = sum(1 for e in evidence if any(w in e.lower() for w in ["because", "therefore", "thus", "hence"]))
        
        return {
            "claim": claim,
            "evidence_count": strength,
            "logical_flow": logical_connections,
            "strength": "strong" if logical_connections >= 2 else "moderate" if logical_connections == 1 else "weak",
            "reasoning_chain": evidence
        }
    
    @staticmethod
    def spot_fallacies(arguments: List[str]) -> List[Dict]:
        """Detect logical fallacies"""
        fallacies = []
        
        patterns = {
            "ad_hominem": r"(you|they|he|she).*(stupid|idiot|wrong|liar)",
            "strawman": r"(misrepresent|twist|distort).*argument",
            "false_dilemma": r"(either|or).*(only|two)",
            "circular": r"(because|therefore).*(because|therefore)",
            "bandwagon": r"(everyone|everybody|all).*(know|believe|agree)",
        }
        
        for i, arg in enumerate(arguments):
            for fallacy, pattern in patterns.items():
                if re.search(pattern, arg.lower()):
                    fallacies.append({"index": i, "type": fallacy, "text": arg})
        
        return fallacies
    
    @staticmethod
    def syllogism(premise1: str, premise2: str) -> Dict:
        """Classic logic syllogism"""
        return {
            "premise_1": premise1,
            "premise_2": premise2,
            "conclusion": f"Therefore: {premise1} + {premise2}",
            "valid": True,
            "form": "modus_ponens"
        }


class GraphTheoryReasoner:
    """Graph-based reasoning for relationships"""
    
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[str, List[str]] = defaultdict(list)
        self.weights: Dict[Tuple[str, str], float] = {}
    
    def add_concept(self, concept: str, related: List[str], weight: float = 1.0):
        """Add concept to reasoning graph"""
        self.nodes.add(concept)
        for r in related:
            self.nodes.add(r)
            self.edges[concept].append(r)
            self.edges[r].append(concept)
            self.edges[(concept, r)] = [weight]
    
    def find_path(self, start: str, end: str) -> Optional[List[str]]:
        """BFS path finding - relationships between concepts"""
        if start not in self.nodes or end not in self.nodes:
            return None
        
        visited = {start}
        queue = [(start, [start])]
        
        while queue:
            node, path = queue.pop(0)
            if node == end:
                return path
            
            for neighbor in self.edges[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def centrality(self, concept: str) -> float:
        """Calculate concept importance (degree centrality)"""
        return len(self.edges.get(concept, []))
    
    def similarity(self, concept1: str, concept2: str) -> float:
        """Jaccard similarity between concepts"""
        neighbors1 = set(self.edges.get(concept1, []))
        neighbors2 = set(self.edges.get(concept2, []))
        
        if not neighbors1 or not neighbors2:
            return 0.0
        
        intersection = len(neighbors1 & neighbors2)
        union = len(neighbors1 | neighbors2)
        
        return intersection / union if union > 0 else 0.0


class StringPatternMatcher:
    """String theory-inspired pattern matching"""
    
    @staticmethod
    def find_recurring_patterns(text: str, min_length: int = 3) -> List[Dict]:
        """Find repeating string patterns"""
        patterns = defaultdict(int)
        
        for length in range(min_length, len(text) // 2):
            for i in range(len(text) - length):
                pattern = text[i:i + length]
                if pattern not in text[i + length:]:
                    continue
                patterns[pattern] += 1
        
        return [
            {"pattern": p, "count": c, "length": len(p)}
            for p, c in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    @staticmethod
    def string_distance(s1: str, s2: str) -> int:
        """Levenshtein distance - edit distance"""
        if len(s1) < len(s2):
            return StringPatternMatcher.string_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def entropy(text: str) -> float:
        """Calculate string entropy - randomness measure"""
        if not text:
            return 0.0
        
        freq = defaultdict(int)
        for c in text:
            freq[c] += 1
        
        entropy = 0.0
        length = len(text)
        
        for count in freq.values():
            p = count / length
            entropy -= p * math.log2(p)
        
        return entropy


class FinancialMathematics:
    """Financial math for decision making"""
    
    @staticmethod
    def expected_value(outcomes: List[Tuple[float, float]]) -> float:
        """Calculate expected value: Σ(probability * value)"""
        return sum(prob * value for prob, value in outcomes)
    
    @staticmethod
    def risk_adjusted_return(expected_return: float, risk: float, risk_free: float = 0.02) -> float:
        """Sharpe ratio-like calculation"""
        return (expected_return - risk_free) / risk if risk > 0 else 0.0
    
    @staticmethod
    def compound_growth(principal: float, rate: float, periods: int) -> float:
        """A = P(1 + r)^n"""
        return principal * math.pow(1 + rate, periods)
    
    @staticmethod
    def time_value_of_money(future_value: float, rate: float, periods: int) -> float:
        """Present value calculation: PV = FV / (1 + r)^n"""
        return future_value / math.pow(1 + rate, periods)
    
    @staticmethod
    def decision_matrix(criteria: Dict[str, float], weights: Dict[str, float]) -> float:
        """Weighted decision scoring"""
        score = 0.0
        for criterion, value in criteria.items():
            score += value * weights.get(criterion, 1.0)
        return score


class CalculusReasoner:
    """Calculus for optimization and change"""
    
    @staticmethod
    def analyze_change(values: List[float]) -> Dict:
        """Analyze rate of change"""
        if len(values) < 2:
            return {"error": "Insufficient data"}
        
        changes = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        
        return {
            "values": values,
            "changes": changes,
            "avg_change": sum(changes) / len(changes),
            "max_increase": max(changes),
            "max_decrease": min(changes),
            "trend": "increasing" if sum(changes) > 0 else "decreasing" if sum(changes) < 0 else "stable"
        }
    
    @staticmethod
    def optimize_gradient(gradient_fn, start: float, learning_rate: float = 0.1, iterations: int = 100) -> float:
        """Gradient descent for finding minimum"""
        current = start
        
        for _ in range(iterations):
            try:
                gradient = gradient_fn(current)
                current -= learning_rate * gradient
            except:
                break
        
        return current
    
    @staticmethod
    def convergence_test(sequence: List[float], tolerance: float = 0.001) -> bool:
        """Test if sequence converges"""
        if len(sequence) < 2:
            return False
        
        for i in range(len(sequence) - 1):
            if abs(sequence[i + 1] - sequence[i]) > tolerance:
                return False
        
        return True
    
    @staticmethod
    def area_approximation(values: List[float], dx: float = 1.0) -> float:
        """Riemann sum approximation"""
        return sum(v * dx for v in values)


class ReasoningEngine:
    """Unified reasoning engine combining all methodologies"""
    
    def __init__(self):
        self.thinking = ThinkingToolbox()
        self.critical = CriticalThinking()
        self.graph = GraphTheoryReasoner()
        self.patterns = StringPatternMatcher()
        self.finance = FinancialMathematics()
        self.calculus = CalculusReasoner()
    
    def reason(self, problem: str, context: Dict = None) -> Dict:
        """Multi-disciplinary reasoning on a problem"""
        
        # Lateral thinking perspectives
        perspectives = self.thinking.lateral_thinking(problem)
        
        # First principles breakdown
        first_principles = self.thinking.first_principles(problem)
        
        # Inversion thinking
        inversion = self.thinking.inversion_thinking(problem)
        
        return {
            "problem": problem,
            "lateral_perspectives": perspectives,
            "first_principles": first_principles,
            "inversion_thinking": inversion,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_code_quality(self, code: str) -> Dict:
        """Analyze code using multiple metrics"""
        
        # Pattern detection
        patterns = self.patterns.find_recurring_patterns(code)
        
        # Entropy analysis (complexity)
        entropy = self.patterns.entropy(code)
        
        # Change analysis
        lines = code.split('\n')
        line_lengths = [len(l) for l in lines]
        change_analysis = self.calculus.analyze_change(line_lengths)
        
        return {
            "patterns_found": patterns,
            "complexity_entropy": entropy,
            "line_change_analysis": change_analysis,
            "quality_score": min(100, max(0, 100 - entropy * 10))
        }
    
    def make_decision(self, options: List[Dict], criteria: Dict[str, float]) -> Dict:
        """Make decision using financial math and logic"""
        
        scored_options = []
        
        for option in options:
            score = self.finance.decision_matrix(
                option.get("scores", {}),
                criteria
            )
            scored_options.append({
                "option": option.get("name", "Unnamed"),
                "score": score,
                "reasoning": option.get("reason", "")
            })
        
        scored_options.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "decision": scored_options[0] if scored_options else None,
            "alternatives": scored_options,
            "methodology": "weighted_decision_matrix"
        }


# Singleton instance
_reasoning_engine = None

def get_reasoning_engine() -> ReasoningEngine:
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = ReasoningEngine()
    return _reasoning_engine
