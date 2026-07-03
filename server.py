"""
桥梁结构认知助手 — 后端服务器
基于阿里云通义千问 (Qwen) 大模型，通过 DashScope API 调用。
Flask 提供静态文件服务和 API 代理，保护 API Key 不暴露在前端。
"""

import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# ========================================================================
#  初始化
# ========================================================================
load_dotenv()

API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
MODEL = os.getenv("MODEL", "qwen-plus")

# DashScope 兼容 OpenAI 格式的 API 端点
DASHSCOPE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path="")


# ========================================================================
#  系统提示词（Prompt Engineering 核心部分）
# ========================================================================
SYSTEM_PROMPT = """你是一位拥有注册结构工程师资质的桥梁工程专家助手。你的核心任务是根据用户输入的桥梁特征描述，完成桥梁类型识别、结构原理讲解和拓展说明。

## 一、桥型分类体系

你必须能识别以下7种基本桥型，并在回复末尾附加桥型标识标签：

1. **梁桥 (beam)** — 以受弯为主的结构，荷载沿梁跨传递至支座
2. **拱桥 (arch)** — 拱圈主要承受轴向压力，支座产生水平推力
3. **斜拉桥 (cable-stayed)** — 斜拉索将主梁荷载传递至桥塔，塔以受压为主
4. **悬索桥 (suspension)** — 主缆呈悬链线形，通过吊索悬挂加劲梁，锚碇承受拉力
5. **桁架桥 (truss)** — 由三角形单元组成的杆件系统，各杆件承受轴向力
6. **悬臂桥 (cantilever)** — 悬臂梁从桥墩向两侧伸出，中间以挂孔连接
7. **刚架桥 (rigid-frame)** — 梁与墩固结形成刚架结构，节点承受弯矩和轴力

## 二、识别方法论

1. **结构特征关键词**：拱圈、斜拉索、悬索/主缆、桁架、悬臂、刚架/刚构
2. **跨度信息**：小跨(20-50m)多梁桥，中跨(50-200m)可拱可斜拉，大跨(200-1000m)多斜拉桥，超大跨(>1000m)多悬索桥
3. **材料线索**：预应力混凝土→梁桥/刚构桥；钢管混凝土→拱桥；高强钢丝→斜拉/悬索
4. **地形线索**：深谷山区→拱桥/刚构桥；跨江跨海→斜拉桥/悬索桥；城市立交→梁桥

## 三、输出格式要求

### 根据讲解深度（depth参数）调整内容：

**科普版 (popular)**：用通俗易懂的语言，面向无专业背景的读者。重点解释"这座桥长什么样""为什么这么建"，避免复杂力学公式。

**专业通识版 (professional)**：面向工科学生，使用专业术语但给出解释。包含结构体系、荷载传递路径、核心构件功能，可适当提及力学概念。

**深度专业版 (expert)**：面向桥梁工程专业人员，深入力学分析。包含弯矩图特征、应力分布、稳定分析、施工关键工序、常见病害与检养要点。

### 回复必须包含以下结构（使用 Markdown 格式）：

## 一、桥梁特征识别结果

- **桥型分类**：[主桥型] — [子类型（如有）]
- **核心构件**：列出主要构件及其位置和功能
- **主要材料**：识别使用的主要材料
- **辨识特征**：用于区分该桥型的关键特征

## 二、结构原理讲解

（根据 depth 调整深度）
- 结构受力体系
- 荷载传递路径
- 核心力学原理
（深度专业版额外包含：弯矩分布特征、施工关键工序、常见病害）

## 三、拓展说明

- 适用跨度范围
- 经典工程案例
- 优缺点对比

## 四、桥型标签

在回复的最末尾，必须附加一行标签（前端用于匹配 SVG 结构图）：
[BRIDGE_TYPE: 桥型标识符]

桥型标识符取值：beam / arch / cable-stayed / suspension / truss / cantilever / rigid-frame

## 四、异常处理

1. 若用户输入信息不足以判断桥型，说明缺失信息，给出最可能的1-2种猜测
2. 若描述包含多种桥型特征（组合体系桥），以主要结构体系为准
3. 若用户输入与桥梁无关，友好引导回桥梁话题"""


# ========================================================================
#  API 路由
# ========================================================================
@app.route("/api/chat", methods=["POST"])
def chat():
    """接收用户消息，调用 Qwen 大模型，返回 AI 回复"""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        history = data.get("history", [])
        depth = data.get("depth", "professional")

        if not user_message:
            return jsonify({"error": "消息不能为空"}), 400

        if not API_KEY:
            return jsonify({"error": "服务器未配置 API Key，请检查 .env 文件"}), 500

        # 根据深度级别调整系统提示词
        depth_desc = {
            "popular": "（当前为科普版，请用通俗易懂的语言讲解）",
            "professional": "（当前为专业通识版，请面向工科学生使用专业术语并适当解释）",
            "expert": "（当前为深度专业版，请深入力学分析，包含弯矩图特征、应力分布、施工工序、常见病害等）",
        }
        system_content = SYSTEM_PROMPT + "\n\n" + depth_desc.get(depth, "")

        # 构建消息列表
        messages = [{"role": "system", "content": system_content}]

        # 添加对话历史（最近10轮）
        for h in history[-10:]:
            role = h.get("role", "user")
            content = h.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})

        # 调用 DashScope API（兼容 OpenAI 格式）
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        }
        payload = {
            "model": MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096,
        }

        resp = requests.post(DASHSCOPE_URL, headers=headers, json=payload, timeout=60)

        if resp.status_code != 200:
            error_msg = "大模型调用失败"
            try:
                err_data = resp.json()
                error_msg = err_data.get("error", {}).get("message", error_msg)
            except Exception:
                error_msg = resp.text[:200]
            return jsonify({"error": error_msg}), 502

        result = resp.json()
        reply = result["choices"][0]["message"]["content"]

        return jsonify({"reply": reply})

    except requests.exceptions.Timeout:
        return jsonify({"error": "请求超时，请稍后重试"}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "无法连接到大模型服务，请检查网络"}), 502
    except Exception as e:
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


# ========================================================================
#  静态文件服务
# ========================================================================
@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    """提供静态文件（CSS、JS、图片等）"""
    return send_from_directory(BASE_DIR, path)


# ========================================================================
#  启动
# ========================================================================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("=" * 50)
    print("  桥梁结构认知助手 — 服务已启动")
    print(f"  模型: {MODEL}")
    print(f"  地址: http://localhost:{port}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=port, debug=True)
