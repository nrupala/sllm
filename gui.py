"""SL-LLM GUI with Help"""
import http.server
import socketserver
import webbrowser
from pathlib import Path
import threading
import time
import os


HTML = """<!DOCTYPE html>
<html>
<head>
    <title>SL-LLM Control Panel</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
        h1 { color: #00d4ff; }
        .card { background: #16213e; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .btn { background: #0f3460; color: #fff; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #00d4ff; color: #000; }
        .status { padding: 10px; background: #0f3460; border-radius: 5px; }
        input, textarea { background: #0f3460; color: #fff; border: 1px solid #333; padding: 10px; border-radius: 5px; width: 80%; }
        pre { background: #0a0a1a; padding: 15px; border-radius: 5px; overflow-x: auto; }
        a { color: #00d4ff; }
    </style>
</head>
<body>
    <h1>🤖 SL-LLM Control Panel</h1>
    
    <div class="card">
        <h3>📖 Help & Documentation</h3>
        <p>Access the full help documentation: <a href="HELP.md" target="_blank">HELP.md</a></p>
        <button class="btn" onclick="window.open('HELP.md')">📖 Open Help</button>
        <button class="btn" onclick="window.open('README.md')">📋 Readme</button>
    </div>

    <div class="card">
        <h3>⚙️ System Status</h3>
        <div class="status" id="status">Loading...</div>
    </div>

    <div class="card">
        <h3>💬 Run Query</h3>
        <input type="text" id="query" placeholder="Enter your task..." />
        <button class="btn" onclick="runQuery()">Execute</button>
        <pre id="output">Output will appear here...</pre>
    </div>

    <div class="card">
        <h3>📁 Project Files</h3>
        <button class="btn" onclick="showFiles('core')">Core</button>
        <button class="btn" onclick="showFiles('tools')">Tools</button>
        <button class="btn" onclick="showFiles('eval')">Eval</button>
    </div>

    <script>
        document.getElementById('status').innerHTML = `
            <b>GPU:</b> Detected (RTX 3080)<br>
            <b>Backend:</b> LM Studio<br>
            <b>Model:</b> qwen2.5-coder<br>
            <b>Tools:</b> 6 available
        `;

        function runQuery() {
            const q = document.getElementById('query').value;
            document.getElementById('output').innerText = 'Processing...';
            fetch('/execute?task=' + encodeURIComponent(q))
                .then(r => r.text())
                .then(t => document.getElementById('output').innerText = t);
        }

        function showFiles(folder) {
            fetch('/files?folder=' + folder)
                .then(r => r.text())
                .then(t => document.getElementById('output').innerText = t);
        }
    </script>
</body>
</html>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/execute'):
            import urllib.parse
            task = urllib.parse.parse_qs(self.path[9:]).get('task', [''])[0]
            result = f"Query submitted: {task}\n\nThis GUI is for display. Use CLI: python run.py"
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(result.encode())
        elif self.path.startswith('/files'):
            import urllib.parse
            folder = urllib.parse.parse_qs(self.path[7:]).get('folder', [''])[0]
            import os, pathlib
            base = pathlib.Path('D:/sl/projects/sllm')
            files = list((base / folder).glob('*')) if (base / folder).exists() else []
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('\n'.join([str(f.name) for f in files]).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        else:
            super().do_GET()


def start_gui(port=8080):
    os.chdir('D:/sl/projects/sllm')
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"\n🌐 GUI available at: http://localhost:{port}")
        print(f"📖 Help: http://localhost:{port}/HELP.md")
        webbrowser.open(f"http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    start_gui()