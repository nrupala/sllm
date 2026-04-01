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


# === VANILLA TOOLS (No External Dependencies) ===

def git_operations(args: dict) -> str:
    """Git operations via subprocess - no external deps"""
    import subprocess
    import os
    
    command = args.get("command", "status")
    repo_path = args.get("path", ".")
    
    git_commands = {
        "status": ["git", "status", "--porcelain"],
        "log": ["git", "log", "--oneline", "-10"],
        "diff": ["git", "diff", "--stat"],
        "branch": ["git", "branch", "-a"],
        "remote": ["git", "remote", "-v"],
        "commit": ["git", "commit", "-m", args.get("message", "Auto-commit")],
        "push": ["git", "push"],
        "pull": ["git", "pull"],
    }
    
    cmd = git_commands.get(command, ["git", command])
    
    try:
        result = subprocess.run(
            cmd, cwd=repo_path, capture_output=True, text=True, timeout=30
        )
        return result.stdout + result.stderr if result.stderr else result.stdout or "Done"
    except Exception as e:
        return f"Git error: {e}"


def web_search(args: dict) -> str:
    """Web search via urllib - no external deps"""
    import urllib.parse
    import urllib.request
    import json
    
    query = args.get("query", "")
    if not query:
        return "No query provided"
    
    try:
        encoded = urllib.parse.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8")
        
        results = []
        import re
        for match in re.findall(r'<a class="result__a" href="([^"]*)"[^>]*>([^<]*)</a>', html)[:5]:
            results.append(f"{match[1]}: {match[0]}")
        
        return "\n".join(results) if results else "No results found"
    except Exception as e:
        return f"Search error: {e}"


def database_ops(args: dict) -> str:
    """SQLite database operations - no external deps"""
    import sqlite3
    import json
    
    operation = args.get("operation", "query")
    db_path = args.get("db_path", "data.db")
    query = args.get("query", "")
    table = args.get("table", "items")
    data = args.get("data", {})
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if operation == "create":
            columns = args.get("columns", "id INTEGER PRIMARY KEY, data TEXT")
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns})")
            conn.commit()
            return f"Table {table} created"
        
        elif operation == "insert":
            if isinstance(data, str):
                data = json.loads(data) if data else {}
            keys = ", ".join(data.keys())
            placeholders = ", ".join(["?"] * len(data))
            cursor.execute(f"INSERT INTO {table} ({keys}) VALUES ({placeholders})", list(data.values()))
            conn.commit()
            return f"Inserted into {table}"
        
        elif operation == "query":
            cursor.execute(query)
            rows = cursor.fetchall()
            return "\n".join(str(r) for r in rows) if rows else "No results"
        
        elif operation == "update":
            set_clause = args.get("set", "")
            where = args.get("where", "1=1")
            cursor.execute(f"UPDATE {table} SET {set_clause} WHERE {where}")
            conn.commit()
            return f"Updated {cursor.rowcount} rows"
        
        elif operation == "delete":
            where = args.get("where", "1=1")
            cursor.execute(f"DELETE FROM {table} WHERE {where}")
            conn.commit()
            return f"Deleted {cursor.rowcount} rows"
        
        conn.close()
        return "Done"
    
    except Exception as e:
        return f"Database error: {e}"


def http_request(args: dict) -> str:
    """HTTP requests via urllib - no external deps"""
    import urllib.request
    import urllib.parse
    import json
    import base64
    
    method = args.get("method", "GET")
    url = args.get("url", "")
    headers = args.get("headers", {})
    body = args.get("body", "")
    
    if not url:
        return "No URL provided"
    
    try:
        req = urllib.request.Request(url, method=method)
        
        for key, value in headers.items():
            req.add_header(key, value)
        
        if body:
            if isinstance(body, dict):
                body = json.dumps(body).encode("utf-8")
                req.add_header("Content-Type", "application/json")
            else:
                body = body.encode("utf-8")
            req.data = body
        
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.status
            headers = dict(response.headers)
            content = response.read().decode("utf-8")
        
        return json.dumps({
            "status": status,
            "headers": headers,
            "body": content[:2000]
        }, indent=2)
    
    except Exception as e:
        return f"HTTP error: {e}"


# Add new tools to registry
TOOL_FUNCTIONS.update({
    "git_operations": git_operations,
    "web_search": web_search,
    "database_ops": database_ops,
    "http_request": http_request
})

TOOLS.extend([
    {"type": "function", "function": {"name": "git_operations", "description": "Git operations (status, log, diff, branch, commit, push)", "parameters": {"type": "object", "properties": {"command": {"type": "string", "enum": ["status", "log", "diff", "branch", "remote", "commit", "push", "pull"]}, "path": {"type": "string"}, "message": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "web_search", "description": "Search the web", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
    {"type": "function", "function": {"name": "database_ops", "description": "SQLite database operations", "parameters": {"type": "object", "properties": {"operation": {"type": "string", "enum": ["create", "insert", "query", "update", "delete"]}, "db_path": {"type": "string"}, "table": {"type": "string"}, "query": {"type": "string"}, "data": {"type": "object"}, "columns": {"type": "string"}, "set": {"type": "string"}, "where": {"type": "string"}}, "required": ["operation"]}}},
    {"type": "function", "function": {"name": "http_request", "description": "HTTP request (GET, POST, PUT, DELETE)", "parameters": {"type": "object", "properties": {"method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]}, "url": {"type": "string"}, "headers": {"type": "object"}, "body": {"type": "string"}}, "required": ["url"]}}}
])