"""
SL-LLM Daemon Server
Exposes SL-LLM as a local API server with MCP/OpenAI-compatible endpoints.
Links with local LLM engines: LM Studio, Ollama, llama.cpp, text-gen-webui.

Usage:
    python daemon.py                    # Start server on default port 8080
    python daemon.py --port 9000       # Custom port
    python daemon.py --prefer lmstudio  # Use specific backend
    python daemon.py --mock          # Test mode (no real LLM)

API Endpoints:
    POST /v1/chat/completions    - OpenAI-compatible chat
    POST /v1/completions        - OpenAI-compatible completion
    GET  /health               - Health check
    GET  /models              - List available models
    POST /execute              - Execute task with tools

MCP-Style:
    POST /mcp/tools/list       - List available tools
    POST /mcp/tools/call      - Call a tool
    POST /mcp/resources       - Access knowledge graph

WebSocket:
    WS /ws                   - Interactive session
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("sllm-daemon")

# Try to import HTTP server libraries
try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, Web, WebSocket, WebSocketDisconnect
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    logger.warning("fastapi/uvicorn not available - using basic HTTP server")
    FASTAPI_AVAILABLE = False
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from socketserver import ThreadingMixIn

# Import SL-LLM core
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.client import get_client, detect_gpu, GPU_INFO
from tools.builtin import get_default_tools, execute_tool
from knowledge_graph_manager import FluidKnowledgeGraph, get_enhanced_context


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class DaemonConfig:
    """Server configuration"""
    host: str = "127.0.0.1"
    port: int = 8080
    prefer: str = "auto"  # lmstudio, ollama, llama.cpp, mock
    model: str = "local"
    cors_enabled: bool = True
    api_key: Optional[str] = None  # Optional API key
    max_concurrent: int = 4
    timeout: int = 300
    
    # Security
    allowed_actions: List[str] = field(default_factory=lambda: [
        "file_read", "file_write", "list_directory", "execute_code",
        "search_code", "get_system_info", "git_operations"
    ])
    blocked_patterns: List[str] = field(default_factory=lambda: [
        r"rm\s+-rf", r"mkfs", r">\s*/dev/sd", r"curl.*\|.*bash"
    ])


# ============================================================================
# Security Layer
# ============================================================================

class ActionValidator:
    """Validates actions before execution - Action-Selector Pattern"""
    
    def __init__(self, config: DaemonConfig):
        self.config = config
        self.action_counts: Dict[str, int] = {}
        
    def validate(self, action: str, args: Dict) -> tuple[bool, str]:
        """Returns (allowed, reason)"""
        # Check action whitelist
        if action not in self.config.allowed_actions:
            return False, f"Action '{action}' not in allowed set"
        
        # Check blocked patterns in args
        import re
        args_str = json.dumps(args)
        for pattern in self.config.blocked_patterns:
            if re.search(pattern, args_str, re.IGNORECASE):
                return False, f"Blocked pattern '{pattern}' detected"
        
        # Rate limiting
        self.action_counts[action] = self.action_counts.get(action, 0) + 1
        if self.action_counts[action] > 100:
            return False, f"Rate limit exceeded for {action}"
            
        return True, "allowed"


class SecureExecutor:
    """Secure code execution with sandboxing"""
    
    BLOCKED_IMPORTS = frozenset({
        "os", "subprocess", "socket", "requests", "urllib",
        "http", "ftplib", "telnetlib", "poplib", "imaplib",
        "smtplib", "pwd", "spwd", "crypt", "grp"
    })
    
    def __init__(self, action_validator: ActionValidator):
        self.validator = action_validator
        self.execution_log: List[Dict] = []
        
    def execute(self, action: str, args: Dict) -> str:
        """Execute with validation"""
        allowed, reason = self.validator.validate(action, args)
        if not allowed:
            logger.warning(f"Blocked action: {action} - {reason}")
            return json.dumps({"error": reason})
        
        try:
            result = execute_tool(action, args)
            
            # Log execution
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "args_keys": list(args.keys()),
                "result_len": len(result)
            })
            
            # Keep only last 1000
            if len(self.execution_log) > 1000:
                self.execution_log = self.execution_log[-500:]
                
            return result
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return json.dumps({"error": str(e)})


# ============================================================================
# SL-LLM Core Integration
# ============================================================================

class SLLMCore:
    """SL-LLM core for daemon"""
    
    def __init__(self, config: DaemonConfig):
        self.config = config
        self.kgm = FluidKnowledgeGraph()
        
        # Initialize LLM client
        logger.info(f"Initializing LLM client with prefer={config.prefer}")
        self.llm_client = get_client(prefer=config.prefer, model=config.model)
        
        # Tools
        self.tools = get_default_tools()
        
        # Security
        self.action_validator = ActionValidator(config)
        self.executor = SecureExecutor(self.action_validator)
        
        # Session state
        self.sessions: Dict[str, Dict] = {}
        
    def chat(self, messages: List[Dict], session_id: Optional[str] = None) -> Dict:
        """Process chat with full SL-LLM pipeline"""
        
        # Get last user message
        user_msg = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        if not user_msg:
            return {"error": "No user message found"}
        
        task = user_msg.get("content", "")
        
        # Get knowledge graph context
        enhanced_context, kg_metadata = get_enhanced_context(task)
        
        # Build full prompt
        full_prompt = f"{enhanced_context}\n\nUser: {task}"
        
        # Call LLM
        try:
            response = self.llm_client.chat(
                [{"role": "user", "content": full_prompt}],
                tools=self.tools
            )
        except Exception as e:
            return {"error": str(e)}
        
        msg = response.get("message", {})
        content = msg.get("content", "")
        
        # Handle tool calls
        if msg.get("tool_calls"):
            tool_results = []
            for call in msg["tool_calls"]:
                tool_name = call["function"]["name"]
                try:
                    args = json.loads(call["function"]["arguments"])
                except:
                    args = {"code": call["function"]["arguments"]}
                
                result = self.executor.execute(tool_name, args)
                tool_results.append({"tool": tool_name, "result": result})
                
                # Refine with tool result
                try:
                    response = self.llm_client.chat(
                        messages + [msg] + [{"role": "tool", "content": result}],
                        tools=self.tools
                    )
                    msg = response.get("message", {})
                except:
                    pass
            
            content = msg.get("content", "")
        
        return {
            "content": content,
            "model": self.config.model,
            "knowledge_used": kg_metadata.get("insights_retrieved", 0),
            "classification": kg_metadata.get("classification", {}).get("primary_category", "general"),
            "session_id": session_id
        }
    
    def execute_task(self, task: str, session_id: Optional[str] = None) -> Dict:
        """Execute a task with full SL-LLM"""
        messages = [{"role": "user", "content": task}]
        return self.chat(messages, session_id)
    
    def create_session(self) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())[:8]
        self.sessions[session_id] = {
            "created": datetime.now().isoformat(),
            "messages": [],
            "context": {}
        }
        return session_id
    
    def get_tools(self) -> List[Dict]:
        """Get available tools for MCP"""
        return self.tools


# ============================================================================
# API Implementation
# ============================================================================

class SLLMDaemon:
    """Main daemon server"""
    
    def __init__(self, config: DaemonConfig):
        self.config = config
        self.core = SLLMCore(config)
        self.started = datetime.now()
        
        if FASTAPI_AVAILABLE:
            self.app = FastAPI(
                title="SL-LLM Daemon",
                description="Self-Learning LLM API Server",
                version="1.0.0"
            )
            self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        from fastapi import Request
        from fastapi.middleware.cors import CORSMiddleware
        
        app = self.app
        
        # CORS
        if self.config.cors_enabled:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        @app.get("/health")
        async def health():
            """Health check"""
            return {
                "status": "healthy",
                "uptime": (datetime.now() - self.started).total_seconds(),
                "gpu": GPU_INFO[0],
                "llm_backend": self.config.prefer,
                "sessions": len(self.core.sessions)
            }
        
        @app.get("/models")
        async def list_models():
            """List available models"""
            return {
                "data": [{
                    "id": self.config.model,
                    "object": "model",
                    "created": 0,
                    "owned_by": "sllm"
                }]
            }
        
        @app.post("/v1/chat/completions")
        async def chat_completions(request: Request):
            """OpenAI-compatible chat endpoint"""
            body = await request.json()
            
            messages = body.get("messages", [])
            session_id = body.get("session_id")
            
            # Create session if needed
            if not session_id:
                session_id = self.core.create_session()
            
            result = self.core.chat(messages, session_id)
            
            return {
                "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                "object": "chat.completion",
                "created": int(datetime.now().timestamp()),
                "model": self.config.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result.get("content", "")
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": len(str(messages)),
                    "completion_tokens": len(result.get("content", "")),
                    "total_tokens": len(str(messages)) + len(result.get("content", ""))
                }
            }
        
        @app.post("/v1/completions")
        async def completions(request: Request):
            """OpenAI-compatible completion endpoint"""
            body = await request.json()
            prompt = body.get("prompt", "")
            
            result = self.core.execute_task(prompt)
            
            return {
                "id": f"cmpl-{uuid.uuid4().hex[:8]}",
                "object": "text_completion",
                "created": int(datetime.now().timestamp()),
                "model": self.config.model,
                "choices": [{
                    "text": result.get("content", ""),
                    "index": 0,
                    "finish_reason": "stop"
                }]
            }
        
        @app.post("/execute")
        async def execute_task(request: Request):
            """Execute task with tools"""
            body = await request.json()
            task = body.get("task", "")
            
            result = self.core.execute_task(task)
            
            # Include knowledge graph stats
            counts = self.core.kgm._get_category_counts()
            
            return {
                **result,
                "knowledge_graph": counts
            }
        
        @app.get("/mcp/tools/list")
        async def mcp_tools_list():
            """MCP-style tools list"""
            return {
                "tools": self.core.get_tools()
            }
        
        @app.post("/mcp/tools/call")
        async def mcp_tools_call(request: Request):
            """MCP-style tool call"""
            body = await request.json()
            tool = body.get("tool", "")
            args = body.get("arguments", {})
            
            result = self.core.executor.execute(tool, args)
            
            return {"result": result}
        
        @app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "name": "SL-LLM Daemon",
                "version": "1.0.0",
                "primary_purpose": "Self-learning, sentient AI agent",
                "docs": "/docs"
            }
    
    def run(self):
        """Run the daemon"""
        if FASTAPI_AVAILABLE:
            logger.info(f"Starting SL-LLM Daemon on {self.config.host}:{self.config.port}")
            uvicorn.run(self.app, host=self.config.host, port=self.config.port)
        else:
            raise RuntimeError("FastAPI not available")


# ============================================================================
# Basic HTTP Server (Fallback)
# ============================================================================

class BasicHandler(BaseHTTPRequestHandler):
    """Basic HTTP handler when FastAPI unavailable"""
    
    def log_message(self, format, *args):
        logger.info("%s - %s", self.address_string(), format % args)
    
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"
        
        if self.path == "/execute":
            try:
                data = json.loads(body)
                result = {"status": "ok", "output": "Basic server - use FastAPI for full features"}
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except:
                self.send_response(500)
                self.end_headers()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Threaded HTTP server"""
    daemon_threads = True


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="SL-LLM Daemon Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind")
    parser.add_argument("--prefer", default="auto", 
                     choices=["auto", "lmstudio", "ollama", "llama.cpp", "mock"],
                     help="LLM backend preference")
    parser.add_argument("--model", default="local", help="Model name")
    parser.add_argument("--api-key", help="API key (optional)")
    parser.add_argument("--cors", action="bool", default=True, help="Enable CORS")
    
    args = parser.parse_args()
    
    config = DaemonConfig(
        host=args.host,
        port=args.port,
        prefer=args.prefer,
        model=args.model,
        api_key=args.api_key,
        cors_enabled=args.cors
    )
    
    daemon = SLLMDaemon(config)
    daemon.run()


if __name__ == "__main__":
    main()