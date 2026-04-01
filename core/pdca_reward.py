"""
SL-LLM PDCA + Reward Learning System
- Plan-Do-Check-Act continuous improvement cycle
- Reward-based weight adjustment for knowledge graph
- Multi-dimensional reward signals (correctness, efficiency, safety, user satisfaction)
- Automatic knowledge graph growth from successful cycles
- Adversarial validation before self-modification
"""

import json
import math
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum


# ============================================================
# PDCA PHASES
# ============================================================

class PDCAPhase(Enum):
    PLAN = "plan"
    DO = "do"
    CHECK = "check"
    ACT = "act"


@dataclass
class PDCAStep:
    phase: PDCAPhase
    action: str
    result: str
    metrics: Dict
    timestamp: str
    success: bool


@dataclass
class PDCACycle:
    id: str
    objective: str
    steps: List[PDCAStep]
    overall_result: str
    reward: float
    knowledge_gained: List[str]
    timestamp: str
    duration_seconds: float = 0.0


# ============================================================
# REWARD DIMENSIONS
# ============================================================

class RewardDimensions:
    """Multi-dimensional reward signals"""
    
    DIMENSIONS = {
        "correctness": {
            "description": "Did the output achieve the goal correctly?",
            "weight": 0.35,
            "indicators": ["tests_passed", "no_errors", "expected_output"],
        },
        "efficiency": {
            "description": "Was it done efficiently (time, resources)?",
            "weight": 0.20,
            "indicators": ["fast_execution", "low_memory", "optimal_algorithm"],
        },
        "safety": {
            "description": "Was it done safely without side effects?",
            "weight": 0.20,
            "indicators": ["no_crashes", "no_data_loss", "secure"],
        },
        "elegance": {
            "description": "Is the solution clean and maintainable?",
            "weight": 0.10,
            "indicators": ["readable", "well_structured", "documented"],
        },
        "learning_value": {
            "description": "Did this produce reusable knowledge?",
            "weight": 0.15,
            "indicators": ["new_insight", "pattern_recognized", "generalizable"],
        },
    }
    
    @classmethod
    def compute_reward(cls, scores: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        """Compute weighted reward from dimension scores (0.0-1.0 each)"""
        total = 0.0
        total_weight = 0.0
        breakdown = {}
        
        for dim_name, dim_info in cls.DIMENSIONS.items():
            score = scores.get(dim_name, 0.0)
            weight = dim_info["weight"]
            breakdown[dim_name] = score
            total += score * weight
            total_weight += weight
        
        if total_weight > 0:
            total /= total_weight
        
        return min(1.0, max(0.0, total)), breakdown


# ============================================================
# REWARD MEMORY
# ============================================================

class RewardMemory:
    """Stores and analyzes reward history for learning"""
    
    def __init__(self, max_entries: int = 500):
        self.entries: List[Dict] = []
        self.max_entries = max_entries
        self.trend_window = 20
    
    def record(self, task: str, reward: float, breakdown: Dict,
               phase_results: Dict, knowledge_extracted: List[str]):
        """Record a reward entry"""
        entry = {
            "id": str(uuid.uuid4()),
            "task": task[:100],
            "reward": reward,
            "breakdown": breakdown,
            "phase_results": phase_results,
            "knowledge_extracted": knowledge_extracted,
            "timestamp": datetime.now().isoformat(),
        }
        self.entries.append(entry)
        
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
    
    def get_average_reward(self, window: int = None) -> float:
        """Get average reward over recent window"""
        w = window or self.trend_window
        recent = self.entries[-w:]
        if not recent:
            return 0.5
        return sum(e["reward"] for e in recent) / len(recent)
    
    def get_trend(self) -> str:
        """Get reward trend direction"""
        if len(self.entries) < 4:
            return "insufficient_data"
        
        half = len(self.entries) // 2
        first_half = sum(e["reward"] for e in self.entries[:half]) / half
        second_half = sum(e["reward"] for e in self.entries[half:]) / (len(self.entries) - half)
        
        diff = second_half - first_half
        if diff > 0.05:
            return "improving"
        elif diff < -0.05:
            return "declining"
        return "stable"
    
    def get_weakest_dimension(self) -> str:
        """Find the weakest reward dimension"""
        if not self.entries:
            return "unknown"
        
        dim_totals = defaultdict(float)
        dim_counts = defaultdict(int)
        
        for entry in self.entries[-self.trend_window:]:
            for dim, score in entry.get("breakdown", {}).items():
                dim_totals[dim] += score
                dim_counts[dim] += 1
        
        if not dim_totals:
            return "unknown"
        
        dim_averages = {dim: total / dim_counts[dim] for dim, total in dim_totals.items()}
        return min(dim_averages, key=dim_averages.get)
    
    def get_strongest_dimension(self) -> str:
        """Find the strongest reward dimension"""
        if not self.entries:
            return "unknown"
        
        dim_totals = defaultdict(float)
        dim_counts = defaultdict(int)
        
        for entry in self.entries[-self.trend_window:]:
            for dim, score in entry.get("breakdown", {}).items():
                dim_totals[dim] += score
                dim_counts[dim] += 1
        
        if not dim_totals:
            return "unknown"
        
        dim_averages = {dim: total / dim_counts[dim] for dim, total in dim_totals.items()}
        return max(dim_averages, key=dim_averages.get)
    
    def get_top_learned_patterns(self, limit: int = 5) -> List[str]:
        """Get most frequently extracted knowledge patterns"""
        pattern_counts = defaultdict(int)
        for entry in self.entries:
            for pattern in entry.get("knowledge_extracted", []):
                pattern_counts[pattern] += 1
        
        sorted_patterns = sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)
        return [p for p, _ in sorted_patterns[:limit]]
    
    def get_stats(self) -> Dict:
        """Get comprehensive reward statistics"""
        if not self.entries:
            return {"total_entries": 0}
        
        rewards = [e["reward"] for e in self.entries]
        recent_rewards = [e["reward"] for e in self.entries[-self.trend_window:]]
        
        return {
            "total_entries": len(self.entries),
            "average_reward": sum(rewards) / len(rewards),
            "recent_average": sum(recent_rewards) / len(recent_rewards) if recent_rewards else 0,
            "min_reward": min(rewards),
            "max_reward": max(rewards),
            "trend": self.get_trend(),
            "weakest_dimension": self.get_weakest_dimension(),
            "strongest_dimension": self.get_strongest_dimension(),
            "top_patterns": self.get_top_learned_patterns(),
        }
    
    def to_dict(self) -> Dict:
        return {
            "entries": self.entries[-100:],
            "stats": self.get_stats(),
        }


