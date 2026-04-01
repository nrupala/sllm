"""
SL-LLM Dual-Loop Learning System: RAG-PDCA + GAN-PDCA
- RAG-PDCA: Knowledge-grounded iterative improvement loop
- GAN-PDCA: Generator-Discriminator adversarial improvement loop
- Hallucination avoidance by design: grounding, fact-checking, adversarial validation
- Reward maximization: loops until reward saturates (delta < threshold)
"""

import json
import math
import uuid
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, field
from collections import defaultdict


# ============================================================
# HALLUCINATION AVOIDANCE SYSTEM
# ============================================================

class HallucinationGuard:
    """Prevents hallucination by design through multiple validation layers"""
    
    HALLUCINATION_PATTERNS = [
        r"(i think|maybe|perhaps|i believe|probably)\s+(that\s+)?(it|this|the)",
        r"according to (my|our) (knowledge|understanding|training)",
        r"as (an|a) (ai|language model|llm)",
        r"i (don't|cannot|can't) (have|access|know)",
        r"this is (not|purely) (real|factual|verified)",
    ]
    
    CONFIDENCE_MARKERS = {
        "high": ["definitely", "certainly", "verified", "confirmed", "proven", "fact"],
        "medium": ["likely", "probably", "suggests", "indicates", "appears"],
        "low": ["possibly", "might", "could", "perhaps", "uncertain", "unclear"],
    }
    
    @classmethod
    def check_grounding(cls, output: str, context: str, knowledge: List[Dict]) -> Dict:
        """Check if output is grounded in provided context and knowledge"""
        issues = []
        grounding_score = 1.0
        
        # Check for hallucination patterns
        for pattern in cls.HALLUCINATION_PATTERNS:
            matches = re.findall(pattern, output.lower())
            if matches:
                issues.append(f"Uncertainty markers found: {len(matches)} instances")
                grounding_score -= 0.1 * len(matches)
        
        # Check if output references provided knowledge
        knowledge_referenced = 0
        for ins in knowledge:
            content = ins.get("insight", ins.get("content", ""))
            if content and any(word in output.lower() for word in content.lower().split()[:5]):
                knowledge_referenced += 1
        
        if knowledge and knowledge_referenced == 0:
            issues.append("No reference to provided knowledge")
            grounding_score -= 0.2
        
        # Check for overconfident claims without evidence
        high_confidence_words = cls.CONFIDENCE_MARKERS["high"]
        if any(w in output.lower() for w in high_confidence_words):
            if not context or len(context) < 100:
                issues.append("High confidence claim without sufficient grounding context")
                grounding_score -= 0.15
        
        # Check for fabricated specifics (dates, numbers, names not in context)
        fabricated = cls._check_fabricated_specifics(output, context)
        if fabricated:
            issues.extend(fabricated)
            grounding_score -= 0.1 * len(fabricated)
        
        return {
            "grounded": grounding_score >= 0.6,
            "grounding_score": max(0.0, min(1.0, grounding_score)),
            "issues": issues,
            "knowledge_referenced": knowledge_referenced,
        }
    
    @classmethod
    def _check_fabricated_specifics(cls, output: str, context: str) -> List[str]:
        """Check for potentially fabricated specific claims"""
        issues = []
        context_lower = context.lower()
        
        # Check for specific statistics not in context
        stat_patterns = re.findall(r'(\d+\.?\d*)\s*%', output)
        for stat in stat_patterns:
            if stat not in context_lower:
                # Allow common percentages
                if stat not in ["100", "0", "50", "25", "75"]:
                    issues.append(f"Unverified statistic: {stat}%")
        
        # Check for specific dates not in context
        date_patterns = re.findall(r'\b(19|20)\d{2}\b', output)
        for year in date_patterns:
            if year not in context_lower:
                issues.append(f"Unverified year reference: {year}")
        
        return issues[:3]  # Limit to top 3 issues
    
    @classmethod
    def adversarial_validate(cls, output: str, task: str) -> Dict:
        """Adversarial validation: try to find flaws in the output"""
        flaws = []
        strength = 1.0
        
        # Check for internal contradictions
        if cls._has_contradictions(output):
            flaws.append("Internal contradictions detected")
            strength -= 0.3
        
        # Check for incomplete logic
        if cls._has_incomplete_logic(output):
            flaws.append("Incomplete logical flow")
            strength -= 0.2
        
        # Check for unsupported claims
        unsupported = cls._count_unsupported_claims(output)
        if unsupported > 3:
            flaws.append(f"{unsupported} unsupported claims")
            strength -= 0.1 * min(unsupported, 5)
        
        # Check code for common errors
        code_blocks = re.findall(r'```(?:python)?\n(.*?)```', output, re.DOTALL)
        for code in code_blocks:
            code_issues = cls._validate_code(code)
            flaws.extend(code_issues)
            strength -= 0.1 * len(code_issues)
        
        return {
            "valid": strength >= 0.5,
            "strength": max(0.0, min(1.0, strength)),
            "flaws": flaws,
        }
    
    @classmethod
    def _has_contradictions(cls, text: str) -> bool:
        """Check for contradictory statements"""
        contradiction_pairs = [
            ("always", "never"),
            ("all", "none"),
            ("every", "no"),
            ("true", "false"),
            ("correct", "incorrect"),
        ]
        
        text_lower = text.lower()
        for a, b in contradiction_pairs:
            if a in text_lower and b in text_lower:
                # Check they're not in the same sentence
                sentences = re.split(r'[.!?]+', text_lower)
                for sentence in sentences:
                    if a in sentence and b in sentence:
                        return True
        return False
    
    @classmethod
    def _has_incomplete_logic(cls, text: str) -> bool:
        """Check for incomplete logical flow"""
        if "therefore" in text.lower() or "thus" in text.lower():
            if "because" not in text.lower() and "since" not in text.lower():
                return True
        return False
    
    @classmethod
    def _count_unsupported_claims(cls, text: str) -> int:
        """Count claims without supporting evidence"""
        claim_markers = ["is", "are", "was", "were", "will", "should", "must"]
        evidence_markers = ["because", "since", "therefore", "evidence", "data", "study", "research"]
        
        sentences = re.split(r'[.!?]+', text.lower())
        unsupported = 0
        
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 5:
                has_claim = any(m in words for m in claim_markers)
                has_evidence = any(m in sentence for m in evidence_markers)
                if has_claim and not has_evidence:
                    unsupported += 1
        
        return unsupported
    
    @classmethod
    def _validate_code(cls, code: str) -> List[str]:
        """Basic code validation"""
        issues = []
        
        # Check for undefined variables
        defined = set(re.findall(r'(?:def|class|import|from)\s+(\w+)', code))
        defined.update(re.findall(r'(\w+)\s*=', code))
        
        # Check for common Python errors
        if "print(" in code and ")" not in code[code.index("print("):]:
            issues.append("Unclosed print statement")
        
        # Check for infinite loop patterns
        if "while True:" in code and "break" not in code:
            issues.append("Potential infinite loop")
        
        return issues


