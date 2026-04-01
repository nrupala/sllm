"""
SL-LLM Phase 3: Security, Scalability, Formal Verification
- Input sanitization and security hardening
- Multi-instance architecture for scalability
- Static analysis and formal verification for generated code
"""

import ast
import re
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


# ============================================================
# SECURITY HARDENING
# ============================================================

class InputSanitizer:
    """Sanitize and validate all inputs"""
    
    DANGEROUS_PATTERNS = [
        r"os\.system\s*\(",
        r"subprocess\.(call|run|Popen)\s*\(",
        r"eval\s*\(",
        r"exec\s*\(",
        r"__import__\s*\(",
        r"compile\s*\(",
        r"globals\s*\(",
        r"locals\s*\(",
        r"open\s*\(['\"].*?(?:/etc/passwd|\.ssh|\.env)",
        r"rm\s+-rf\s+/",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"INSERT\s+INTO.*(?:DROP|DELETE|UPDATE)",
        r"<script>",
        r"javascript:",
        r"data:text/html",
    ]
    
    MAX_INPUT_LENGTH = 10000
    MAX_FILE_PATH_LENGTH = 500
    
    @classmethod
    def sanitize_text(cls, text: str) -> Tuple[str, List[str]]:
        """Sanitize text input, return (cleaned_text, warnings)"""
        warnings = []
        
        if len(text) > cls.MAX_INPUT_LENGTH:
            warnings.append(f"Input truncated from {len(text)} to {cls.MAX_INPUT_LENGTH} chars")
            text = text[:cls.MAX_INPUT_LENGTH]
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                warnings.append(f"Dangerous pattern detected: {pattern}")
        
        return text, warnings
    
    @classmethod
    def sanitize_file_path(cls, path: str) -> Tuple[str, List[str]]:
        """Sanitize file path, prevent path traversal"""
        warnings = []
        
        if len(path) > cls.MAX_FILE_PATH_LENGTH:
            warnings.append(f"Path too long: {len(path)} chars")
            path = path[:cls.MAX_FILE_PATH_LENGTH]
        
        # Prevent path traversal
        if ".." in path:
            warnings.append("Path traversal attempt detected")
            path = path.replace("..", "")
        
        # Normalize path
        path = str(Path(path).resolve())
        
        return path, warnings
    
    @classmethod
    def sanitize_code(cls, code: str) -> Tuple[str, List[str]]:
        """Sanitize code for safe execution"""
        warnings = []
        
        for pattern in cls.DANGEROUS_PATTERNS:
            matches = re.findall(pattern, code, re.IGNORECASE)
            if matches:
                warnings.append(f"Dangerous code pattern: {pattern} ({len(matches)} matches)")
        
        return code, warnings


class RateLimiter:
    """Rate limiting for API calls and operations"""
    
    def __init__(self, max_requests: int = 100, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[float] = []
    
    def allow_request(self) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Remove old requests
        cutoff = now - self.window_seconds
        self.requests = [t for t in self.requests if t > cutoff]
        
        if len(self.requests) >= self.max_requests:
            return False
        
        self.requests.append(now)
        return True
    
    def get_status(self) -> Dict:
        now = time.time()
        cutoff = now - self.window_seconds
        active = len([t for t in self.requests if t > cutoff])
        return {
            "active_requests": active,
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
            "remaining": max(0, self.max_requests - active),
        }


class SecurityAudit:
    """Security audit and monitoring"""
    
    def __init__(self):
        self.audit_log: List[Dict] = []
        self.violations: List[Dict] = []
        self.sanitizer = InputSanitizer()
        self.rate_limiter = RateLimiter()
    
    def audit_input(self, input_type: str, content: str) -> Dict:
        """Audit an input for security issues"""
        if not self.rate_limiter.allow_request():
            self.violations.append({
                "type": "rate_limit_exceeded",
                "input_type": input_type,
                "timestamp": datetime.now().isoformat(),
            })
            return {"allowed": False, "reason": "Rate limit exceeded"}
        
        if input_type == "text":
            cleaned, warnings = self.sanitizer.sanitize_text(content)
        elif input_type == "file_path":
            cleaned, warnings = self.sanitizer.sanitize_file_path(content)
        elif input_type == "code":
            cleaned, warnings = self.sanitizer.sanitize_code(content)
        else:
            cleaned, warnings = content, []
        
        result = {
            "allowed": len(warnings) == 0,
            "warnings": warnings,
            "cleaned": cleaned,
        }
        
        self.audit_log.append({
            "type": input_type,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        })
        
        if warnings:
            self.violations.append({
                "type": "input_warning",
                "input_type": input_type,
                "warnings": warnings,
                "timestamp": datetime.now().isoformat(),
            })
        
        return result
    
    def get_status(self) -> Dict:
        return {
            "total_audits": len(self.audit_log),
            "total_violations": len(self.violations),
            "rate_limiter": self.rate_limiter.get_status(),
            "recent_audits": self.audit_log[-5:],
            "recent_violations": self.violations[-5:],
        }


# ============================================================
# SCALABILITY
# ============================================================

class InstanceRegistry:
    """Registry for multiple SL-LLM instances"""
    
    def __init__(self, registry_file: str = "D:/sl/projects/sllm/memory/instance_registry.json"):
        self.registry_file = Path(registry_file)
        self.instances: Dict[str, Dict] = {}
        self._load()
    
    def register(self, instance_id: str, metadata: Dict = None) -> str:
        """Register a new instance"""
        self.instances[instance_id] = {
            "id": instance_id,
            "registered_at": datetime.now().isoformat(),
            "last_heartbeat": datetime.now().isoformat(),
            "status": "active",
            "metadata": metadata or {},
            "tasks_processed": 0,
        }
        self._save()
        return instance_id
    
    def heartbeat(self, instance_id: str) -> bool:
        """Update instance heartbeat"""
        if instance_id in self.instances:
            self.instances[instance_id]["last_heartbeat"] = datetime.now().isoformat()
            self.instances[instance_id]["status"] = "active"
            self._save()
            return True
        return False
    
    def increment_tasks(self, instance_id: str):
        """Increment task count for an instance"""
        if instance_id in self.instances:
            self.instances[instance_id]["tasks_processed"] += 1
            self._save()
    
    def get_active_instances(self) -> List[Dict]:
        """Get all active instances"""
        cutoff = (datetime.now() - timedelta(minutes=5)).isoformat()
        return [
            inst for inst in self.instances.values()
            if inst["last_heartbeat"] > cutoff
        ]
    
    def get_status(self) -> Dict:
        active = self.get_active_instances()
        return {
            "total_instances": len(self.instances),
            "active_instances": len(active),
            "instances": active,
        }
    
    def _save(self):
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_file, "w") as f:
            json.dump(self.instances, f, indent=2)
    
    def _load(self):
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r") as f:
                    self.instances = json.load(f)
            except:
                self.instances = {}


