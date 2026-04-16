"""
SL-LLM MCP Integration
Provides MCP server capabilities for SL-LLM including Playwright for browser automation.

MCP Servers included:
- Playwright browser automation
- File system operations
- Git operations
- Knowledge Graph access
- Code execution

Usage:
    python mcp_server.py              # Start MCP server
    python mcp_server.py --playwright  # With Playwright browser automation
    python mcp_server.py --port 8931   # Custom port
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("sllm-mcp")

# Try imports
PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    logger.warning("Playwright not installed - browser automation disabled")

# SL-LLM imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.client import get_client, detect_gpu
from tools.builtin import get_default_tools, execute_tool
from knowledge_graph_manager import FluidKnowledgeGraph


# ============================================================================
# MCP Protocol Types
# ============================================================================

@dataclass
class MCPRequest:
    """MCP JSON-RPC request"""
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    method: str = ""
    params: Dict = None
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}


@dataclass
class MCPResponse:
    """MCP JSON-RPC response"""
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    result: Any = None
    error: Optional[Dict] = None


# ============================================================================
# Tool Definitions (MCP Style)
# ============================================================================

def get_sllm_tools() -> List[Dict]:
    """Get SL-LLM tools in MCP format"""
    return [
        {
            "name": "sllm_execute_task",
            "description": "Execute a coding task with SL-LLM's self-learning capabilities",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Task description"},
                    "max_iterations": {"type": "integer", "default": 5}
                },
                "required": ["task"]
            }
        },
        {
            "name": "file_read",
            "description": "Read a file from the filesystem",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        },
        {
            "name": "file_write",
            "description": "Write content to a file",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        },
        {
            "name": "execute_code",
            "description": "Execute Python code in a sandbox",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "timeout": {"type": "integer", "default": 30}
                },
                "required": ["code"]
            }
        },
        {
            "name": "search_code",
            "description": "Search for patterns in code files",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string", "default": "."},
                    "file_type": {"type": "string", "default": ".py"}
                },
                "required": ["pattern"]
            }
        },
        {
            "name": "list_directory",
            "description": "List directory contents",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": "."}
                }
            }
        },
        {
            "name": "git_operations",
            "description": "Git operations (status, log, diff, commit)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "enum": ["status", "log", "diff", "branch", "commit"]},
                    "path": {"type": "string", "default": "."},
                    "message": {"type": "string"}
                },
                "required": ["command"]
            }
        },
        {
            "name": "get_system_info",
            "description": "Get system information",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "web_search",
            "description": "Search the web",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "kg_query",
            "description": "Query the Knowledge Graph for relevant insights",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "category": {"type": "string", "default": "all"},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        }
    ]


# ============================================================================
# Playwright Browser Automation
# ============================================================================

class PlaywrightBrowser:
    """Playwright browser automation for MCP"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.pages: List[Any] = []
        
    async def initialize(self):
        """Initialize Playwright"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        
    async def navigate(self, url: str) -> Dict:
        """Navigate to URL"""
        if not self.browser:
            await self.initialize()
            
        page = await self.context.new_page()
        await page.goto(url)
        self.pages.append(page)
        
        return {"status": "ok", "url": url, "title": await page.title()}
    
    async def snapshot(self) -> Dict:
        """Get accessibility snapshot of current page"""
        if not self.pages:
            return {"error": "No page open"}
            
        page = self.pages[-1]
        snapshot = await page.accessibility.snapshot()
        
        return {
            "snapshot": snapshot,
            "url": page.url,
            "title": await page.title()
        }
    
    async def click(self, selector: str) -> Dict:
        """Click element"""
        if not self.pages:
            return {"error": "No page open"}
            
        page = self.pages[-1]
        await page.click(selector)
        
        return {"status": "ok", "selector": selector}
    
    async def type(self, selector: str, text: str) -> Dict:
        """Type text into element"""
        if not self.pages:
            return {"error": "No page open"}
            
        page = self.pages[-1]
        await page.fill(selector, text)
        
        return {"status": "ok", "selector": selector, "text": text}
    
    async def evaluate(self, code: str) -> Dict:
        """Evaluate JavaScript in page context"""
        if not self.pages:
            return {"error": "No page open"}
            
        page = self.pages[-1]
        result = await page.evaluate(code)
        
        return {"status": "ok", "result": result}
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# ============================================================================
# MCP Server Implementation
# ============================================================================

class SLLMMCPServer:
    """MCP Server for SL-LLM"""
    
    def __init__(self, with_playwright: bool = False):
        self.with_playwright = with_playwright
        self.browser = None
        self.kgm = FluidKnowledgeGraph()
        self.llm_client = get_client()
        self.tools = get_default_tools()
        
    async def initialize(self):
        """Initialize server"""
        if self.with_playwright and PLAYWRIGHT_AVAILABLE:
            self.browser = PlaywrightBrowser()
            await self.browser.initialize()
            logger.info("Playwright initialized")
        
        # Initialize LLM client
        logger.info(f"SL-LLM MCP Server initialized")
    
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP request"""
        method = request.method
        params = request.params or {}
        request_id = request.id
        
        try:
            result = await self._dispatch(method, params)
            return MCPResponse(id=request_id, result=result)
        except Exception as e:
            logger.error(f"Error in {method}: {e}")
            return MCPResponse(
                id=request_id,
                error={"code": -32603, "message": str(e)}
            )
    
    async def _dispatch(self, method: str, params: Dict) -> Any:
        """Dispatch to handler"""
        
        # Tool listing
        if method == "tools/list":
            return {"tools": get_sllm_tools()}
        
        if method == "tools/call":
            tool = params.get("name")
            args = params.get("arguments", {})
            return await self._call_tool(tool, args)
        
        # Tool execution
        if method.startswith("sllm_"):
            return await self._call_tool(method, params)
        
        return {"error": f"Unknown method: {method}"}
    
    async def _call_tool(self, tool: str, args: Dict) -> Any:
        """Call a tool"""
        
        # SL-LLM task execution
        if tool == "sllm_execute_task":
            task = args.get("task", "")
            max_iter = args.get("max_iterations", 5)
            
            from knowledge_graph_manager import get_enhanced_context
            enhanced_context, kg_metadata = get_enhanced_context(task)
            
            full_prompt = f"{enhanced_context}\n\nTask: {task}"
            
            response = self.llm_client.chat(
                [{"role": "user", "content": full_prompt}],
                tools=self.tools
            )
            
            msg = response.get("message", {})
            content = msg.get("content", "")
            
            # Handle tool calls
            if msg.get("tool_calls"):
                for call in msg["tool_calls"]:
                    tool_name = call["function"]["name"]
                    try:
                        t_args = json.loads(call["function"]["arguments"])
                    except:
                        t_args = {"code": call["function"]["arguments"]}
                    
                    result = execute_tool(tool_name, t_args)
                    
                    # Refine
                    response = self.llm_client.chat(
                        [{"role": "user", "content": full_prompt},
                         msg,
                         {"role": "tool", "content": result}],
                        tools=self.tools
                    )
                    msg = response.get("message", {})
                
                content = msg.get("content", "")
            
            return {
                "content": content,
                "knowledge_used": kg_metadata.get("insights_retrieved", 0)
            }
        
        # Knowledge Graph
        if tool == "kg_query":
            query = args.get("query", "")
            category = args.get("category", "all")
            limit = args.get("limit", 5)
            
            from knowledge_graph_manager import retrieve_insights
            insights = retrieve_insights(query, category=category, limit=limit)
            
            return {"insights": insights}
        
        # File tools
        if tool in ["file_read", "file_write", "execute_code", "list_directory", 
                   "search_code", "get_system_info", "git_operations", "web_search"]:
            return execute_tool(tool, args)
        
        # Playwright tools
        if self.browser and tool in ["browser_navigate", "browser_snapshot", 
                                    "browser_click", "browser_type", "browser_evaluate"]:
            return await self._playwright_tool(tool, args)
        
        return {"error": f"Unknown tool: {tool}"}
    
    async def _playwright_tool(self, tool: str, args: Dict) -> Any:
        """Handle Playwright tool calls"""
        
        if tool == "browser_navigate":
            return await self.browser.navigate(args.get("url", ""))
        elif tool == "browser_snapshot":
            return await self.browser.snapshot()
        elif tool == "browser_click":
            return await self.browser.click(args.get("selector", ""))
        elif tool == "browser_type":
            return await self.browser.type(
                args.get("selector", ""),
                args.get("text", "")
            )
        elif tool == "browser_evaluate":
            return await self.browser.evaluate(args.get("code", ""))
        
        return {"error": f"Unknown browser tool: {tool}"}
    
    async def shutdown(self):
        """Shutdown server"""
        if self.browser:
            await self.browser.close()