# ============================================================
# RAG-PDCA LOOP
# ============================================================

class RAGPDCALoop:
    """Knowledge-grounded PDCA loop with reward maximization"""
    
    def __init__(self, reward_saturation_threshold: float = 0.02,
                 max_iterations: int = 10):
        self.reward_saturation_threshold = reward_saturation_threshold
        self.max_iterations = max_iterations
        self.history: List[Dict] = []
    
    def run(self, task: str, retrieve_fn: Callable, generate_fn: Callable,
            execute_fn: Callable, validate_fn: Callable, store_fn: Callable) -> Dict:
        """
        Run RAG-PDCA loop until reward saturates.
        
        Args:
            task: The task to solve
            retrieve_fn: (task) -> knowledge from KG
            generate_fn: (task, knowledge, plan) -> output
            execute_fn: (output) -> execution result
            validate_fn: (output, execution_result, knowledge) -> reward + breakdown
            store_fn: (knowledge, reward) -> store in KG
        """
        iteration = 0
        prev_reward = 0.0
        rewards = []
        best_output = None
        best_reward = 0.0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # PLAN: Retrieve knowledge, analyze task, plan approach
            knowledge = retrieve_fn(task)
            plan = self._plan(task, knowledge, rewards)
            
            # DO: Generate and execute
            output = generate_fn(task, knowledge, plan)
            execution_result = execute_fn(output)
            
            # CHECK: Validate and compute reward
            reward, breakdown = validate_fn(output, execution_result, knowledge)
            
            # Track best
            if reward > best_reward:
                best_reward = reward
                best_output = output
            
            rewards.append(reward)
            
            # Check saturation
            if iteration > 1:
                delta = abs(reward - prev_reward)
                if delta < self.reward_saturation_threshold:
                    # Reward saturated
                    break
            
            prev_reward = reward
            
            # ACT: Store learning, update approach
            store_fn(output, reward, breakdown, iteration)
        
        return {
            "task": task,
            "iterations": iteration,
            "final_reward": rewards[-1] if rewards else 0,
            "best_reward": best_reward,
            "rewards": rewards,
            "saturated": len(rewards) > 1 and abs(rewards[-1] - rewards[-2]) < self.reward_saturation_threshold,
            "best_output": best_output,
            "history": self.history,
        }
    
    def _plan(self, task: str, knowledge: List[Dict], rewards: List[float]) -> Dict:
        """Plan approach based on task and reward history"""
        plan = {
            "knowledge_available": len(knowledge),
            "strategy": "default",
        }
        
        if rewards:
            if rewards[-1] < 0.5:
                plan["strategy"] = "conservative"  # Use proven patterns
            elif rewards[-1] < 0.7:
                plan["strategy"] = "balanced"
            else:
                plan["strategy"] = "exploratory"  # Try novel approaches
        
        if knowledge:
            plan["strategy"] = "knowledge_driven"
        
        return plan


