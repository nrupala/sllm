"""
SL-LLM Entry Point with Full Cognitive Integration
- Knowledge Graph RAG
- Design Pattern Recognition
- Agentification  
- Agency with Reasoning Trace
- Sentient Thinking
- Thinking Toolbox (Psychology, Logic, Graph Theory, etc.)
Usage: python run.py [--test] [--prefer=lmstudio|ollama|mock] [--verbose]
"""

import sys
import json
import time
from pathlib import Path
from typing import Tuple, Dict

# Parse arguments
prefer = "auto"
verbose = False

for arg in sys.argv:
    if arg.startswith("--prefer="):
        prefer = arg.split("=")[1]
    if arg == "--verbose" or arg == "-v":
        verbose = True

from core.client import get_client
llm_client = get_client(prefer=prefer)

from tools.builtin import get_default_tools, execute_tool
from knowledge_graph_manager import FluidKnowledgeGraph, get_enhanced_context

# New cognitive systems
from core.thinking_engine import get_reasoning_engine
from core.pattern_recognition import get_pattern_recognizer
from core.agentification import get_coding_team, get_self_improvement_team
from core.agency import get_agency, DecisionType
from core.sentient_thinking import get_sentient_thinking, ThoughtType


class SelfLearningLLM:
    def __init__(self, model="qwen2.5-coder", verbose=False):
        self.model = model
        self.client = llm_client
        self.tools = get_default_tools()
        self.verbose = verbose
        self.kgm = FluidKnowledgeGraph()
        
        # Initialize cognitive systems
        self.reasoning = get_reasoning_engine()
        self.patterns = get_pattern_recognizer()
        self.coding_team = get_coding_team()
        self.self_improvement_team = get_self_improvement_team()
        self.agency = get_agency()
        self.sentient = get_sentient_thinking()
        
        # Set up agency
        self.agency.add_value("accuracy", 0.8)
        self.agency.add_value("efficiency", 0.6)
        self.agency.add_value("safety", 0.9)
        
        stats = self.kgm._get_category_counts()
        
        print(f"SL-LLM initialized with {self.model}")
        print(f"Tools: {[t['function']['name'] for t in self.tools]}")
        print(f"Knowledge Graph: {stats.get('bug_fix', 0)} bugs, {stats.get('performance', 0)} optimizations stored")
        print(f"Cognitive Systems: Reasoning, Patterns, Agentification, Agency, Sentient Thinking")
        if self.verbose:
            print("[VERBOSE MODE: ON]")

    def _verbose_print(self, phase: str, message: str, details=None):
        if self.verbose:
            print(f"\n{'='*50}")
            print(f"[THINKING] {phase}")
            print(f"{'='*50}")
            print(f"  {message}")
            if details:
                print(f"  Details: {str(details)[:200]}")
            print()

    def execute_task(self, task: str, max_iterations: int = 5) -> Dict:
        self._verbose_print("RECEIVING TASK", task)
        
        # === SENTIENT THINKING: Process incoming task ===
        self.sentient.think(task, ThoughtType.PERCEPTION)
        
        # === THINKING TOOLBOX: Multi-disciplinary reasoning ===
        reasoning_result = self.reasoning.reason(task)
        self._verbose_print("REASONING", f"Lateral perspectives: {len(reasoning_result.get('lateral_perspectives', []))}")
        
        # === AGENCY: Make decision on approach ===
        options = [
            {"name": "direct_execution", "score": 0.7, "pros": ["fast"], "cons": ["may miss edge cases"]},
            {"name": "reasoned_approach", "score": 0.8, "pros": ["thorough"], "cons": ["slower"]},
            {"name": "pattern_matching", "score": 0.6, "pros": ["proven patterns"], "cons": ["may not fit"]}
        ]
        decision = self.agency.make_decision(task, options)
        self._verbose_print("AGENCY DECISION", f"Chose: {decision.chosen_option.get('name')}, Confidence: {decision.confidence:.0%}")
        
        # === DESIGN PATTERN RECOGNITION ===
        pattern_suggestion = self.patterns.suggest_pattern(task)
        if pattern_suggestion:
            self._verbose_print("PATTERNS", f"Suggested: {[p['name'] for p in pattern_suggestion.get('suggested_patterns', [])]}")
        
        # Get enhanced knowledge graph context
        self._verbose_print("KNOWLEDGE GRAPH", "Analyzing and retrieving relevant memories...")
        
        enhanced_context, kg_metadata = get_enhanced_context(task)
        
        classification = kg_metadata.get("classification", {})
        context_info = kg_metadata.get("context", {})
        
        self._verbose_print("KNOWLEDGE GRAPH", 
            f"Classified as: {classification.get('primary_category', 'general')}, "
            f"Contexts: {classification.get('contexts', [])}, "
            f"Insights: {kg_metadata.get('insights_retrieved', 0)}")
        
        start = time.time()
        
        for i in range(max_iterations):
            self._verbose_print(f"ITERATION {i+1}", f"Processing task...")
            
            try:
                full_prompt = f"{enhanced_context}\n\nUser: {task}"
                self._verbose_print("CALLING LLM", f"Sending task + classified context to model")
                response = self.client.chat(
                    [{"role": "user", "content": full_prompt}], 
                    tools=self.tools
                )
            except Exception as e:
                return {"success": False, "error": str(e), "elapsed": time.time()-start}
            
            msg = response.get("message", {})
            
            # Handle tool calls
            if msg.get("tool_calls"):
                for call in msg["tool_calls"]:
                    tool_name = call["function"]["name"]
                    try:
                        args = json.loads(call["function"]["arguments"])
                    except:
                        args = {"code": call["function"]["arguments"]}
                    
                    self._verbose_print("TOOL CALL", f"Using tool: {tool_name}", args)
                    result = execute_tool(tool_name, args)
                    self._verbose_print("TOOL RESULT", f"Tool: {tool_name}", result[:100])
                    
                    try:
                        self._verbose_print("REFINING", "Sending tool result back to LLM")
                        response = self.client.chat(
                            [{"role": "user", "content": full_prompt}, 
                             msg,
                             {"role": "tool", "content": result, "tool_call_id": call.get("id", "call")}],
                            tools=self.tools
                        )
                    except Exception as e:
                        return {"success": False, "error": str(e)}
                    msg = response.get("message", {})
            
            # Return text response
            out = msg.get("content", "")
            if out:
                self._verbose_print("GENERATING RESPONSE", 
                    f"Producing output ({len(out)} chars), Category: {classification.get('primary_category', 'general')}")
                return {
                    "success": True, 
                    "output": out, 
                    "elapsed": time.time()-start,
                    "knowledge_used": kg_metadata.get('insights_retrieved', 0),
                    "classification": classification.get('primary_category', 'general')
                }
        
        return {"success": False, "output": "Max iterations", "elapsed": time.time()-start}

    def run_self_learning_cycle(self, task: str) -> Dict:
        """Complete self-learning cycle with reflection"""
        
        self._verbose_print("SELF-LEARNING CYCLE", "Starting self-improvement loop with KG context")
        
        result = self.execute_task(task)
        
        # Execute code check
        self._verbose_print("STEP 2: EXECUTE", "Testing the generated code")
        if "```python" in result.get("output", ""):
            code = result["output"].split("```python")[1].split("```")[0] if "```python" in result["output"] else result["output"]
            exec_result = execute_tool("execute_code", {"code": code, "timeout": 10})
            self._verbose_print("EXECUTION RESULT", exec_result[:150])
            
            if "Error" in exec_result or "Traceback" in exec_result:
                self._verbose_print("STEP 3: REFLECT", "Detected error - using KG context for fix")
        
        return result

    def interactive(self):
        print("\nSL-LLM Interactive (type 'exit' to quit)")
        print("Commands: 'verbose on/off', 'kg stats', 'classify <text>'")
        
        while True:
            try:
                task = input(">> ")
                if task.lower() == "exit":
                    break
                if task.lower() == "verbose on":
                    self.verbose = True
                    print("[VERBOSE MODE: ON]")
                    continue
                if task.lower() == "verbose off":
                    self.verbose = False
                    print("[VERBOSE MODE: OFF]")
                    continue
                if task.lower() == "kg stats":
                    counts = self.kgm._get_category_counts()
                    print(f"Knowledge categories: {counts}")
                    continue
                if task.lower().startswith("classify "):
                    text = task[9:]
                    from knowledge_graph_manager import KnowledgeClassifier
                    result = KnowledgeClassifier.classify(text)
                    print(f"Classification: {result}")
                    continue
                
                result = self.execute_task(task)
                output = result.get('output', 'No output')
                # Print full output without truncation
                print(f"\n[Knowledge: {result.get('knowledge_used', 0)} insights, Type: {result.get('classification', 'general')}]")
                print(output)
                print()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    sllm = SelfLearningLLM(verbose=verbose)
    
    if "--test" in sys.argv:
        result = sllm.execute_task("Write a fibonacci function in Python")
        print(f"\n[Used {result.get('knowledge_used', 0)} insights, Type: {result.get('classification', 'general')}]")
        print(result.get('output', 'No output'))
    else:
        sllm.interactive()

if __name__ == "__main__":
    main()