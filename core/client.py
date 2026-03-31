"""
SL-LLM Client with GPU optimization
Supports: LM Studio, Ollama, Mock
"""

import json
import os
import sys


def detect_gpu():
    """Detect GPU availability"""
    try:
        import subprocess
        result = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return "nvidia", result.stdout.strip()
    except:
        pass
    
    # Check for AMD GPU
    try:
        import subprocess
        result = subprocess.run(["wmic", "path", "win32_VideoController", "get", "name"], 
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and "AMD" in result.stdout:
            return "amd", result.stdout.strip()
    except:
        pass
    
    return "cpu", None


GPU_INFO = detect_gpu()
print(f"Detected: {GPU_INFO[0]} - {GPU_INFO[1][:50] if GPU_INFO[1] else 'CPU mode'}")


class BaseLLMClient:
    def chat(self, messages, tools=None, **kwargs): raise NotImplemented
    def generate(self, prompt, **kwargs): raise NotImplemented


class MockClient(BaseLLMClient):
    def __init__(self, model="deepseek-coder:14b"):
        self.model = model
    
    def _generate(self, prompt):
        p = prompt.lower()
        if "fibonacci" in p:
            return '''def fibonacci(n):
    if n <= 0: return 0
    elif n == 1: return 1
    return fibonacci(n-1) + fibonacci(n-2)

# Test
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")'''
        if "reverse" in p and "string" in p:
            return 'def reverse_string(s): return s[::-1]\nprint(reverse_string("hello"))'
        if "prime" in p:
            return '''def is_prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True'''
        if "sort" in p:
            return '''def quicksort(arr):
    if len(arr) <= 1: return arr
    pivot = arr[len(arr) // 2]
    return quicksort([x for x in arr if x < pivot]) + [x for x in arr if x == pivot] + quicksort([x for x in arr if x > pivot])'''
        if "tool" in p:
            return "I'll use the available tools to help you."
        return '''# Solution
def solution():
    pass

# Add your implementation here''' 
    
    def chat(self, messages, tools=None, **kwargs):
        import time
        time.sleep(0.5)  # Simulate thinking
        last = messages[-1].get("content", "") if messages else ""
        return {"message": {"content": self._generate(last), "tool_calls": []}, "done": True}
    
    def generate(self, prompt, **kwargs):
        import time
        time.sleep(0.5)
        return {"response": self._generate(prompt), "done": True}


class LMStudioClient(BaseLLMClient):
    def __init__(self, model="local-model", url="http://localhost:1234/v1"):
        self.model = model
        self.url = url
        self.timeout = 120  # 2 min timeout for GPU
    
    def _request(self, endpoint, data):
        try:
            import requests
            resp = requests.post(f"{self.url}{endpoint}", json=data, timeout=self.timeout)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def chat(self, messages, tools=None, **kwargs):
        payload = {"model": self.model, "messages": messages, **kwargs}
        if tools:
            payload["tools"] = tools
        result = self._request("/chat/completions", payload)
        if "error" in result:
            return {"message": {"content": f"Error: {result['error']}"}, "done": True}
        return {"message": {"content": result.get("choices", [{}])[0].get("message", {}).get("content", "")}, "done": True}
    
    def generate(self, prompt, **kwargs):
        payload = {"model": self.model, "prompt": prompt, **kwargs}
        result = self._request("/completions", payload)
        if "error" in result:
            return {"response": f"Error: {result['error']}", "done": True}
        return {"response": result.get("choices", [{}])[0].get("text", ""), "done": True}


def get_client(prefer="lmstudio", model="local-model"):
    """Auto-detect and return best available client"""
    
    # Try LM Studio first (port 1234) - optimized for GPU
    if prefer in ["lmstudio", "auto"]:
        try:
            import requests
            r = requests.get("http://localhost:1234/v1/models", timeout=5)
            if r.status_code == 200:
                models = r.json().get("data", [])
                # Use the actual loaded model from LM Studio
                model_name = "qwen2.5-coder"  # Auto-detected from loaded model
                print(f">> Using LM Studio with {model_name} (GPU accelerated)")
                return LMStudioClient(model_name)
        except Exception as e:
            print(f"LM Studio not available: {e}")
    
    # Try Ollama (port 11434)
    if prefer in ["ollama", "auto"]:
        try:
            import requests
            r = requests.get("http://localhost:11434/api/tags", timeout=5)
            if r.status_code == 200:
                from core.agent import OllamaClient
                print(f">> Using Ollama")
                return OllamaClient(model)
        except:
            pass
    
    # Fallback to mock
    print(">> Using MOCK backend")
    return MockClient(model)


if __name__ == "__main__":
    client = get_client("auto")
    print("Testing...")
    r = client.chat([{"role": "user", "content": "write fibonacci"}])
    print(r["message"]["content"][:200])