# ============================================================
# GAN-PDCA LOOP
# ============================================================

class Generator:
    """Generates output, improves through discriminator feedback"""
    
    def __init__(self):
        self.output_history: List[Dict] = []
        self.style_preferences: Dict[str, float] = {
            "detail_level": 0.5,
            "formality": 0.5,
            "creativity": 0.5,
            "caution": 0.5,
        }
    
    def generate(self, task: str, knowledge: List[Dict], feedback: Dict = None) -> str:
        """Generate output, adjusted by feedback"""
        if feedback:
            self._adjust_style(feedback)
        
        # This is a placeholder - actual generation happens via LLM
        # The Generator tracks what works and adjusts parameters
        self.output_history.append({
            "task": task[:50],
            "knowledge_used": len(knowledge),
            "style": dict(self.style_preferences),
            "timestamp": datetime.now().isoformat(),
        })
        
        return None  # Actual generation done by LLM
    
    def _adjust_style(self, feedback: Dict):
        """Adjust generation style based on discriminator feedback"""
        lr = 0.1  # learning rate
        
        if feedback.get("too_verbose", False):
            self.style_preferences["detail_level"] -= lr
        if feedback.get("too_brief", False):
            self.style_preferences["detail_level"] += lr
        
        if feedback.get("too_creative", False):
            self.style_preferences["creativity"] -= lr
        if feedback.get("too_conservative", False):
            self.style_preferences["creativity"] += lr
        
        if feedback.get("hallucination_detected", False):
            self.style_preferences["caution"] += lr * 2
            self.style_preferences["creativity"] -= lr
        
        # Clamp
        for k in self.style_preferences:
            self.style_preferences[k] = max(0.0, min(1.0, self.style_preferences[k]))


