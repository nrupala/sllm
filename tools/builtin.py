import json
import subprocess
from pathlib import Path


def file_read(args: dict) -> str:
    try:
        path = Path(args["path"])
        if not path.exists():
            return f"File not found: {args['path']}"
        return path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error: {e}"


def file_write(args: dict) -> str:
    try:
        path = Path(args["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(args["content"], encoding="utf-8")
        return f"Written to {args['path']}"
    except Exception as e:
        return f"Error: {e}"


def list_directory(args: dict) -> str:
    try:
        path = Path(args.get("path", "."))
        if not path.exists():
            return f"Directory not found"
        items = [f"{p.name}" + ("/" if p.is_dir() else "") for p in path.iterdir()]
        return "\n".join(sorted(items)) if items else "Empty"
    except Exception as e:
        return f"Error: {e}"


def execute_code(args: dict) -> str:
    import tempfile, os
    timeout = args.get("timeout", 30)
    code = args.get("code", "")
    
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(code)
            temp_path = f.name
        
        result = subprocess.run(["python", temp_path], capture_output=True, text=True, timeout=timeout)
        os.unlink(temp_path)
        
        out = result.stdout
        if result.stderr:
            out += "\n[STDERR]\n" + result.stderr
        return out or "No output"
    except subprocess.TimeoutExpired:
        return f"Timeout ({timeout}s)"
    except Exception as e:
        return f"Error: {e}"


def search_code(args: dict) -> str:
    pattern = args.get("pattern", "")
    path = Path(args.get("path", "D:/sl/projects/sllm"))
    ext = args.get("file_type", ".py")
    
    results = []
    try:
        for p in path.rglob(f"*{ext}"):
            try:
                if pattern in p.read_text(encoding="utf-8"):
                    results.append(str(p))
            except:
                pass
    except:
        pass
    
    return "\n".join(results[:20]) if results else "No matches"


def get_system_info(args: dict) -> str:
    import platform, psutil
    return json.dumps({
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu": psutil.cpu_count(),
        "ram_gb": round(psutil.virtual_memory().available / (1024**3), 1)
    })


TOOL_FUNCTIONS = {
    "file_read": file_read,
    "file_write": file_write,
    "list_directory": list_directory,
    "execute_code": execute_code,
    "search_code": search_code,
    "get_system_info": get_system_info
}


TOOLS = [
    {"type": "function", "function": {"name": "file_read", "description": "Read file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "file_write", "description": "Write file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "list_directory", "description": "List directory", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "execute_code", "description": "Run Python code", "parameters": {"type": "object", "properties": {"code": {"type": "string"}, "timeout": {"type": "integer"}}, "required": ["code"]}}},
    {"type": "function", "function": {"name": "search_code", "description": "Search in files", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}, "file_type": {"type": "string"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {"name": "get_system_info", "description": "System info", "parameters": {"type": "object", "properties": {}}}}
]


def get_default_tools():
    return TOOLS


def execute_tool(name: str, args: dict) -> str:
    return TOOL_FUNCTIONS.get(name, lambda a: f"Unknown: {name}")(args)