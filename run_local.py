"""
SL-LLM Local Runner
Self-contained local LLM execution using GGUF models.

Supports:
- Direct GGUF loading (llama.cpp bindings)
- LM Studio API
- Ollama API

Usage:
    python run_local.py              # Auto-detect best option
    python run_local.py --model gemma-3-4b-it  # Specific model
    python run_local.py --interactive # Chat mode
"""

import argparse
import json
import os
import platform
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.client import get_client, detect_gpu, GPU_INFO
from tools.builtin import get_default_tools
from knowledge_graph_manager import FluidKnowledgeGraph, get_enhanced_context


# ============================================================================
# Configuration
# ============================================================================

LOCAL_GGUF_MODELS = {
    "gemma-3-4b-it": {
        "path": "D:/models/lmstudio-community/gemma-3-4b-it-GGUF/gemma-3-4b-it-Q4_K_M.gguf",
        "size": 2.32,
        "quantization": "Q4_K_M",
        "context": 8192,
    },
    "gemma-3-4b": {
        "path": "D:/models/lmstudio-community/gemma-3-4b-it-GGUF/gemma-3-4b-it-Q4_K_M.gguf",
        "size": 2.32,
        "quantization": "Q4_K_M",
        "context": 8192,
    },
    "lfm-1.2b": {
        "path": "D:/models/lmstudio-community/LFM2.5-1.2B-Instruct-GGUF/LFM2.5-1.2B-Instruct-Q8_0.gguf",
        "size": 1.16,
        "quantization": "Q8_0",
        "context": 4096,
    },
    "lfm2.5-1.2b": {
        "path": "D:/models/lmstudio-community/LFM2.5-1.2B-Instruct-GGUF/LFM2.5-1.2B-Instruct-Q8_0.gguf",
        "size": 1.16,
        "quantization": "Q8_0",
        "context": 4096,
    },
}


# ============================================================================
# LLM Execution Backends
# ============================================================================

class LLMBackend:
    """Base LLM backend"""
    
    def __init__(self, name: str):
        self.name = name
        
    def chat(self, messages, tools=None, **kwargs):
        raise NotImplemented
    
    def generate(self, prompt, **kwargs):
        raise NotImplemented


class LMStudioBackend(LLMBackend):
    """LM Studio API backend"""
    
    def __init__(self, model: str = "auto"):
        super().__init__("lmstudio")
        self.base_url = "http://localhost:1234/v1"
        self.model = model
        self._check_connection()
        
    def _check_connection(self):
        import urllib.request
        try:
            req = urllib.request.Request(f"{self.base_url}/models")
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read())
                models = data.get("data", [])
                if models and self.model == "auto":
                    self.model = models[0]["id"]
                    print(f"Using model: {self.model}")
        except Exception as e:
            print(f"LM Studio not available: {e}")
            self.model = None
    
    def chat(self, messages, tools=None, **kwargs):
        import urllib.request
        
        if not self.model:
            return {"error": "No model available"}
        
        # Build messages for API
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2048),
        }
        
        if tools:
            payload["tools"] = tools
            
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    
    def generate(self, prompt, **kwargs):
        return self.chat([{"role": "user", "content": prompt}], **kwargs)


class OllamaBackend(LLMBackend):
    """Ollama API backend"""
    
    def __init__(self, model: str = "auto"):
        super().__init__("ollama")
        self.base_url = "http://localhost:11434"
        self.model = model
        self._check_connection()
        
    def _check_connection(self):
        import urllib.request
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=2) as resp:
                data = json.loads(resp.read())
                models = data.get("models", [])
                if models and self.model == "auto":
                    self.model = models[0]["name"]
                    print(f"Using model: {self.model}")
        except Exception as e:
            print(f"Ollama not available: {e}")
            self.model = None
    
    def chat(self, messages, tools=None, **kwargs):
        import urllib.request
        
        if not self.model:
            return {"error": "No model available"}
        
        # Convert to Ollama format
        ollama_messages = []
        for m in messages:
            ollama_messages.append({
                "role": m.get("role", "user"),
                "content": m.get("content", "")
            })
        
        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
        }
        
        req = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read())
    
    def generate(self, prompt, **kwargs):
        return self.chat([{"role": "user", "content": prompt}], **kwargs)


class MockBackend(LLMBackend):
    """Mock backend for testing"""
    
    def __init__(self, model: str = "mock"):
        super().__init__("mock")
        self.model = model
        
    def chat(self, messages, tools=None, **kwargs):
        from core.client import MockClient
        return MockClient(self.model).chat(messages, tools, **kwargs)
    
    def generate(self, prompt, **kwargs):
        from core.client import MockClient
        return MockClient(self.model).generate(prompt, **kwargs)


# ============================================================================
# Main Runner
# ============================================================================

class SL_LLM_Runner:
    """SL-LLM Local Runner"""
    
    def __init__(self, prefer: str = "auto", model: Optional[str] = None):
        self.prefer = prefer
        self.model = model
        self.kgm = FluidKnowledgeGraph()
        self.backend = None
        
    def initialize(self):
        """Initialize the best available backend"""
