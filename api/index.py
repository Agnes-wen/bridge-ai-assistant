import os, json, requests
from http.server import BaseHTTPRequestHandler

API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
MODEL = os.getenv("MODEL", "qwen-plus")
URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            messages = data.get("messages", [])

            if not API_KEY:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "未配置 API Key"}).encode())
                return

            resp = requests.post(URL, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                                 json={"model": MODEL, "messages": messages, "temperature": 0.7, "max_tokens": 4096}, timeout=30)
            result = resp.json()
            reply = result["choices"][0]["message"]["content"]

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