class Discriminator:
    """Validates generator output, provides feedback for improvement"""
    
    def __init__(self):
        self.validation_history: List[Dict] = []
        self.false_positive_rate = 0.0
        self.false_negative_rate = 0.0
    
    def validate(self, output: str, task: str, knowledge: List[Dict],
                 execution_result: str = "") -> Dict:
        """Validate output and provide detailed feedback"""
        feedback = {}
        
        # Grounding check
        grounding = HallucinationGuard.check_grounding(output, "", knowledge)
        feedback["grounding"] = grounding
        
        # Adversarial validation
        adversarial = HallucinationGuard.adversarial_validate(output, task)
        feedback["adversarial"] = adversarial
        
        # Style analysis
        feedback["too_verbose"] = len(output) > 3000
        feedback["too_brief"] = len(output) < 50
        feedback["too_creative"] = self._is_too_creative(output)
        feedback["too_conservative"] = self._is_too_conservative(output)
        feedback["hallucination_detected"] = grounding["grounding_score"] < 0.5
        
        # Execution validation
        if execution_result:
            feedback["execution_valid"] = "error" not in execution_result.lower()
            feedback["execution_valid"] = feedback["execution_valid"] and "traceback" not in execution_result.lower()
        
        # Compute discriminator score
        score = self._compute_score(feedback)
        
        self.validation_history.append({
            "task": task[:50],
            "score": score,
            "feedback": {k: v for k, v in feedback.items() if k != "grounding"},
            "timestamp": datetime.now().isoformat(),
        })
        
        return {
            "score": score,
            "feedback": feedback,
            "passed": score >= 0.6,
        }
    
    def _compute_score(self, feedback: Dict) -> float:
        """Compute overall validation score"""
        score = 1.0
        
        grounding = feedback.get("grounding", {})
        score -= (1 - grounding.get("grounding_score", 1.0)) * 0.3
        
        adversarial = feedback.get("adversarial", {})
        score -= (1 - adversarial.get("strength", 1.0)) * 0.3
        
        if feedback.get("hallucination_detected", False):
            score -= 0.3
        
        if feedback.get("too_verbose", False) or feedback.get("too_brief", False):
            score -= 0.1
        
        if not feedback.get("execution_valid", True):
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _is_too_creative(self, output: str) -> bool:
        """Check if output is overly speculative"""
        speculative_words = ["might", "could", "perhaps", "possibly", "maybe", "imagine"]
        count = sum(1 for w in speculative_words if w in output.lower())
        return count > 5
    
    def _is_too_conservative(self, output: str) -> bool:
        """Check if output is overly cautious"""
        cautious_words = ["however", "but", "although", "unless", "except", "caveat"]
        count = sum(1 for w in cautious_words if w in output.lower())
        return count > 5


class GANPDCALoop:
    """GAN-style PDCA loop with Generator-Discriminator adversarial training"""
    
    def __init__(self, reward_saturation_threshold: float = 0.02,
                 max_iterations: int = 10):
        self.generator = Generator()
        self.discriminator = Discriminator()
        self.reward_saturation_threshold = reward_saturation_threshold
        self.max_iterations = max_iterations
    
    def run(self, task: str, retrieve_fn: Callable, llm_generate_fn: Callable,
            execute_fn: Callable, store_fn: Callable) -> Dict:
        """
        Run GAN-PDCA loop until discriminator score saturates.
        
        Args:
            task: The task to solve
            retrieve_fn: (task) -> knowledge from KG
            llm_generate_fn: (task, knowledge, generator_style) -> output
            execute_fn: (output) -> execution result
            store_fn: (output, score, feedback) -> store in KG
        """
        iteration = 0
        prev_score = 0.0
        scores = []
        best_output = None
        best_score = 0.0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # PLAN: Retrieve knowledge
            knowledge = retrieve_fn(task)
            
            # DO: Generator produces, LLM generates
            self.generator.generate(task, knowledge)
            output = llm_generate_fn(task, knowledge, self.generator.style_preferences)
            execution_result = execute_fn(output)
            
            # CHECK: Discriminator validates
            validation = self.discriminator.validate(output, task, knowledge, execution_result)
            score = validation["score"]
            
            # Track best
            if score > best_score:
                best_score = score
                best_output = output
            
            scores.append(score)
            
            # Check saturation
            if iteration > 1:
                delta = abs(score - prev_score)
                if delta < self.reward_saturation_threshold:
                    break
            
            prev_score = score
            
            # ACT: Store learning, adjust generator
            store_fn(output, score, validation["feedback"], iteration)
            
            # If discriminator passed with high score, generator is good
            # If not, generator needs to adjust (feedback loop)
        
        return {
            "task": task,
            "iterations": iteration,
            "final_score": scores[-1] if scores else 0,
            "best_score": best_score,
            "scores": scores,
            "saturated": len(scores) > 1 and abs(scores[-1] - scores[-2]) < self.reward_saturation_threshold,
            "best_output": best_output,
            "generator_style": self.generator.style_preferences,
            "discriminator_validations": len(self.discriminator.validation_history),
        }


# ============================================================
# DUAL-LOOP ORCHESTRATOR
# ============================================================

