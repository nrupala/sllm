"""
SL-LLM Entry Point
Usage: python run.py [--test] [--prefer=lmstudio|ollama|mock] [--verbose]
"""

import sys

import json
import time
from pathlib import Path

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


class SelfLearningLLM:
    def __init__(self, model="qwen2.5-coder", verbose=False):
        self.model = model
        self.client = llm_client
        self.tools = get_default_tools()
        self.verbose = verbose
        
        print(f"SL-LLM initialized with {self.model}")
        print(f"Tools: {[t['function']['name'] for t in self.tools]}")
        if self.verbose:
            print("[VERBOSE MODE: ON]")

    def _verbose_print(self, phase, message, details=None):
        if self.verbose:
            print(f"\n{'='*50}")
            print(f"[THINKING] {phase}")
            print(f"{'='*50}")
            print(f"  {message}")
            if details:
                print(f"  Details: {str(details)[:200]}")
            print()

    def execute_task(self, task, max_iterations=5):
        self._verbose_print("RECEIVING TASK", task)
        
        start = time.time()
        
        for i in range(max_iterations):
            self._verbose_print(f"ITERATION {i+1}", f"Processing task...")
            
            try:
                self._verbose_print("CALLING LLM", f"Sending task to model: {self.model}")
                response = self.client.chat([{"role": "user", "content": task}], tools=self.tools)
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
                    
                    # Continue conversation with tool result
                    try:
                        self._verbose_print("REFINING", "Sending tool result back to LLM for refinement")
                        response = self.client.chat(
                            [{"role": "user", "content": task}, 
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
                self._verbose_print("GENERATING RESPONSE", f"Producing final output ({len(out)} chars)")
                return {"success": True, "output": out, "elapsed": time.time()-start}
        
        return {"success": False, "output": "Max iterations", "elapsed": time.time()-start}

    def run_self_learning_cycle(self, task):
        """Complete self-learning cycle with reflection"""
        
        self._verbose_print("SELF-LEARNING CYCLE", "Starting self-improvement loop")
        
        # Step 1: Generate
        self._verbose_print("STEP 1: GENERATE", "Creating initial solution")
        result = self.execute_task(task)
        
        # Step 2: Execute to check for errors
        self._verbose_print("STEP 2: EXECUTE", "Testing the generated code")
        if "```python" in result.get("output", ""):
            code = result["output"].split("```python")[1].split("```")[0] if "```python" in result["output"] else result["output"]
            exec_result = execute_tool("execute_code", {"code": code, "timeout": 10})
            self._verbose_print("EXECUTION RESULT", exec_result[:150])
            
            # Step 3: Reflect
            if "Error" in exec_result or "Traceback" in exec_result:
                self._verbose_print("STEP 3: REFLECT", "Detected error - analyzing what went wrong")
                # Self-reflection would happen here in full implementation
                self._verbose_print("SELF-REFLECTION", "Analyzing error cause and fix needed")
        
        return result

    def interactive(self):
        print("\nSL-LLM Interactive (type 'exit' to quit)")
        print("Commands: 'verbose on/off' to toggle thinking display\n")
        
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
                
                result = self.execute_task(task)
                print(f"\n{result.get('output', 'No output')[:500]}\n")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    sllm = SelfLearningLLM(verbose=verbose)
    
    if "--test" in sys.argv:
        result = sllm.execute_task("Write a fibonacci function in Python")
        print(f"\nResult:\n{result.get('output', 'No output')[:400]}")
    else:
        sllm.interactive()

if __name__ == "__main__":
    main()