# ============================================================
# PDCA ENGINE
# ============================================================

class PDCAEngine:
    """Plan-Do-Check-Act continuous improvement engine"""
    
    def __init__(self, reward_memory: RewardMemory = None):
        self.reward_memory = reward_memory or RewardMemory()
        self.active_cycles: List[PDCACycle] = []
        self.completed_cycles: List[PDCACycle] = []
        self.improvement_log: List[Dict] = []
    
    def start_cycle(self, objective: str) -> str:
        """Start a new PDCA cycle"""
        cycle_id = str(uuid.uuid4())
        cycle = PDCACycle(
            id=cycle_id,
            objective=objective,
            steps=[],
            overall_result="in_progress",
            reward=0.0,
            knowledge_gained=[],
            timestamp=datetime.now().isoformat(),
        )
        self.active_cycles.append(cycle)
        return cycle_id
    
    def plan(self, cycle_id: str, task: str, context: Dict) -> Dict:
        """PLAN: Analyze task, identify approach, set success criteria"""
        cycle = self._get_cycle(cycle_id)
        if not cycle:
            return {"error": "Cycle not found"}
        
        # Analyze task complexity
        complexity = self._assess_complexity(task)
        
        # Identify potential risks
        risks = self._identify_risks(task)
        
        # Set success criteria
        success_criteria = self._define_success_criteria(task, complexity)
        
        # Select strategy based on reward history
        strategy = self._select_strategy(task, context)
        
        plan = {
            "task": task,
            "complexity": complexity,
            "risks": risks,
            "success_criteria": success_criteria,
            "strategy": strategy,
            "estimated_iterations": min(5, max(2, complexity * 2)),
        }
        
        step = PDCAStep(
            phase=PDCAPhase.PLAN,
            action=f"Planned approach: {strategy}",
            result=json.dumps(plan),
            metrics={"complexity": complexity, "risks_count": len(risks)},
            timestamp=datetime.now().isoformat(),
            success=True,
        )
        cycle.steps.append(step)
        
        return plan
    
    def do(self, cycle_id: str, execution_result: Dict) -> Dict:
        """DO: Execute the plan and capture results"""
        cycle = self._get_cycle(cycle_id)
        if not cycle:
            return {"error": "Cycle not found"}
        
        success = execution_result.get("success", False)
        output = execution_result.get("output", "")
        elapsed = execution_result.get("elapsed", 0)
        
        step = PDCAStep(
            phase=PDCAPhase.DO,
            action="Executed task",
            result=output[:500] if output else "No output",
            metrics={
                "success": success,
                "elapsed": elapsed,
                "output_length": len(output),
            },
            timestamp=datetime.now().isoformat(),
            success=success,
        )
        cycle.steps.append(step)
        
        return {
            "executed": True,
            "success": success,
            "elapsed": elapsed,
        }
    
    def check(self, cycle_id: str, output: str, expected: str = "",
              execution_output: str = "") -> Dict:
        """CHECK: Evaluate results against success criteria"""
        cycle = self._get_cycle(cycle_id)
        if not cycle:
            return {"error": "Cycle not found"}
        
        # Evaluate correctness
        correctness = self._evaluate_correctness(output, expected, execution_output)
        
        # Evaluate efficiency
        do_step = next((s for s in cycle.steps if s.phase == PDCAPhase.DO), None)
        elapsed = do_step.metrics.get("elapsed", 0) if do_step else 0
        efficiency = self._evaluate_efficiency(elapsed, len(output))
        
        # Evaluate safety
        safety = self._evaluate_safety(output, execution_output)
        
        # Evaluate elegance
        elegance = self._evaluate_elegance(output)
        
        # Evaluate learning value
        learning_value = self._evaluate_learning_value(output, cycle.objective)
        
        # Compute overall reward
        scores = {
            "correctness": correctness,
            "efficiency": efficiency,
            "safety": safety,
            "elegance": elegance,
            "learning_value": learning_value,
        }
        reward, breakdown = RewardDimensions.compute_reward(scores)
        
        # Record in reward memory
        self.reward_memory.record(
            task=cycle.objective,
            reward=reward,
            breakdown=breakdown,
            phase_results={s.phase.value: s.success for s in cycle.steps},
            knowledge_extracted=self._extract_knowledge(output, cycle.objective),
        )
        
        check_result = {
            "scores": scores,
            "reward": reward,
            "breakdown": breakdown,
            "passed": reward >= 0.6,
            "needs_improvement": reward < 0.6,
        }
        
        step = PDCAStep(
            phase=PDCAPhase.CHECK,
            action="Evaluated results",
            result=f"Reward: {reward:.2f}, Passed: {check_result['passed']}",
            metrics=scores,
            timestamp=datetime.now().isoformat(),
            success=check_result["passed"],
        )
        cycle.steps.append(step)
        cycle.reward = reward
        
        return check_result
    
    def act(self, cycle_id: str, check_result: Dict) -> Dict:
        """ACT: Apply improvements based on check results"""
        cycle = self._get_cycle(cycle_id)
        if not cycle:
            return {"error": "Cycle not found"}
        
        passed = check_result.get("passed", False)
        weakest = check_result.get("breakdown", {})
        
        if passed:
            # Success: consolidate knowledge, reinforce successful patterns
            action = "consolidate"
            improvements = self._consolidate_learning(cycle, check_result)
            cycle.overall_result = "success"
        else:
            # Failure: identify root cause, plan improvement
            action = "improve"
            improvements = self._plan_improvement(cycle, check_result)
            cycle.overall_result = "needs_improvement"
        
        step = PDCAStep(
            phase=PDCAPhase.ACT,
            action=f"Applied {action} based on reward {cycle.reward:.2f}",
            result=json.dumps(improvements),
            metrics={"action": action, "reward": cycle.reward},
            timestamp=datetime.now().isoformat(),
            success=passed,
        )
        cycle.steps.append(step)
        
        # Calculate duration
        try:
            start = datetime.fromisoformat(cycle.timestamp)
            end = datetime.fromisoformat(step.timestamp)
            cycle.duration_seconds = (end - start).total_seconds()
        except:
            pass
        
        # Move to completed
        if cycle in self.active_cycles:
            self.active_cycles.remove(cycle)
        self.completed_cycles.append(cycle)
        
        # Log improvement
        self.improvement_log.append({
            "cycle_id": cycle.id,
            "objective": cycle.objective,
            "result": cycle.overall_result,
            "reward": cycle.reward,
            "improvements": improvements,
            "timestamp": datetime.now().isoformat(),
        })
        
        return {
            "action": action,
            "improvements": improvements,
            "cycle_complete": True,
            "reward": cycle.reward,
        }
    
    def execute_full_cycle(self, task: str, execute_fn, context: Dict = None) -> Dict:
        """Execute a complete PDCA cycle with automatic progression"""
        context = context or {}
        
        # PLAN
        cycle_id = self.start_cycle(task)
        plan = self.plan(cycle_id, task, context)
        
        # DO
        execution_result = execute_fn(task, plan)
        do_result = self.do(cycle_id, execution_result)
        
        # CHECK
        output = execution_result.get("output", "")
        exec_output = execution_result.get("execution_output", "")
        check_result = self.check(cycle_id, output, execution_output=exec_output)
        
        # ACT
        act_result = self.act(cycle_id, check_result)
        
        # Get the completed cycle
        cycle = next((c for c in self.completed_cycles if c.id == cycle_id), None)
        
        return {
            "cycle_id": cycle_id,
            "plan": plan,
            "execution": do_result,
            "check": check_result,
            "act": act_result,
            "reward": cycle.reward if cycle else 0,
            "knowledge_gained": cycle.knowledge_gained if cycle else [],
        }
    
    # --- Internal methods ---
    
    def _get_cycle(self, cycle_id: str) -> Optional[PDCACycle]:
        for cycle in self.active_cycles:
            if cycle.id == cycle_id:
                return cycle
        return None
    
    def _assess_complexity(self, task: str) -> float:
        """Assess task complexity (1-5 scale)"""
        task_lower = task.lower()
        complexity = 1.0
        
        complexity_keywords = {
            2: ["function", "script", "simple", "basic"],
            3: ["algorithm", "class", "system", "module"],
            4: ["architecture", "framework", "distributed", "concurrent"],
            5: ["compiler", "operating system", "distributed system", "ml pipeline"],
        }
        
        for level, keywords in complexity_keywords.items():
            if any(kw in task_lower for kw in keywords):
                complexity = max(complexity, level)
        
        # Length factor
        word_count = len(task.split())
        if word_count > 30:
            complexity = min(5, complexity + 0.5)
        
        return complexity
    
    def _identify_risks(self, task: str) -> List[str]:
        """Identify potential risks in the task"""
        risks = []
        task_lower = task.lower()
        
        risk_patterns = {
            "security_risk": ["password", "token", "secret", "auth", "credential"],
            "data_loss_risk": ["delete", "drop", "remove", "destroy", "truncate"],
            "performance_risk": ["large", "million", "billion", "real-time", "streaming"],
            "complexity_risk": ["recursive", "concurrent", "async", "distributed"],
            "dependency_risk": ["external", "api", "third-party", "library"],
        }
        
        for risk_name, keywords in risk_patterns.items():
            if any(kw in task_lower for kw in keywords):
                risks.append(risk_name)
        
        return risks
    
    def _define_success_criteria(self, task: str, complexity: float) -> List[str]:
        """Define what success looks like for this task"""
        criteria = ["produces_valid_output", "no_errors"]
        
        if complexity >= 3:
            criteria.extend(["well_structured", "documented"])
        if complexity >= 4:
            criteria.extend(["efficient", "scalable"])
        if complexity >= 5:
            criteria.extend(["tested", "robust"])
        
        return criteria
    
    def _select_strategy(self, task: str, context: Dict) -> str:
        """Select approach strategy based on reward history"""
        weakest = self.reward_memory.get_weakest_dimension()
        
        strategy_map = {
            "correctness": "test_driven",
            "efficiency": "optimize_first",
            "safety": "defensive_programming",
            "elegance": "clean_code",
            "learning_value": "document_everything",
        }
        
        return strategy_map.get(weakest, "balanced_approach")
    
    def _evaluate_correctness(self, output: str, expected: str, exec_output: str) -> float:
        """Evaluate output correctness"""
        score = 0.5  # baseline
        
        # Check for error indicators
        error_indicators = ["error", "traceback", "exception", "failed", "crash"]
        has_errors = any(ind in exec_output.lower() for ind in error_indicators)
        
        if has_errors:
            score -= 0.3
        else:
            score += 0.3
        
        # Check for code quality indicators
        if "def " in output or "class " in output or "function " in output:
            score += 0.1
        
        # Check for completeness
        if len(output) > 100:
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _evaluate_efficiency(self, elapsed: float, output_length: int) -> float:
        """Evaluate execution efficiency"""
        score = 0.5
        
        if elapsed < 5:
            score += 0.3
        elif elapsed < 15:
            score += 0.1
        elif elapsed > 60:
            score -= 0.2
        
        # Reasonable output length
        if 50 <= output_length <= 5000:
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _evaluate_safety(self, output: str, exec_output: str) -> float:
        """Evaluate safety of the output"""
        score = 0.8  # baseline high
        
        danger_patterns = [
            "os.system(", "subprocess.call(", "rm -rf", "DROP TABLE",
            "DELETE FROM", "eval(", "exec(", "__import__",
        ]
        
        for pattern in danger_patterns:
            if pattern in output:
                score -= 0.2
        
        if "error" in exec_output.lower() or "traceback" in exec_output.lower():
            score -= 0.1
        
        return min(1.0, max(0.0, score))
    
    def _evaluate_elegance(self, output: str) -> float:
        """Evaluate code elegance and structure"""
        score = 0.5
        
        # Check for good practices
        good_practices = [
            "def ", "class ", "# ", "return", "if ", "for ", "try:",
            "with ", "import", "from ",
        ]
        
        practice_count = sum(1 for p in good_practices if p in output)
        if practice_count >= 3:
            score += 0.2
        if practice_count >= 5:
            score += 0.1
        
        # Check for code blocks
        if "```" in output:
            score += 0.1
        
        return min(1.0, max(0.0, score))
    
    def _evaluate_learning_value(self, output: str, objective: str) -> float:
        """Evaluate how much reusable knowledge was produced"""
        score = 0.3  # baseline
        
        # Check for explanatory content
        explanatory_indicators = [
            "because", "therefore", "this means", "in other words",
            "note that", "important", "remember", "key point",
        ]
        
        explanation_count = sum(1 for ind in explanatory_indicators if ind in output.lower())
        if explanation_count >= 2:
            score += 0.3
        if explanation_count >= 4:
            score += 0.2
        
        # Check for reusable patterns
        if "def " in output and len(output) > 200:
            score += 0.2
        
        return min(1.0, max(0.0, score))
    
    def _extract_knowledge(self, output: str, objective: str) -> List[str]:
        """Extract knowledge patterns from output"""
        patterns = []
        
        # Extract function definitions as patterns
        import re
        functions = re.findall(r'def\s+(\w+)', output)
        for func in functions:
            patterns.append(f"function_pattern:{func}")
        
        # Extract concepts
        if "algorithm" in output.lower():
            patterns.append("algorithm_used")
        if "class " in output:
            patterns.append("oop_pattern")
        if "try:" in output:
            patterns.append("error_handling")
        
        return patterns
    
    def _consolidate_learning(self, cycle: PDCACycle, check_result: Dict) -> Dict:
        """Consolidate learning from successful cycle"""
        improvements = {
            "knowledge_extracted": cycle.reward > 0.7,
            "pattern_reinforced": True,
            "confidence_boost": min(0.1, cycle.reward * 0.1),
        }
        
        # Extract knowledge for knowledge graph
        cycle.knowledge_gained = self._extract_knowledge(
            next((s.result for s in cycle.steps if s.phase == PDCAPhase.DO), ""),
            cycle.objective,
        )
        
        return improvements
    
    def _plan_improvement(self, cycle: PDCACycle, check_result: Dict) -> Dict:
        """Plan improvements for failed cycle"""
        weakest_dim = min(check_result.get("breakdown", {}),
                         key=check_result.get("breakdown", {}).get,
                         default="correctness")
        
        improvements = {
            "root_cause": f"Weak in {weakest_dim}",
            "next_strategy": {
                "correctness": "Add validation and testing",
                "efficiency": "Profile and optimize bottlenecks",
                "safety": "Add defensive checks",
                "elegance": "Refactor for clarity",
                "learning_value": "Add explanations and documentation",
            }.get(weakest_dim, "General improvement"),
            "retry_recommended": True,
        }
        
        return improvements
    
    def get_status(self) -> Dict:
        """Get PDCA engine status"""
        return {
            "active_cycles": len(self.active_cycles),
            "completed_cycles": len(self.completed_cycles),
            "reward_stats": self.reward_memory.get_stats(),
            "improvement_log_count": len(self.improvement_log),
        }
    
    def save(self, filepath: str):
        """Save PDCA state"""
        data = {
            "completed_cycles": [
                {
                    "id": c.id,
                    "objective": c.objective,
                    "overall_result": c.overall_result,
                    "reward": c.reward,
                    "knowledge_gained": c.knowledge_gained,
                    "timestamp": c.timestamp,
                    "duration_seconds": c.duration_seconds,
                }
                for c in self.completed_cycles[-50:]
            ],
            "reward_memory": self.reward_memory.to_dict(),
            "improvement_log": self.improvement_log[-50:],
            "saved_at": datetime.now().isoformat(),
        }
        
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)