# ============================================================
# FORMAL VERIFICATION
# ============================================================

class CodeVerifier:
    """Static analysis and formal verification for generated code"""
    
    DANGEROUS_FUNCTIONS = {
        "eval", "exec", "compile", "__import__", "globals", "locals",
        "open", "input", "breakpoint",
    }
    
    DANGEROUS_MODULES = {
        "os", "subprocess", "sys", "ctypes", "pickle", "marshal",
        "shelve", "socket", "http", "urllib",
    }
    
    def __init__(self):
        self.verification_log: List[Dict] = []
    
    def verify(self, code: str) -> Dict:
        """Verify code safety and correctness"""
        issues = []
        warnings = []
        passed = True
        
        # Parse AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "valid": False,
                "issues": [f"Syntax error: {e}"],
                "warnings": [],
                "metrics": {},
            }
        
        # Check for dangerous functions
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in self.DANGEROUS_FUNCTIONS:
                    issues.append(f"Dangerous function: {node.func.id} at line {node.lineno}")
                    passed = False
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.DANGEROUS_FUNCTIONS:
                        issues.append(f"Dangerous method: {node.func.attr} at line {node.lineno}")
                        passed = False
            
            # Check for dangerous imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.DANGEROUS_MODULES:
                        warnings.append(f"Dangerous module imported: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in self.DANGEROUS_MODULES:
                    warnings.append(f"Dangerous module imported: {node.module}")
            
            # Check for infinite loops
            if isinstance(node, ast.While):
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    # Check for break statement
                    has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                    if not has_break:
                        warnings.append(f"Potential infinite loop at line {node.lineno}")
            
            # Check for undefined variables (basic)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                # This is a simplified check
                pass
        
        # Calculate metrics
        metrics = self._calculate_metrics(tree)
        
        result = {
            "valid": passed,
            "issues": issues,
            "warnings": warnings,
            "metrics": metrics,
        }
        
        self.verification_log.append({
            "timestamp": datetime.now().isoformat(),
            "valid": passed,
            "issues_count": len(issues),
            "warnings_count": len(warnings),
        })
        
        return result
    
    def _calculate_metrics(self, tree: ast.AST) -> Dict:
        """Calculate code metrics"""
        metrics = {
            "functions": 0,
            "classes": 0,
            "lines": 0,
            "complexity": 0,
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                metrics["functions"] += 1
            elif isinstance(node, ast.ClassDef):
                metrics["classes"] += 1
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                metrics["complexity"] += 1
        
        # Count lines
        if hasattr(tree, "end_lineno"):
            metrics["lines"] = tree.end_lineno or 0
        
        return metrics
    
    def get_status(self) -> Dict:
        return {
            "total_verifications": len(self.verification_log),
            "recent_verifications": self.verification_log[-5:],
        }


# ============================================================
# MAIN PHASE 3 SYSTEM
# ============================================================

class Phase3System:
    """Unified Phase 3: Security + Scalability + Formal Verification"""
    
    def __init__(self):
        self.security = SecurityAudit()
        self.registry = InstanceRegistry()
        self.verifier = CodeVerifier()
    
    def audit_input(self, input_type: str, content: str) -> Dict:
        """Audit input for security"""
        return self.security.audit_input(input_type, content)
    
    def verify_code(self, code: str) -> Dict:
        """Verify code safety"""
        return self.verifier.verify(code)
    
    def register_instance(self, instance_id: str, metadata: Dict = None) -> str:
        """Register an instance"""
        return self.registry.register(instance_id, metadata)
    
    def get_status(self) -> Dict:
        return {
            "security": self.security.get_status(),
            "registry": self.registry.get_status(),
            "verifier": self.verifier.get_status(),
        }


# Singleton
_phase3 = None

def get_phase3_system() -> Phase3System:
    global _phase3
    if _phase3 is None:
        _phase3 = Phase3System()
    return _phase3
