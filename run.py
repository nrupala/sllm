"""
SL-LLM Entry Point
Usage: python run.py [--test] [--prefer lmstudio|ollama|mock]
"""

import sys

import json
import time
from pathlib import Path

prefer = "auto"
for arg in sys.argv:
    if arg.startswith("--prefer="):
        prefer = arg.split("=")[1]

from core.client import get_client
llm_client = get_client(prefer=prefer)

from tools.builtin import get_default_tools, execute_tool


class SelfLearningLLM:
    def __init__(self, model="qwen2.5-coder"):
        self.model = model
        self.client = llm_client
        self.tools = get_default_tools()
        print(f"SL-LLM initialized with {self.model}")
        print(f"Tools: {[t['function']['name'] for t in self.tools]}")

    def execute_task(self, task, max_iterations=5):
        print(f"\nTask: {task}")
        start = time.time()
        
        for i in range(max_iterations):
            try:
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
                    print(f"  [Tool] {tool_name}: {str(args)[:50]}...")
                    result = execute_tool(tool_name, args)
                    print(f"  [Result] {str(result)[:100]}...")
                    
                    # Continue conversation with tool result
                    try:
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
                return {"success": True, "output": out, "elapsed": time.time()-start}
        
        return {"success": False, "output": "Max iterations", "elapsed": time.time()-start}

    def interactive(self):
        print("\nSL-LLM Interactive (type 'exit' to quit)\n")
        while True:
            try:
                task = input(">> ")
                if task.lower() == "exit":
                    break
                result = self.execute_task(task)
                print(f"\n{result.get('output', 'No output')[:500]}\n")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    sllm = SelfLearningLLM()
    if "--test" in sys.argv:
        result = sllm.execute_task("Write a fibonacci function in Python")
        print(f"\nResult:\n{result.get('output', 'No output')[:400]}")
    else:
        sllm.interactive()

if __name__ == "__main__":
    main()