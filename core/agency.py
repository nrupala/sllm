"""
SL-LLM Agency System
- Autonomous decision making with reasoning trace
- Goal-directed behavior
- Ethical constraints
- Transparency through reasoning logs
"""

import uuid
import json
from datetime import datetime
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class DecisionType(Enum):
    IMMEDIATE = "immediate"     # Quick decisions
    DELIBERATE = "deliberate"   # Thoughtful decisions
    REFLEXIVE = "reflexive"      # Instinctive
    CREATIVE = "creative"        # Novel solutions


class EthicalConstraint(Enum):
    SAFE = "safe"               # No harm
    HONEST = "honest"           # Truthful
    FAIR = "fair"               # Unbiased
    PRIVATE = "private"         # Respect privacy
    HELPFUL = "helpful"         # Assist user


@dataclass
class ReasoningStep:
    step_id: str
    step_number: int
    thought: str
    evidence: List[str] = field(default_factory=list)
    alternatives_considered: List[str] = field(default_factory=list)
    confidence: float = 0.5
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Decision:
    id: str
    decision_type: DecisionType
    context: str
    options_considered: List[Dict]
    chosen_option: Dict
    reasoning_chain: List[ReasoningStep]
    confidence: float
    ethical_checks: List[Dict]
    outcome: Optional[Dict] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class Agency:
    """Autonomous agency system with reasoning trace"""
    
    def __init__(self, name: str = "SL-LLM"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.decision_history: List[Decision] = []
        self.goals: List[Dict] = []
        self.constraints: Dict[EthicalConstraint, bool] = {
            EthicalConstraint.SAFE: True,
            EthicalConstraint.HONEST: True,
            EthicalConstraint.FAIR: True,
            EthicalConstraint.PRIVATE: True,
            EthicalConstraint.HELPFUL: True,
        }
        self.values: Dict[str, float] = {}
    
    def set_goal(self, goal: str, priority: float = 1.0, deadline: Optional[str] = None):
        """Set a goal to pursue"""
        self.goals.append({
            "id": str(uuid.uuid4()),
            "goal": goal,
            "priority": priority,
            "deadline": deadline,
            "created": datetime.now().isoformat(),
            "status": "active"
        })
    
    def add_value(self, value: str, weight: float):
        """Add a value with importance weight"""
        self.values[value] = weight
    
    def enable_constraint(self, constraint: EthicalConstraint, enabled: bool = True):
        """Enable/disable ethical constraint"""
        self.constraints[constraint] = enabled
    
    def make_decision(
        self,
        context: str,
        options: List[Dict],
        decision_type: DecisionType = DecisionType.DELIBERATE
    ) -> Decision:
        """Make autonomous decision with full reasoning trace"""
        
        decision_id = str(uuid.uuid4())
        reasoning_chain = []
        
        # Step 1: Understand the context
        step1 = ReasoningStep(
            step_id=str(uuid.uuid4()),
            step_number=1,
            thought=f"Analyzing context: {context}",
            confidence=0.8
        )
        reasoning_chain.append(step1)
        
        # Step 2: Identify options
        alternatives = [opt.get("name", "Option") for opt in options]
        step2 = ReasoningStep(
            step_id=str(uuid.uuid4()),
            step_number=2,
            thought=f"Identified {len(options)} options to consider",
            alternatives_considered=alternatives,
            confidence=0.9
        )
        reasoning_chain.append(step2)
        
        # Step 3: Evaluate each option
        for i, option in enumerate(options):
            eval_step = ReasoningStep(
                step_id=str(uuid.uuid4()),
                step_number=3 + i,
                thought=f"Evaluating option: {option.get('name', 'Unnamed')}",
                evidence=[f"Pros: {option.get('pros', [])}", f"Cons: {option.get('cons', [])}"],
                confidence=option.get("score", 0.5)
            )
            reasoning_chain.append(eval_step)
        
        # Step 4: Check ethical constraints
        ethical_checks = self._check_ethical_constraints(options)
        
        # Step 5: Select best option
        scored_options = []
        for opt in options:
            score = opt.get("score", 0.5)
            
            # Weight by values alignment
            for value, weight in self.values.items():
                if value in opt.get("values_aligned", []):
                    score += weight * 0.1
            
            # Penalize if violates constraints
            if not ethical_checks.get(opt.get("name", ""), {}).get("passed", True):
                score -= 0.3
            
            scored_options.append({**opt, "final_score": score})
        
        scored_options.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        chosen = scored_options[0] if scored_options else options[0]
        
        step_final = ReasoningStep(
            step_id=str(uuid.uuid4()),
            step_number=len(reasoning_chain) + 1,
            thought=f"Chosen option: {chosen.get('name', 'Unknown')}",
            evidence=[f"Final score: {chosen.get('final_score', 0)}"],
            confidence=chosen.get("final_score", 0.5)
        )
        reasoning_chain.append(step_final)
        
        # Create decision
        decision = Decision(
            id=decision_id,
            decision_type=decision_type,
            context=context,
            options_considered=options,
            chosen_option=chosen,
            reasoning_chain=reasoning_chain,
            confidence=chosen.get("final_score", 0.5),
            ethical_checks=[{"option": k, **v} for k, v in ethical_checks.items()]
        )
        
        self.decision_history.append(decision)
        return decision
    
    def _check_ethical_constraints(self, options: List[Dict]) -> Dict:
        """Check options against ethical constraints"""
        results = {}
        
        for option in options:
            option_name = option.get("name", "Unknown")
            checks = {"passed": True, "violations": []}
            
            # Check each constraint
            if self.constraints.get(EthicalConstraint.SAFE):
                if option.get("harmful", False):
                    checks["passed"] = False
                    checks["violations"].append("unsafe")
            
            if self.constraints.get(EthicalConstraint.HONEST):
                if option.get("dishonest", False):
                    checks["passed"] = False
                    checks["violations"].append("dishonest")
            
            if self.constraints.get(EthicalConstraint.FAIR):
                if option.get("biased", False):
                    checks["passed"] = False
                    checks["violations"].append("unfair")
            
            results[option_name] = checks
        
        return results
    
    def evaluate_outcome(self, decision_id: str, outcome: Dict):
        """Record outcome of a decision for learning"""
        for decision in self.decision_history:
            if decision.id == decision_id:
                decision.outcome = outcome
                break
        
        # Learn from outcome - adjust value weights
        if outcome.get("success"):
            for step in decision.reasoning_chain:
                if step.confidence < 1.0:
                    step.confidence = min(1.0, step.confidence + 0.05)
    
    def get_reasoning_trace(self, decision_id: str) -> List[Dict]:
        """Get full reasoning trace for a decision"""
        for decision in self.decision_history:
            if decision.id == decision_id:
                return [
                    {
                        "step": step.step_number,
                        "thought": step.thought,
                        "evidence": step.evidence,
                        "alternatives": step.alternatives_considered,
                        "confidence": step.confidence
                    }
                    for step in decision.reasoning_chain
                ]
        return []
    
    def explain_decision(self, decision_id: str) -> str:
        """Generate human-readable explanation of decision"""
        for decision in self.decision_history:
            if decision.id == decision_id:
                lines = [
                    f"Decision: {decision.context}",
                    f"Type: {decision.decision_type.value}",
                    f"Confidence: {decision.confidence:.0%}",
                    "",
                    "Reasoning:"
                ]
                
                for step in decision.reasoning_chain:
                    lines.append(f"  {step.step_number}. {step.thought}")
                
                if decision.ethical_checks:
                    lines.append("")
                    lines.append("Ethical Checks:")
                    for check in decision.ethical_checks:
                        lines.append(f"  - {check}")
                
                return "\n".join(lines)
        
        return "Decision not found"
    
    def get_agency_status(self) -> Dict:
        """Get current agency status"""
        return {
            "name": self.name,
            "goals_active": len([g for g in self.goals if g["status"] == "active"]),
            "decisions_made": len(self.decision_history),
            "constraints": [c.value for c, e in self.constraints.items() if e],
            "values": self.values
        }


# Singleton
_agency = None

def get_agency() -> Agency:
    global _agency
    if _agency is None:
        _agency = Agency()
    return _agency