# ============================================================================
# MCP Transport (stdio)
# ============================================================================

async def handle_stdio(server: SLLMMCPServer):
    """Handle stdio JSON-RPC communication"""
    import sys
    
    buffer = ""
    
    while True:
        try:
            char = sys.stdin.read(1)
            if not char:
                break
            
            if char == '\n':
                try:
                    request_data = json.loads(buffer)
                    request = MCPRequest(**request_data)
                    response = await server.handle_request(request)
                    
                    # Write response
                    print(json.dumps({
                        "jsonrpc": response.jsonrpc,
                        "id": response.id,
                        "result": response.result,
                        "error": response.error
                    }), flush=True)
                    
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    logger.error(f"Error: {e}")
                
                buffer = ""
            else:
                buffer += char
                
        except KeyboardInterrupt:
            break
        except EOFError:
            break


# ============================================================================
# Main
# ============================================================================

import asyncio

def main():
    parser = argparse.ArgumentParser(description="SL-LLM MCP Server")
    parser.add_argument("--playwright", action="store_true", help="Enable Playwright browser automation")
    parser.add_argument("--port", type=int, default=8931, help="Port for HTTP transport")
    args = parser.parse_args()
    
    async def run():
        server = SLLMMCPServer(with_playwright=args.playwright)
        await server.initialize()
        
        # Check if HTTP or stdio
        if os.environ.get("MCP_TRANSPORT") == "http":
            # HTTP transport would need uvicorn/fastapi
            logger.info(f"MCP Server running on port {args.port}")
            await asyncio.sleep(float('inf'))
        else:
            # stdio transport
            logger.info("MCP Server running (stdio mode)")
            await handle_stdio(server)
        
        await server.shutdown()
    
    asyncio.run(run())


if __name__ == "__main__":
    main()