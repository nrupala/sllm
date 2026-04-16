"""
SL-LLM MCP Gateway Integration
Provides MCP protocol endpoints for external tool integration
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPTool:
    """Represents an MCP tool"""
    def __init__(self, name: str, description: str, input_schema: Dict):
        self.name = name
        self.description = description
        self.input_schema = input_schema
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


class MCPGateway:
    """
    MCP Gateway - connects SL-LLM to external tools via MCP protocol
    Supports: Claude skills, Cursor skills, MstyStudio skills, Azure tools
    """
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_all_tools()
    
    def _register_all_tools(self):
        """Register all available tools from all sources"""
        
        # SL-LLM Core Tools
        self.register_tool(MCPTool(
            name="slll_generate",
            description="Generate text using SL-LLM",
            input_schema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "temperature": {"type": "number", "default": 0.7},
                    "max_tokens": {"type": "number", "default": 2048}
                },
                "required": ["prompt"]
            }
        ))
        
        self.register_tool(MCPTool(
            name="slll_chat",
            description="Chat with SL-LLM with conversation history",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "session_id": {"type": "string"},
                    "model": {"type": "string"}
                },
                "required": ["message"]
            }
        ))
        
        self.register_tool(MCPTool(
            name="slll_code",
            description="Generate code using SL-LLM",
            input_schema={
                "type": "object",
                "properties": {
                    "task": {"type": "string"},
                    "language": {"type": "string"},
                    "model": {"type": "string"}
                },
                "required": ["task"]
            }
        ))
        
        # Agent Design Tools (from Claude/MstyStudio)
        self.register_tool(MCPTool(
            name="design_agent_architecture",
            description="Design multi-agent system architecture",
            input_schema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "enum": ["supervisor", "swarm", "hierarchical", "pipeline"]},
                    "agents": {"type": "array"},
                    "task": {"type": "string"}
                },
                "required": ["pattern", "task"]
            }
        ))
        
        self.register_tool(MCPTool(
            name="design_tool_schema",
            description="Design MCP tool schema with validation",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "parameters": {"type": "object"}
                },
                "required": ["name", "description"]
            }
        ))
        
        # Code Review Tools
        self.register_tool(MCPTool(
            name="analyze_pr",
            description="Analyze PR for complexity and risks",
            input_schema={
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                    "base_branch": {"type": "string"},
                    "head_branch": {"type": "string"}
                },
                "required": ["repo_path"]
            }
        ))
        
        self.register_tool(MCPTool(
            name="check_code_quality",
            description="Check code quality for issues",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "language": {"type": "string"}
                },
                "required": ["path"]
            }
        ))
        
        # Development Tools
        self.register_tool(MCPTool(
            name="create_feature",
            description="Create new feature with TDD approach",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "stack": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["name", "stack"]
            }
        ))
        
        # Security Tools
        self.register_tool(MCPTool(
            name="security_review",
            description="Perform security best practices review",
            input_schema={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "language": {"type": "string"},
                    "framework": {"type": "string"}
                },
                "required": ["path"]
            }
        ))
        
        # Research Tools
        self.register_tool(MCPTool(
            name="deep_research",
            description="Conduct in-depth research on topic",
            input_schema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "depth": {"type": "string", "enum": ["quick", "medium", "very thorough"]},
                    "output_format": {"type": "string"}
                },
                "required": ["topic"]
            }
        ))
        
        # Strategy Tools
        self.register_tool(MCPTool(
            name="plan_launch",
            description="Plan product launch strategy",
            input_schema={
                "type": "object",
                "properties": {
                    "product": {"type": "string"},
                    "target": {"type": "string"},
                    "channels": {"type": "array"}
                },
                "required": ["product"]
            }
        ))
        
        # Cursor-specific tools
        self.register_tool(MCPTool(
            name="babysit_pr",
            description="Keep PR merge-ready (Cursor skill)",
            input_schema={
                "type": "object",
                "properties": {
                    "pr_url": {"type": "string"}
                },
                "required": ["pr_url"]
            }
        ))
        
        self.register_tool(MCPTool(
            name="create_skill",
            description="Create new skill (Cursor skill)",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["name"]
            }
        ))
        
        logger.info(f"Registered {len(self.tools)} MCP tools")
    
    def register_tool(self, tool: MCPTool):
        """Register a tool"""
        self.tools[tool.name] = tool
    
    def list_tools(self) -> List[Dict]:
        """List all available tools"""
        return [t.to_dict() for t in self.tools.values()]
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a specific tool"""
        return self.tools.get(name)
    
    async def execute_tool(self, name: str, arguments: Dict) -> Dict:
        """Execute a tool"""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool {name} not found"}
        
        # Validate arguments
        required = tool.input_schema.get("required", [])
        for field in required:
            if field not in arguments:
                return {"error": f"Missing required field: {field}"}
        
        # Execute based on tool type
        try:
            result = await self._execute(name, arguments)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}
    
    async def _execute(self, name: str, args: Dict) -> Any:
        """Execute specific tool logic"""
        if name.startswith("slll_"):
            return await self._execute_slll(name, args)
        elif name.startswith("design_"):
            return await self._execute_design(name, args)
        elif name.startswith("analyze") or name.startswith("check_"):
            return await self._execute_analysis(name, args)
        else:
            return f"Tool {name} executed with args: {args}"
    
    async def _execute_slll(self, name: str, args: Dict) -> Any:
        """Execute SL-LLM native tools"""
        # Import and use SL-LLM core
        try:
            from core.sl_llm_agent import create_agent
            agent = create_agent()
            
            if name == "slll_generate":
                return agent.generate(args.get("prompt", ""), 
                                     temperature=args.get("temperature", 0.7),
                                     max_tokens=args.get("max_tokens", 2048))
            elif name == "slll_chat":
                return agent.generate(args.get("message", ""), 
                                     session_id=args.get("session_id"))
            elif name == "slll_code":
                return agent.generate(f"Write {args.get('language', 'code')}: {args.get('task')}")
        except Exception as e:
            return f"Error: {e}"
        
        return "Tool execution placeholder"
    
    async def _execute_design(self, name: str, args: Dict) -> Any:
        """Execute agent design tools"""
        return {
            "pattern": args.get("pattern"),
            "architecture": "Designed based on pattern requirements",
            "agents": args.get("agents", [])
        }
    
    async def _execute_analysis(self, name: str, args: Dict) -> Any:
        """Execute code analysis tools"""
        return {
            "path": args.get("path"),
            "analysis": "Code analysis placeholder",
            "issues": []
        }