# ============================================================
# KNOWLEDGE GRAPH GROWTH MANAGER
# ============================================================

class KnowledgeGraphGrowthManager:
    """Manages knowledge graph growth from PDCA cycles"""
    
    def __init__(self, kg_manager=None):
        self.kg_manager = kg_manager
        self.growth_log: List[Dict] = []
    
    def process_cycle_result(self, cycle_result: Dict) -> Dict:
        """Process a PDCA cycle result and grow the knowledge graph"""
        reward = cycle_result.get("reward", 0)
        knowledge = cycle_result.get("knowledge_gained", [])
        objective = cycle_result.get("plan", {}).get("task", "")
        
        growth_actions = []
        
        if reward >= 0.7:
            # High reward: add as proven pattern
            growth_actions.append({
                "action": "add_pattern",
                "content": f"Proven: {objective[:80]}",
                "category": "pattern",
                "confidence": reward,
            })
        
        if reward >= 0.5:
            # Medium reward: add as insight
            growth_actions.append({
                "action": "add_insight",
                "content": f"Learned from {objective[:80]} (reward: {reward:.2f})",
                "category": "insight",
                "confidence": reward,
            })
        
        if reward < 0.5:
            # Low reward: add as lesson learned
            growth_actions.append({
                "action": "add_lesson",
                "content": f"Lesson from {objective[:80]}: needs improvement in {cycle_result.get('check', {}).get('breakdown', {})}",
                "category": "lesson",
                "confidence": 1.0 - reward,
            })
        
        # Add knowledge patterns
        for pattern in knowledge:
            growth_actions.append({
                "action": "add_pattern",
                "content": f"Pattern: {pattern}",
                "category": "code_pattern",
                "confidence": 0.8,
            })
        
        self.growth_log.append({
            "objective": objective,
            "reward": reward,
            "actions": growth_actions,
            "timestamp": datetime.now().isoformat(),
        })
        
        return {
            "growth_actions": growth_actions,
            "knowledge_added": len(growth_actions),
        }
    
    def get_growth_stats(self) -> Dict:
        """Get knowledge growth statistics"""
        if not self.growth_log:
            return {"total_growth_events": 0}
        
        total_actions = sum(len(g["actions"]) for g in self.growth_log)
        avg_reward = sum(g["reward"] for g in self.growth_log) / len(self.growth_log)
        
        return {
            "total_growth_events": len(self.growth_log),
            "total_knowledge_added": total_actions,
            "average_reward": avg_reward,
            "recent_events": self.growth_log[-10:],
        }


