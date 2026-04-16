import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Dict, List
from dataclasses import dataclass, field

from prompts.prompt_engine import PromptManager
from core.client import LocalRunner, OllamaClient as BaseOllamaClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConversationMessage:
    role: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


@dataclass
class Session:
    session_id: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())
    message_count: int = 0
    context_window: List[ConversationMessage] = field(default_factory=list)
    max_context: int = 20


class ContextManager:
    MAX_CONTEXT = 20

    def __init__(self, max_context: int = None):
        self.max_context = max_context or self.MAX_CONTEXT
        self.sessions: Dict[str, Session] = {}

    def get_or_create_session(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            self.sessions[session_id] = Session(session_id=session_id)
        return self.sessions[session_id]

    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None):
        session = self.get_or_create_session(session_id)
        msg = ConversationMessage(role=role, content=content, metadata=metadata or {})
        session.context_window.append(msg)
        session.message_count += 1
        session.last_activity = datetime.now().isoformat()

        if len(session.context_window) > self.max_context:
            session.context_window = session.context_window[-self.max_context:]

    def get_conversation_history(self, session_id: str, max_turns: int = None) -> str:
        session = self.sessions.get(session_id)
        if not session:
            return ""

        window = session.context_window[-max_turns:] if max_turns else session.context_window
        lines = []
        for msg in window:
            role = msg.role.upper() if msg.role != "tool" else "TOOL"
            lines.append(f"{role}: {msg.content[:500]}")
        return "\n".join(lines)

    def get_recent_messages(self, session_id: str, n: int = 5) -> List[ConversationMessage]:
        session = self.sessions.get(session_id)
        if not session:
            return []
        return session.context_window[-n:]

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def list_sessions(self) -> List[str]:
        return list(self.sessions.keys())


class SafetyEnforcer:
    BLOCKED_PATTERNS = [
        r"(hack|bypass|exploit)\s+(security|authentication|permission)",
        r"(malware|virus|ransomware|trojan)",
        r"(generate\s+(harmful|illegal|weapon))",
    ]

    def __init__(self):
        import re
        self.blocked_patterns = [re.compile(p, re.IGNORECASE) for p in self.BLOCKED_PATTERNS]

    def check_input(self, user_input: str) -> tuple[bool, str]:
        for pattern in self.blocked_patterns:
            if pattern.search(user_input):
                return False, "Input blocked: potentially harmful content detected"
        return True, ""

    def sanitize_output(self, output: str) -> str:
        dangerous = ["<script>", "javascript:", "onerror=", "onclick="]
        sanitized = output
        for d in dangerous:
            sanitized = sanitized.replace(d, "")
        return sanitized


class TruncationHandler:
    MAX_OUTPUT_LENGTH = 8000

    def __init__(self, max_length: int = None):
        self.max_length = max_length or self.MAX_OUTPUT_LENGTH

    def check_and_truncate(self, output: str) -> tuple[str, bool]:
        if len(output) <= self.max_length:
            return output, False

        truncated = output[:self.max_length]
        return truncated, True

    def get_continuation_prompt(self) -> str:
        return "\n\n[Response truncated. Ask a follow-up to continue the thought.]"


class ZeroCheckValidator:
    @staticmethod
    def validate_division(numerator: Any, denominator: Any) -> bool:
        try:
            if denominator == 0:
                return False
            return True
        except:
            return False

    @staticmethod
    def validate_array_access(arr: list, index: int) -> bool:
        return 0 <= index < len(arr)

    @staticmethod
    def validate_file_path(path: str) -> bool:
        try:
            p = Path(path)
            return not p.is_absolute() or str(path).startswith(str(Path.cwd()))
        except:
            return False


