"""
SL-LLM Production GUI
Full production ecosystem with model selection, engine selection, and monitoring.
"""
from flask import Flask, render_template_string, jsonify, request
import os
import threading
import platform

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SL-LLM Production Console</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', system-ui, sans-serif; 
            background: #0d1117; color: #c9d1d9; margin: 0; padding: 0; 
        }
        .header { 
            background: #161b22; padding: 15px 20px; border-bottom: 1px solid #30363d;
            display: flex; justify-content: space-between; align-items: center;
        }
        .header h1 { margin: 0; color: #58a6ff; font-size: 1.4rem; }
        .header .badge { background: #238636; color: #fff; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; }
        
        .container { display: flex; min-height: 100vh; }
        .sidebar { 
            width: 260px; background: #161b22; border-right: 1px solid #30363d; 
            padding: 15px; overflow-y: auto;
        }
        .main { flex: 1; padding: 20px; overflow-y: auto; }
        
        .section { margin-bottom: 20px; }
        .section-title { 
            color: #8b949e; font-size: 0.75rem; text-transform: uppercase; 
            margin-bottom: 10px; letter-spacing: 0.5px;
        }
        
        .card { 
            background: #21262d; border: 1px solid #30363d; border-radius: 6px; 
            padding: 15px; margin-bottom: 10px;
        }
        .card:hover { border-color: #58a6ff; }
        
        label { display: block; color: #8b949e; font-size: 0.85rem; margin-bottom: 5px; }
        select, input, textarea { 
            width: 100%; background: #0d1117; color: #c9d1d9; 
            border: 1px solid #30363d; border-radius: 6px; padding: 8px 12px;
            font-size: 0.9rem; margin-bottom: 10px;
        }
        select:focus, input:focus, textarea:focus { outline: none; border-color: #58a6ff; }
        
        .btn { 
            background: #238636; color: #fff; border: none; border-radius: 6px;
            padding: 8px 16px; cursor: pointer; font-size: 0.9rem;
        }
        .btn:hover { background: #2ea043; }
        .btn:disabled { background: #30363d; cursor: not-allowed; }
        .btn-secondary { background: #21262d; border: 1px solid #30363d; }
        .btn-secondary:hover { background: #30363d; }
        
        .model-list { max-height: 200px; overflow-y: auto; }
        .model-item { 
            padding: 8px 10px; border-radius: 4px; cursor: pointer; margin-bottom: 4px;
        }
        .model-item:hover { background: #30363d; }
        .model-item.active { background: #1f6feb; color: #fff; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .stat { background: #0d1117; padding: 10px; border-radius: 6px; text-align: center; }
        .stat-value { font-size: 1.5rem; font-weight: bold; color: #58a6ff; }
        .stat-label { font-size: 0.75rem; color: #8b949e; }
        
        pre { 
            background: #0d1117; padding: 15px; border-radius: 6px; 
            overflow-x: auto; white-space: pre-wrap; font-size: 0.85rem;
            max-height: 400px; border: 1px solid #30363d;
        }
        
        .status-dot { 
            display: inline-block; width: 8px; height: 8px; border-radius: 50%;
            margin-right: 5px;
        }
        .status-dot.online { background: #238636; }
        .status-dot.offline { background: #da3633; }
        
        .tabs { display: flex; border-bottom: 1px solid #30363d; margin-bottom: 15px; }
        .tab { 
            padding: 10px 20px; cursor: pointer; color: #8b949e; border-bottom: 2px solid transparent;
        }
        .tab:hover { color: #c9d1d9; }
        .tab.active { color: #58a6ff; border-bottom-color: #58a6ff; }
        
        .console-input { 
            display: flex; gap: 10px; margin-top: 15px; 
        }
        .console-input input { flex: 1; margin-bottom: 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>SL-LLM Production Console</h1>
        <span class="badge">v1.0</span>
    </div>
    
    <div class="container">
        <div class="sidebar">
            <div class="section">
                <div class="section-title">Engine Status</div>
                <div class="card">
                    <div id="engineStatus">
                        <span class="status-dot offline"></span> Loading...
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">System</div>
                <div class="stats-grid">
                    <div class="stat">
                        <div class="stat-value" id="cpuCount">-</div>
                        <div class="stat-label">CPU Cores</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="ramGB">-</div>
                        <div class="stat-label">RAM GB</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Select Engine</div>
                <select id="engineSelect" onchange="changeEngine()">
                    <option value="auto">Auto (Best Available)</option>
                    <option value="lmstudio">LM Studio (Local)</option>
                    <option value="ollama">Ollama (Local)</option>
                    <option value="mock">Mock (Testing)</option>
                </select>
            </div>
            
            <div class="section">
                <div class="section-title">Available Models</div>
                <select id="modelSelect" onchange="changeModel()">
                    <option value="">Loading...</option>
                </select>
            </div>
            
            <div class="section">
                <div class="section-title">Quick Actions</div>
                <button class="btn btn-secondary" style="width:100%;margin-bottom:5px" onclick="refreshModels()">Refresh Models</button>
                <button class="btn btn-secondary" style="width:100%" onclick="getSystemInfo()">System Info</button>
            </div>
        </div>
        
        <div class="main">
            <div class="tabs">
                <div class="tab active" onclick="switchTab('chat')">Chat</div>
                <div class="tab" onclick="switchTab('code')">Code Generator</div>
                <div class="tab" onclick="switchTab('history')">History</div>
            </div>
            
            <div id="chatTab">
                <div class="card">
                    <label>Model Parameters</label>
                    <div style="display:flex;gap:10px">
                        <div style="flex:1">
                            <label>Temperature</label>
                            <input type="number" id="temp" value="0.7" step="0.1" min="0" max="2">
                        </div>
                        <div style="flex:1">
                            <label>Max Tokens</label>
                            <input type="number" id="maxTokens" value="2048" step="256" min="1">
                        </div>
                    </div>
                </div>
                
                <label>Your Message</label>
                <textarea id="userMessage" rows="3" placeholder="Type your message..."></textarea>
                
                <button class="btn" onclick="sendMessage()">Send</button>
                
                <label style="margin-top:15px">Response</label>
                <pre id="response">No response yet...</pre>
            </div>
            
            <div id="codeTab" style="display:none">
                <label>Code Task</label>
                <textarea id="codeTask" rows="3" placeholder="e.g., Write a Python function to calculate fibonacci..."></textarea>
                <button class="btn" onclick="generateCode()">Generate Code</button>
                
                <label style="margin-top:15px">Generated Code</label>
                <pre id="codeOutput">No code generated yet...</pre>
            </div>
            
            <div id="historyTab" style="display:none">
                <button class="btn btn-secondary" onclick="clearHistory()">Clear History</button>
                <pre id="history">No history yet...</pre>
            </div>
        </div>
    </div>

    <script>
        let currentTab = 'chat';
        let messageHistory = [];
        
        // Initialize
        window.onload = function() {
            loadModels();
            loadSystemInfo();
        };
        
        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('chatTab').style.display = tab === 'chat' ? 'block' : 'none';
            document.getElementById('codeTab').style.display = tab === 'code' ? 'block' : 'none';
            document.getElementById('historyTab').style.display = tab === 'history' ? 'block' : 'none';
        }
        
        function loadModels() {
            fetch('/api/models')
                .then(r => r.json())
                .then(data => {
                    const select = document.getElementById('modelSelect');
                    select.innerHTML = '';
                    
                    data.models.forEach(m => {
                        const opt = document.createElement('option');
                        opt.value = m.id;
                        opt.textContent = m.name;
                        select.appendChild(opt);
                    });
                    
                    // Auto select best coding model
                    data.models.forEach(m => {
                        if (m.id.includes('qwen') && m.id.includes('coder')) {
                            select.value = m.id;
                        }
                    });
                });
        }
        
        function loadSystemInfo() {
            fetch('/api/system')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('cpuCount').textContent = data.cpu_cores;
                    document.getElementById('ramGB').textContent = Math.round(data.total_ram_gb);
                    
                    const status = document.getElementById('engineStatus');
                    if (data.provider === 'mock') {
                        status.innerHTML = '<span class="status-dot offline"></span>Mock';
                    } else {
                        status.innerHTML = '<span class="status-dot online"></span>' + data.provider.toUpperCase();
                    }
                });
        }
        
        function changeEngine() {
            const engine = document.getElementById('engineSelect').value;
            fetch('/api/set_engine?engine=' + engine)
                .then(r => r.json())
                .then(data => {
                    loadModels();
                    loadSystemInfo();
                });
        }
        
        function changeModel() {
            // Model selection - stored per request
        }
        
        function refreshModels() {
            loadModels();
            loadSystemInfo();
        }
        
        function getSystemInfo() {
            fetch('/api/system')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('response').textContent = JSON.stringify(data, null, 2);
                });
        }
        
        function sendMessage() {
            const msg = document.getElementById('userMessage').value;
            const temp = document.getElementById('temp').value;
            const maxTok = document.getElementById('maxTokens').value;
            const model = document.getElementById('modelSelect').value;
            
            document.getElementById('response').textContent = 'Processing...';
            
            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: msg,
                    temperature: parseFloat(temp),
                    max_tokens: parseInt(maxTok),
                    model: model
                })
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('response').textContent = data.response;
                messageHistory.push({role: 'user', content: msg});
                messageHistory.push({role: 'assistant', content: data.response});
            });
        }
        
        function generateCode() {
            const task = document.getElementById('codeTask').value;
            const model = document.getElementById('modelSelect').value;
            
            document.getElementById('codeOutput').textContent = 'Generating...';
            
            fetch('/api/code', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    task: task,
                    model: model
                })
            })
            .then(r => r.json())
            .then(data => {
                document.getElementById('codeOutput').textContent = data.code;
            });
        }
        
        function clearHistory() {
            messageHistory = [];
            document.getElementById('history').textContent = 'History cleared';
        }
    </script>
</body>
</html>
"""

# Global state
_state = {
    "provider": "mock",
    "model": "",
    "base_url": "",
    "initialized": False,
    "runner": None
}

def get_runner(force=False):
    """Get or create the runner"""
    global _state
    
    if _state["initialized"] and _state["runner"] and not force:
        return _state["runner"]
    
    from core.client import LocalRunner
    _state["runner"] = LocalRunner('auto')
    _state["runner"].initialize()
    _state["provider"] = _state["runner"].provider or "mock"
    _state["model"] = _state["runner"].model or ""
    _state["initialized"] = True
    
    return _state["runner"]

def get_system_info():
    """Get system info"""
    import os
    import ctypes
    
    total_ram = 8.0
    try:
        if platform.system() == "Windows":
            kernel32 = ctypes.windll.kernel32
            mem = ctypes.Structure()
            mem.dwLength = ctypes.sizeof(mem)
            kernel32.GlobalMemoryStatus(ctypes.byref(mem))
            total_ram = mem.dwTotalPhys / (1024**3)
    except:
        pass
    
    return {
        "platform": platform.system(),
        "cpu_cores": os.cpu_count() or 4,
        "total_ram_gb": round(total_ram, 1),
        "provider": _state.get("provider", "mock"),
        "model": _state.get("model", "")
    }

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/models')
def api_models():
    """List available models"""
    import json
    models = []
    
    # LM Studio models
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:1234/v1/models")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            for m in data.get("data", []):
                models.append({"id": m["id"], "name": m["id"], "provider": "lmstudio"})
    except:
        pass
    
    # Ollama models
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read())
            for m in data.get("models", []):
                models.append({"id": m["name"], "name": m["name"], "provider": "ollama"})
    except:
        pass
    
    # Fallback
    if not models:
        models = [
            {"id": "mock", "name": "Mock Model (Testing)", "provider": "mock"},
            {"id": "qwen/qwen2.5-coder-14b", "name": "Qwen2.5 Coder 14B", "provider": "lmstudio"},
        ]
    
    return jsonify({"models": models})

@app.route('/api/system')
def api_system():
    return jsonify(get_system_info())

@app.route('/api/set_engine')
def api_set_engine():
    """Set the engine"""
    engine = request.args.get('engine', 'auto')
    
    # Re-initialize with new engine
    global _state
    _state["initialized"] = False
    _state["runner"] = None
    
    runner = get_runner()
    
    return jsonify({"status": "ok", "provider": _state["provider"]})

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Chat completion"""
    data = request.json
    message = data.get('message', '')
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 2048)
    model = data.get('model', '')
    
    try:
        runner = get_runner()
        # Use selected model if specified
        if model:
            runner.model = model
        response = runner.chat([
            {"role": "user", "content": message}
        ])
        content = response.get("message", {}).get("content", "No response")
    except Exception as e:
        content = f"Error: {str(e)}"
    
    return jsonify({
        "response": content,
        "model": model or _state.get("model", ""),
        "provider": _state.get("provider", "")
    })

@app.route('/api/code', methods=['POST'])
def api_code():
    """Code generation"""
    data = request.json
    task = data.get('task', '')
    model = data.get('model', '')
    
    try:
        runner = get_runner()
        if model:
            runner.model = model
        code = runner.run_task(f"Write code: {task}")
    except Exception as e:
        code = f"# Error: {str(e)}"
    
    return jsonify({"code": code})

if __name__ == "__main__":
    print("Starting SL-LLM Production Console...")
    print("URL: http://localhost:8080")
    app.run(port=8080, debug=False, threaded=True)