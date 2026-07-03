import os
import requests
from flask import Flask, request, jsonify

API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
MODEL = os.getenv("MODEL", "qwen-plus")
URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

app = Flask(__name__)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    messages = data.get("messages", [])
    if not API_KEY:
        return jsonify({"error": "未配置 API Key"}), 500
    try:
        resp = requests.post(URL, headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                             json={"model": MODEL, "messages": messages, "temperature": 0.7, "max_tokens": 4096}, timeout=30)
        result = resp.json()
        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