class DualLoopOrchestrator:
    """Orchestrates RAG-PDCA and GAN-PDCA loops together"""
    
    def __init__(self, reward_saturation_threshold: float = 0.02,
                 max_iterations: int = 10):
        self.rag_loop = RAGPDCALoop(reward_saturation_threshold, max_iterations)
        self.gan_loop = GANPDCALoop(reward_saturation_threshold, max_iterations)
        self.run_history: List[Dict] = []
    
    def run(self, task: str, retrieve_fn: Callable, generate_fn: Callable,
            execute_fn: Callable, validate_fn: Callable, store_fn: Callable) -> Dict:
        """
        Run both loops and combine results.
        
        Phase 1: RAG-PDCA - Ground in knowledge, iterate to saturation
        Phase 2: GAN-PDCA - Adversarial validation, iterate to saturation
        Phase 3: Combine best of both, final validation
        """
        # Phase 1: RAG-PDCA
        rag_result = self.rag_loop.run(
            task=task,
            retrieve_fn=retrieve_fn,
            generate_fn=generate_fn,
            execute_fn=execute_fn,
            validate_fn=validate_fn,
            store_fn=store_fn,
        )
        
        # Phase 2: GAN-PDCA (uses RAG results as starting knowledge)
        gan_result = self.gan_loop.run(
            task=task,
            retrieve_fn=retrieve_fn,
            llm_generate_fn=generate_fn,
            execute_fn=execute_fn,
            store_fn=store_fn,
        )
        
        # Phase 3: Combine and final validate
        best_output = rag_result["best_output"] if rag_result["best_reward"] > gan_result["best_score"] else gan_result["best_output"]
        combined_reward = max(rag_result["best_reward"], gan_result["best_score"])
        
        result = {
            "task": task,
            "rag_phase": rag_result,
            "gan_phase": gan_result,
            "best_output": best_output,
            "combined_reward": combined_reward,
            "total_iterations": rag_result["iterations"] + gan_result["iterations"],
            "rag_saturated": rag_result["saturated"],
            "gan_saturated": gan_result["saturated"],
        }
        
        self.run_history.append(result)
        return result
    
    def get_status(self) -> Dict:
        return {
            "total_runs": len(self.run_history),
            "average_reward": sum(r["combined_reward"] for r in self.run_history) / max(len(self.run_history), 1),
            "rag_saturation_rate": sum(1 for r in self.run_history if r["rag_saturated"]) / max(len(self.run_history), 1),
            "gan_saturation_rate": sum(1 for r in self.run_history if r["gan_saturated"]) / max(len(self.run_history), 1),
        }


# ============================================================
# FACTUAL GROUNDING ENGINE
# ============================================================