# ============================================================
# MAIN PDCA + REWARD SYSTEM
# ============================================================

class PDCAPlusRewardSystem:
    """Unified PDCA cycle with reward-based learning"""
    
    def __init__(self, memory_dir: str = "D:/sl/projects/sllm/memory"):
        self.reward_memory = RewardMemory()
        self.pdca_engine = PDCAEngine(self.reward_memory)
        self.kg_growth = KnowledgeGraphGrowthManager()
        self.memory_dir = Path(memory_dir)
        self.state_file = self.memory_dir / "pdca_reward_state.json"
        
        # Load existing state
        self._load_state()
    
    def run_cycle(self, task: str, execute_fn, context: Dict = None) -> Dict:
        """Run a complete PDCA + Reward cycle"""
        # Execute PDCA cycle
        cycle_result = self.pdca_engine.execute_full_cycle(task, execute_fn, context)
        
        # Process knowledge graph growth
        growth_result = self.kg_growth.process_cycle_result(cycle_result)
        
        # Save state
        self._save_state()
        
        return {
            "cycle": cycle_result,
            "growth": growth_result,
            "reward_stats": self.reward_memory.get_stats(),
        }
    
    def get_status(self) -> Dict:
        """Get complete system status"""
        return {
            "pdca": self.pdca_engine.get_status(),
            "rewards": self.reward_memory.get_stats(),
            "knowledge_growth": self.kg_growth.get_growth_stats(),
        }
    
    def _save_state(self):
        """Save system state"""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.pdca_engine.save(str(self.state_file))
    
    def _load_state(self):
        """Load system state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                
                # Restore reward memory
                if "reward_memory" in data and "entries" in data["reward_memory"]:
                    self.reward_memory.entries = data["reward_memory"]["entries"]
                
                # Restore completed cycles
                if "completed_cycles" in data:
                    for cycle_data in data["completed_cycles"]:
                        cycle = PDCACycle(
                            id=cycle_data["id"],
                            objective=cycle_data["objective"],
                            steps=[],
                            overall_result=cycle_data["overall_result"],
                            reward=cycle_data["reward"],
                            knowledge_gained=cycle_data.get("knowledge_gained", []),
                            timestamp=cycle_data["timestamp"],
                            duration_seconds=cycle_data.get("duration_seconds", 0),
                        )
                        self.pdca_engine.completed_cycles.append(cycle)
                
                # Restore improvement log
                if "improvement_log" in data:
                    self.pdca_engine.improvement_log = data["improvement_log"]
                
                print(f"PDCA+Reward state loaded: {len(self.reward_memory.entries)} entries")
            except Exception as e:
                print(f"Could not load PDCA state: {e}")


# Singleton
_pdca_system = None

def get_pdca_system() -> PDCAPlusRewardSystem:
    global _pdca_system
    if _pdca_system is None:
        _pdca_system = PDCAPlusRewardSystem()
    return _pdca_system