print(f"\n{'='*50}")
        print(f"SL-LLM Local Runner")
        print(f"{'='*50}")
        print(f"Platform: {platform.system()}")
        print(f"GPU: {GPU_INFO[0]} - {GPU_INFO[1][:50] if GPU_INFO[1] else 'CPU'}")
        
        # Try backends in order
        if self.prefer == "auto":
            backends = ["lmstudio", "ollama", "mock"]
        else:
            backends = [self.prefer]
        
        for backend_name in backends:
            try:
                if backend_name == "lmstudio":
                    self.backend = LMStudioBackend(self.model)
                    if self.backend.model:
                        print(f"[OK] Using model: {self.backend.model}")
                        break
                elif backend_name == "ollama":
                    self.backend = OllamaBackend(self.model)
                    if self.backend.model:
                        print(f"[OK] Using model: {self.backend.model}")
                        break
                elif backend_name == "mock":
                    self.backend = MockBackend(self.model)
                    print(f"[OK] Using Mock backend")
                    break
            except Exception as e:
                print(f"[FAIL] {backend_name}: {e}")
        
        if not self.backend:
            print("No backend available, using mock")
            self.backend = MockBackend(self.model)
        
        print(f"{'='*50}\n")
        
    def run_task(self, task: str) -> str:
        """Execute a task with full SL-LLM pipeline"""
        print(f"Task: {task}\n")
        
        # Get knowledge graph context
        enhanced_context, kg_metadata = get_enhanced_context(task)
        
        # Build full prompt
        full_prompt = f"""{enhanced_context}

Task: {task}

Respond with:
1. Analysis of what needs to be done
2. The solution/code
3. Self-reflection on potential issues
"""
        
        try:
            # Call LLM
            response = self.backend.chat(
                [{"role": "user", "content": full_prompt}],
                tools=get_default_tools()
            )
            
            if "error" in response:
                return f"Error: {response['error']}"
            
            message = response.get("message", {})
            content = message.get("content", "No response")
            
            # Handle tool calls
            if message.get("tool_calls"):
                print("Executing tool calls...")
                for call in message["tool_calls"]:
                    tool_name = call["function"]["name"]
                    try:
                        args = json.loads(call["function"]["arguments"])
                    except:
                        args = {"code": call["function"]["arguments"]}
                    
                    from tools.builtin import execute_tool
                    result = execute_tool(tool_name, args)
                    print(f"Tool {tool_name}: {result[:200]}...")
                    
                    # Refine with tool result
                    response = self.backend.chat(
                        [{"role": "user", "content": full_prompt},
                         message,
                         {"role": "tool", "content": result}],
                        tools=get_default_tools()
                    )
                    message = response.get("message", {})
                    content = message.get("content", content)
            
            return content
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def interactive(self):
        """Interactive chat mode"""
        print("\nSL-LLM Interactive Mode")
        print("Type 'quit' to exit, 'clear' to clear history\n")
        
        messages = []
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                if user_input.lower() == "clear":
                    messages = []
                    print("History cleared\n")
                    continue
                    
                messages.append({"role": "user", "content": user_input})
                
                response = self.backend.chat(messages)
                
                if "error" in response:
                    print(f"Error: {response['error']}\n")
                    continue
                
                message = response.get("message", {})
                content = message.get("content", "")
                
                if content:
                    print(f"SL-LLM: {content}\n")
                    messages.append({"role": "assistant", "content": content})
                else:
                    print("No response\n")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="SL-LLM Local Runner")
    parser.add_argument("--prefer", default="auto",
                     choices=["auto", "lmstudio", "ollama", "mock"],
                     help="Backend preference")
    parser.add_argument("--model", help="Model name")
    parser.add_argument("--task", help="Task to execute")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    parser.add_argument("--list-models", action="store_true", help="List available models")
    
    args = parser.parse_args()
    
    runner = SL_LLM_Runner(prefer=args.prefer, model=args.model)
    runner.initialize()
    
    if args.list_models:
        if runner.backend.name == "lmstudio":
            import urllib.request
            try:
                req = urllib.request.Request("http://localhost:1234/v1/models")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read())
                    print("\nAvailable models:")
                    for m in data.get("data", []):
                        print(f"  - {m['id']}")
            except:
                print("No models available")
        elif runner.backend.name == "ollama":
            import urllib.request
            try:
                req = urllib.request.Request("http://localhost:11434/api/tags")
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = json.loads(resp.read())
                    print("\nAvailable models:")
                    for m in data.get("models", []):
                        print(f"  - {m['name']} ({m.get('size', '?')})")
            except:
                print("No models available")
        return
    
    if args.task:
        result = runner.run_task(args.task)
        print(f"\n{'='*50}")
        print(f"Result:")
        print(f"{'='*50}")
        print(result)
    elif args.interactive:
        runner.interactive()
    else:
        # Default: show available models
        print("\nUse --task 'your task' or --interactive")
        print("Available local models:")
        for name, info in LOCAL_GGUF_MODELS.items():
            print(f"  - {name}: {info['path'].split('/')[-1]} ({info['size']}GB)")


if __name__ == "__main__":
    main()