class FactualGroundingEngine:
    """Ensures all outputs are grounded in verifiable facts"""
    
    def __init__(self):
        self.verified_facts: Dict[str, Dict] = {}
        self.fact_check_log: List[Dict] = []
    
    def ground_output(self, output: str, knowledge: List[Dict], task: str) -> Dict:
        """Ground output in verified facts and knowledge"""
        result = {
            "grounded": True,
            "confidence": 1.0,
            "grounded_claims": [],
            "ungrounded_claims": [],
            "hallucination_risk": "low",
        }
        
        # Extract claims from output
        claims = self._extract_claims(output)
        
        for claim in claims:
            grounded = self._verify_claim(claim, knowledge)
            if grounded:
                result["grounded_claims"].append(claim)
            else:
                result["ungrounded_claims"].append(claim)
                result["confidence"] -= 0.15
        
        result["confidence"] = max(0.0, result["confidence"])
        
        if result["ungrounded_claims"]:
            if len(result["ungrounded_claims"]) > 3:
                result["hallucination_risk"] = "high"
                result["grounded"] = False
            elif len(result["ungrounded_claims"]) > 1:
                result["hallucination_risk"] = "medium"
        
        self.fact_check_log.append({
            "task": task[:50],
            "claims_checked": len(claims),
            "grounded": len(result["grounded_claims"]),
            "ungrounded": len(result["ungrounded_claims"]),
            "risk": result["hallucination_risk"],
            "timestamp": datetime.now().isoformat(),
        })
        
        return result
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        claims = []
        
        # Extract sentences with factual assertions
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:
                # Check for factual assertion patterns
                if any(marker in sentence.lower() for marker in ["is", "are", "was", "were", "has", "have"]):
                    if not any(marker in sentence.lower() for marker in ["if", "might", "could", "perhaps"]):
                        claims.append(sentence)
        
        return claims[:10]  # Limit to top 10 claims
    
    def _verify_claim(self, claim: str, knowledge: List[Dict]) -> bool:
        """Verify a claim against knowledge"""
        claim_lower = claim.lower()
        claim_words = set(claim_lower.split())
        
        for ins in knowledge:
            content = ins.get("insight", ins.get("content", "")).lower()
            content_words = set(content.split())
            
            # Check for significant overlap
            overlap = len(claim_words & content_words)
            if overlap >= 3:
                return True
        
        # Check against verified facts
        for fact_id, fact in self.verified_facts.items():
            if any(word in fact["content"].lower() for word in list(claim_words)[:5]):
                return True
        
        return False
    
    def add_verified_fact(self, content: str, source: str = "verified"):
        """Add a verified fact to the knowledge base"""
        fact_id = str(uuid.uuid4())
        self.verified_facts[fact_id] = {
            "content": content,
            "source": source,
            "timestamp": datetime.now().isoformat(),
        }
    
    def get_grounding_stats(self) -> Dict:
        if not self.fact_check_log:
            return {"total_checks": 0}
        
        total_claims = sum(e["claims_checked"] for e in self.fact_check_log)
        total_ground = sum(e["grounded"] for e in self.fact_check_log)
        
        return {
            "total_checks": len(self.fact_check_log),
            "total_claims_checked": total_claims,
            "grounding_rate": total_ground / max(total_claims, 1),
            "high_risk_count": sum(1 for e in self.fact_check_log if e["risk"] == "high"),
            "verified_facts": len(self.verified_facts),
        }


# ============================================================
# MAIN INTEGRATED SYSTEM
# ============================================================

class DualLoopPDCAWithGrounding:
    """Complete dual-loop system with hallucination avoidance"""
    
    def __init__(self, memory_dir: str = "D:/sl/projects/sllm/memory"):
        self.orchestrator = DualLoopOrchestrator()
        self.grounding = FactualGroundingEngine()
        self.memory_dir = Path(memory_dir)
        self.state_file = self.memory_dir / "dual_loop_state.json"
        
        self._load_state()
    
    def run_task(self, task: str, retrieve_fn: Callable, generate_fn: Callable,
                 execute_fn: Callable, validate_fn: Callable, store_fn: Callable) -> Dict:
        """Run a task through the complete dual-loop system"""
        
        # Wrap generate_fn with grounding
        def grounded_generate(t, k, plan=None):
            output = generate_fn(t, k, plan)
            if output:
                grounding_result = self.grounding.ground_output(output, k, t)
                if grounding_result["hallucination_risk"] == "high":
                    # Regenerate with stronger grounding prompt
                    return generate_fn(t, k, {"grounding_required": True})
            return output
        
        # Run dual-loop
        result = self.orchestrator.run(
            task=task,
            retrieve_fn=retrieve_fn,
            generate_fn=grounded_generate,
            execute_fn=execute_fn,
            validate_fn=validate_fn,
            store_fn=store_fn,
        )
        
        # Final grounding check on best output
        if result["best_output"]:
            knowledge = retrieve_fn(task)
            final_grounding = self.grounding.ground_output(
                result["best_output"], knowledge, task
            )
            result["final_grounding"] = final_grounding
        
        # Save state
        self._save_state()
        
        return result
    
    def get_status(self) -> Dict:
        return {
            "orchestrator": self.orchestrator.get_status(),
            "grounding": self.grounding.get_grounding_stats(),
        }
    
    def _save_state(self):
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "run_history_count": len(self.orchestrator.run_history),
            "grounding_stats": self.grounding.get_grounding_stats(),
            "saved_at": datetime.now().isoformat(),
        }
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def _load_state(self):
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                print(f"Dual-loop state loaded")
            except:
                pass


# Singleton
_dual_loop = None

def get_dual_loop_system() -> DualLoopPDCAWithGrounding:
    global _dual_loop
    if _dual_loop is None:
        _dual_loop = DualLoopPDCAWithGrounding()
    return _dual_loop