class SLLLMAgent:
    DEFAULT_SESSION = "default"

    def __init__(
        self,
        model: str = "qwen2.5-coder:14b",
        engine: str = "lmstudio",
        system_prompt: str = None
    ):
        self.model = model
        self.engine = engine
        self.prompt_manager = PromptManager()
        self.context_manager = ContextManager()
        self.safety_enforcer = SafetyEnforcer()
        self.truncation_handler = TruncationHandler()
        self.zero_check = ZeroCheckValidator()

        if system_prompt:
            self.prompt_manager.system_prompt = system_prompt

        self.client = self._init_client()
        self._verify_connection()

    def _init_client(self):
        if self.engine == "lmstudio":
            return LocalRunner(base_url="http://localhost:1234/v1")
        elif self.engine == "ollama":
            return BaseOllamaClient(model=self.model)
        else:
            return LocalRunner(base_url="http://localhost:1234/v1")

    def _verify_connection(self):
        try:
            if hasattr(self.client, 'models'):
                models = self.client.models()
                logger.info(f"Connected with {len(models)} models available")
            else:
                logger.info(f"Using {self.engine} engine")
        except Exception as e:
            logger.warning(f"Connection check: {e}")

    def generate(
        self,
        user_input: str,
        session_id: str = None,
        task_type: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> Dict[str, Any]:
        session_id = session_id or self.DEFAULT_SESSION

        safe, reason = self.safety_enforcer.check_input(user_input)
        if not safe:
            return {
                "success": False,
                "error": reason,
                "session_id": session_id
            }

        conversation_history = self.context_manager.get_conversation_history(session_id)
        
        if task_type:
            prompt = self.prompt_manager.render_task(task_type, user_message=user_input)
        else:
            prompt = self.prompt_manager.get_full_prompt(user_input, conversation_history)

        self.context_manager.add_message(session_id, "user", user_input)

        try:
            if hasattr(self.client, 'chat'):
                messages = [{"role": "user", "content": prompt}]
                response = self.client.chat(messages)
                output = response.get("message", {}).get("content", "")
            else:
                output = self.client.generate(prompt, temperature=temperature, max_tokens=max_tokens)

            output, was_truncated = self.truncation_handler.check_and_truncate(output)

            if was_truncated:
                output += self.truncation_handler.get_continuation_prompt()

            self.context_manager.add_message(session_id, "assistant", output)

            return {
                "success": True,
                "output": output,
                "session_id": session_id,
                "truncated": was_truncated,
                "model": self.model,
                "engine": self.engine
            }

        except Exception as e:
            logger.error(f"Generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }

    def chat(self, messages: List[Dict], session_id: str = None, **kwargs) -> Dict:
        session_id = session_id or self.DEFAULT_SESSION
        last_msg = messages[-1].get("content", "") if messages else ""

        return self.generate(last_msg, session_id=session_id, **kwargs)

    def get_session_info(self, session_id: str = None) -> Dict:
        session_id = session_id or self.DEFAULT_SESSION
        session = self.context_manager.sessions.get(session_id)
        if not session:
            return {"session_id": session_id, "exists": False}
        return {
            "session_id": session.session_id,
            "exists": True,
            "message_count": session.message_count,
            "created_at": session.created_at,
            "last_activity": session.last_activity
        }

    def clear_session(self, session_id: str = None):
        session_id = session_id or self.DEFAULT_SESSION
        self.context_manager.clear_session(session_id)

    def list_sessions(self) -> List[str]:
        return self.context_manager.list_sessions()


def create_agent(
    model: str = "qwen2.5-coder:14b",
    engine: str = "lmstudio",
    system_prompt: str = None
) -> SLLLMAgent:
    return SLLLMAgent(model=model, engine=engine, system_prompt=system_prompt)


if __name__ == "__main__":
    agent = create_agent()
    print("SL-LLM Agent initialized")
    print(f"Available templates: {agent.prompt_manager.template_engine.list_templates()}")
    
    result = agent.generate("Hello, what can you do?", task_type="conversation")
    print(f"\nResponse: {result.get('output', result.get('error'))[:200]}")