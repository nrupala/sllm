"""
SL-LLM GUI with Flask
"""
from flask import Flask, render_template_string, request, jsonify
import os
import threading

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>SL-LLM Control Panel</title>
    <style>
        body { font-family: sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        h1 { color: #00d4ff; }
        .card { background: #16213e; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .btn { background: #0f3460; color: #fff; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #00d4ff; color: #000; }
        .status { padding: 10px; background: #0f3460; border-radius: 5px; }
        input { background: #0f3460; color: #fff; border: 1px solid #333; padding: 10px; border-radius: 5px; width: 70%; }
        pre { background: #0a0a1a; padding: 15px; border-radius: 5px; overflow-x: auto; font-family: monospace; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>SL-LLM Control Panel</h1>
    
    <div class="card">
        <h3>System Status</h3>
        <div class="status" id="status">Loading...</div>
    </div>

    <div class="card">
        <h3>Run Query</h3>
        <input type="text" id="query" placeholder="Enter your task..." onkeyup="if(event.key==='Enter')runQuery()">
        <button class="btn" onclick="runQuery()">Execute</button>
        <pre id="output">Output will appear here...</pre>
    </div>

    <script>
        fetch('/status').then(r => r.text()).then(t => document.getElementById('status').innerText = t).catch(e => document.getElementById('status').innerText = 'Error');

        function runQuery() {
            const q = document.getElementById('query').value;
            if (!q.trim()) return;
            document.getElementById('output').innerText = 'Processing...';
            fetch('/execute?task=' + encodeURIComponent(q))
                .then(r => r.text())
                .then(t => document.getElementById('output').innerText = t)
                .catch(e => document.getElementById('output').innerText = 'Error: ' + e);
        }
    </script>
</body>
</html>
"""

# Global runner - initialized once
_runner = None

def get_runner():
    global _runner
    if _runner is None:
        from core.client import LocalRunner
        _runner = LocalRunner('auto')
        _runner.initialize()
    return _runner

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/status')
def status():
    try:
        runner = get_runner()
        return f"GPU: {runner.provider}\nProvider: {runner.provider}\nModel: {runner.model}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/execute')
def execute():
    task = request.args.get('task', '')
    if not task:
        return "No task provided"
    
    try:
        runner = get_runner()
        result = runner.run_task(task)
        return result
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    print("Starting SL-LLM GUI...")
    app.run(port=8080, debug=False, threaded=True)