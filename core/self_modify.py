import json
import re
from pathlib import Path
from typing import Optional
from core.agent import VersionControl


class SelfModifier:
    def __init__(self, project_path: str = "D:/sl/projects/sllm", client=None):
        self.project_path = Path(project_path)
        self.vc = VersionControl(project_path)
        self.client = client
        self.modification_log = []

    def can_modify(self, path: str) -> bool:
        path_obj = Path(path)
        safe_paths = ["tools", "core", "eval", "memory", "sandbox"]
        for safe in safe_paths:
            if str(path_obj).replace("\\", "/").startswith(str(self.project_path / safe)):
                return True
        return False

    def create_checkpoint(self, label: str = None) -> str:
        return self.vc.create_snapshot(label)

    def restore_checkpoint(self, label: str) -> bool:
        return self.vc.restore_snapshot(label)

    def list_checkpoints(self) -> list:
        return self.vc.list_snapshots()

    def parse_modification_request(self, request: str) -> dict:
        pattern = r"(?:modify|update|change|edit)\s+(?:file\s+)?(.+?)\s+(?:to|with|as)?\s*(.+)"
        match = re.search(pattern, request.lower())
        if match:
            return {"file": match.group(1).strip(), "change": match.group(2).strip()}
        return {"file": None, "change": request}

    def apply_modification(self, file_path: str, modification: str, dry_run: bool = False) -> dict:
        if not self.can_modify(file_path):
            return {"success": False, "error": "Path not allowed for modification"}
        
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": "File not found"}
        
        if dry_run:
            return {"success": True, "dry_run": True, "proposed_change": modification}
        
        try:
            original = path.read_text(encoding="utf-8")
            checkpoint = self.create_checkpoint(f"pre_mod_{path.name}")
            
            new_content = self._generate_modified_content(original, modification)
            path.write_text(new_content, encoding="utf-8")
            
            self.modification_log.append({
                "file": file_path,
                "checkpoint": checkpoint,
                "modification": modification
            })
            
            return {"success": True, "checkpoint": checkpoint, "file": file_path}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_modified_content(self, original: str, modification: str) -> str:
        if self.client:
            prompt = f"""Given this original code:
```
{original[:3000]}
```

And this modification request: {modification}

Apply the modification and return the complete modified code. If the modification is a simple text replacement, just return the modified code. If it's a more complex change, provide the full updated file."""
            
            response = self.client.generate(prompt)
            return response.get("response", original)
        
        return original

    def undo_last_modification(self) -> bool:
        if not self.modification_log:
            return False
        
        last = self.modification_log.pop()
        return self.restore_checkpoint(last["checkpoint"])

    def get_modification_history(self) -> list:
        return self.modification_log


class ImprovementAnalyzer:
    def __init__(self, client):
        self.client = client

    def analyze_performance(self, task: str, output: str, execution_time: float) -> dict:
        prompt = f"""Analyze this code execution:
Task: {task}
Output: {output}
Execution Time: {execution_time}s

Assess:
1. Is the output correct?
2. Is the code efficient?
3. Any bugs or issues?
4. Suggestions for improvement?

Respond in JSON with keys: correctness, efficiency, issues[], suggestions[]"""

        response = self.client.generate(prompt)
        try:
            return json.loads(response.get("response", "{}"))
        except:
            return {"correctness": "unknown", "efficiency": "unknown", "issues": [], "suggestions": []}

    def should_self_modify(self, analysis: dict) -> bool:
        score = analysis.get("correctness", 5)
        if isinstance(score, str):
            return "incorrect" in score.lower() or "bug" in score.lower()
        return score < 7

    def generate_improvement_plan(self, analysis: dict) -> str:
        issues = analysis.get("issues", [])
        suggestions = analysis.get("suggestions", [])
        
        if not issues and not suggestions:
            return "NO_IMPROVEMENT_NEEDED"
        
        plan = "## Improvement Plan\n\n"
        for i, issue in enumerate(issues, 1):
            plan += f"{i}. {issue}\n"
        for i, suggestion in enumerate(suggestions, len(issues) + 1):
            plan += f"{i}. {suggestion}\n"
        
        return plan


class ReflectiveAgent:
    def __init__(self, client, modifier: SelfModifier, evaluator):
        self.client = client
        self.modifier = modifier
        self.evaluator = evaluator
        self.improvement_analyzer = ImprovementAnalyzer(client)

    def reflect_on_task(self, task: str, output: str, execution_time: float) -> dict:
        analysis = self.improvement_analyzer.analyze_performance(task, output, execution_time)
        
        should_modify = self.improvement_analyzer.should_self_modify(analysis)
        
        return {
            "analysis": analysis,
            "should_modify": should_modify,
            "improvement_plan": self.improvement_analyzer.generate_improvement_plan(analysis) if should_modify else None
        }

    def execute_with_reflection(self, task: str, code: str, max_iterations: int = 3) -> dict:
        history = []
        
        for i in range(max_iterations):
            import time
            start = time.time()
            
            from tools.builtin import ExecuteCodeTool
            result = ExecuteCodeTool.execute({"code": code, "timeout": 60})
            exec_time = time.time() - start
            
            reflection = self.reflect_on_task(task, result, exec_time)
            history.append({
                "iteration": i + 1,
                "code": code,
                "output": result,
                "execution_time": exec_time,
                "reflection": reflection
            })
            
            if not reflection["should_modify"]:
                return {
                    "success": True,
                    "output": result,
                    "iterations": i + 1,
                    "history": history
                }
            
            if reflection["improvement_plan"] != "NO_IMPROVEMENT_NEEDED":
                code = self._apply_improvement(code, reflection["improvement_plan"])
        
        return {
            "success": False,
            "output": result,
            "iterations": max_iterations,
            "history": history,
            "message": "Max iterations reached without convergence"
        }

    def _apply_improvement(self, original_code: str, improvement_plan: str) -> str:
        if self.client:
            prompt = f"""Original code:
```
{original_code}
```

Improvement plan:
{improvement_plan}

Apply these improvements and return the complete improved code:"""
            
            response = self.client.generate(prompt)
            return response.get("response", original_code)
        return original_code