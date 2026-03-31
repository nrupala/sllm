import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, model: str = "deepseek-coder:14b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self._check_connection()

    def _check_connection(self):
        try:
            import requests
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                logger.info(f"Connected to Ollama at {self.base_url}")
            else:
                logger.warning(f"Ollama returned status {resp.status_code}")
        except Exception as e:
            logger.warning(f"Could not connect to Ollama: {e}")

    def chat(self, messages: list, tools: Optional[list] = None, **kwargs) -> dict:
        import requests
        payload = {
            "model": self.model,
            "messages": messages,
            **kwargs
        }
        if tools:
            payload["tools"] = tools
        try:
            resp = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=300)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Chat API error: {e}")
            return {"message": {"content": f"Error: {e}"}, "done": True}

    def generate(self, prompt: str, **kwargs) -> dict:
        import requests
        payload = {"model": self.model, "prompt": prompt, **kwargs}
        try:
            resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=300)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Generate API error: {e}")
            return {"response": f"Error: {e}", "done": True}

    def list_models(self) -> list:
        try:
            import requests
            resp = requests.get(f"{self.base_url}/api/tags", timeout=10)
            return resp.json().get("models", [])
        except:
            return []


class Tool:
    def __init__(self, name: str, description: str, parameters: dict):
        self.name = name
        self.description = description
        self.parameters = parameters

    def to_openai_format(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_tools(self) -> list:
        return [t.to_openai_format() for t in self.tools.values()]

    def execute(self, name: str, arguments: dict) -> str:
        if name not in self.tools:
            return f"Unknown tool: {name}"
        try:
            return self.tools[name].execute(arguments)
        except Exception as e:
            return f"Tool execution error: {e}"


class Agent:
    def __init__(self, client: OllamaClient, registry: ToolRegistry, memory: "MemoryStore"):
        self.client = client
        self.registry = registry
        self.memory = memory
        self.conversation = []

    def run(self, task: str, max_iterations: int = 10) -> str:
        self.conversation = [{"role": "user", "content": task}]
        
        for i in range(max_iterations):
            response = self.client.chat(
                self.conversation,
                tools=self.registry.get_tools()
            )
            
            msg = response.get("message", {})
            self.conversation.append(msg)
            
            if msg.get("tool_calls"):
                for call in msg["tool_calls"]:
                    tool_name = call["function"]["name"]
                    args = json.loads(call["function"]["arguments"])
                    result = self.registry.execute(tool_name, args)
                    self.conversation.append({
                        "role": "tool",
                        "tool_call_id": call.get("id", "unknown"),
                        "content": result
                    })
            else:
                content = msg.get("content", "")
                if content:
                    return content
                    
        return "Max iterations reached"


class MemoryStore:
    def __init__(self, base_path: str = "D:/sl/projects/sllm/memory"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.episodes = self.base_path / "episodes.jsonl"
        self.insights = self.base_path / "insights.jsonl"
        self._init_files()

    def _init_files(self):
        if not self.episodes.exists():
            self.episodes.write_text("")
        if not self.insights.exists():
            self.insights.write_text("")

    def save_episode(self, task: str, actions: list, result: str, metrics: dict):
        with open(self.episodes, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "task": task,
                "actions": actions,
                "result": result,
                "metrics": metrics
            }) + "\n")

    def save_insight(self, insight: str, category: str):
        with open(self.insights, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "insight": insight,
                "category": category
            }) + "\n")

    def get_recent_episodes(self, n: int = 10) -> list:
        if not self.episodes.exists():
            return []
        with open(self.episodes, "r") as f:
            lines = f.readlines()
            return [json.loads(l) for l in lines[-n:]]


class SelfEvaluator:
    def __init__(self, client: OllamaClient):
        self.client = client

    def evaluate_output(self, task: str, output: str) -> dict:
        prompt = f"""Evaluate the following task result.
Task: {task}
Output: {output}

Rate on a scale of 0-10 for:
- Correctness
- Efficiency
- Quality

Respond in JSON format with keys: correctness, efficiency, quality, overall_score, feedback."""
        
        response = self.client.generate(prompt)
        try:
            return json.loads(response.get("response", "{}"))
        except:
            return {"overall_score": 5, "feedback": "Could not evaluate"}

    def suggest_improvements(self, task: str, output: str, evaluation: dict) -> str:
        prompt = f"""Given this task and evaluation:
Task: {task}
Output: {output}
Evaluation: {evaluation}

Suggest specific code improvements if any. If no improvement needed, respond with "NO_IMPROVEMENT_NEEDED"."""
        
        response = self.client.generate(prompt)
        return response.get("response", "")


class VersionControl:
    def __init__(self, base_path: str = "D:/sl/projects/sllm"):
        self.base_path = Path(base_path)
        self.snapshots = self.base_path / "snapshots"
        self.snapshots.mkdir(exist_ok=True)

    def create_snapshot(self, label: str = None) -> str:
        import shutil
        label = label or datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_path = self.snapshots / label
        
        for subdir in ["core", "tools", "eval"]:
            src = self.base_path / subdir
            if src.exists():
                dst = snapshot_path / subdir
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(src, dst, dirs_exist_ok=True)
        
        logger.info(f"Created snapshot: {label}")
        return label

    def restore_snapshot(self, label: str) -> bool:
        import shutil
        snapshot_path = self.snapshots / label
        if not snapshot_path.exists():
            return False
        
        for subdir in ["core", "tools", "eval"]:
            dst = self.base_path / subdir
            if (snapshot_path / subdir).exists():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(snapshot_path / subdir, dst)
        
        logger.info(f"Restored snapshot: {label}")
        return True

    def list_snapshots(self) -> list:
        return [p.name for p in self.snapshots.iterdir() if p.is_dir()]


if __name__ == "__main__":
    print("SL-LLM Core Module")
    print(f"Memory store: {MemoryStore().base_path}")
    print(f"Version control: {VersionControl().snapshots}")