# MCP Gateway Server
class MCPGatewayServer:
    """HTTP server for MCP Gateway"""
    
    def __init__(self, gateway: MCPGateway):
        self.gateway = gateway
    
    def get_routes(self):
        """Get Flask-style routes"""
        from flask import jsonify
        
        routes = {}
        
        def list_tools():
            return jsonify({"tools": self.gateway.list_tools()})
        routes["/mcp/tools"] = list_tools
        
        def get_tool(name):
            tool = self.gateway.gateway.get_tool(name)
            if tool:
                return jsonify(tool.to_dict())
            return jsonify({"error": "Tool not found"}), 404
        routes[f"/mcp/tools/<name>"] = get_tool
        
        async def execute_tool(request):
            from flask import request as flask_request
            data = flask_request.json
            result = await self.gateway.execute_tool(data.get("name"), data.get("arguments", {}))
            return jsonify(result)
        routes["/mcp/execute"] = execute_tool
        
        return routes


# Singleton
_mcp_gateway = None

def get_mcp_gateway() -> MCPGateway:
    global _mcp_gateway
    if _mcp_gateway is None:
        _mcp_gateway = MCPGateway()
    return _mcp_gateway


if __name__ == "__main__":
    gateway = get_mcp_gateway()
    print(f"=== SL-LLM MCP Gateway ===")
    print(f"Total tools: {len(gateway.tools)}")
    print("\nTools:")
    for name in list(gateway.tools.keys())[:10]:
        print(f"  - {name}")