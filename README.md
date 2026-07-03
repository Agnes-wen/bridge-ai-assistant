# 桥梁结构认知助手

> 基于大语言模型的桥梁特征识别与结构讲解 AI Web 应用  
> 由阿里云通义千问（Qwen）大模型驱动

## 项目简介

本课程作业设计并实现了一个面向桥梁工程学习的 AI 助手，用户可以通过自然语言描述桥梁特征，由大模型自动识别桥梁类型并生成专业的结构讲解分析。

## 功能特性

- **桥梁类型智能识别**：支持梁桥、拱桥、斜拉桥、悬索桥、桁架桥、悬臂桥、刚架桥共 7 种桥型
- **三层讲解深度**：科普版（通俗易懂）、专业通识版（工科学生）、深度专业版（专业人员）
- **AI 生成专业分析**：基于通义千问大模型，生成结构受力体系、荷载传递路径、力学原理等分析
- **SVG 结构可视化**：自动匹配桥梁类型，展示专业结构示意图（含构件标注、荷载箭头、力流路径）
- **对话式交互**：支持多轮对话，保留最近 10 轮历史

## 技术架构

```
用户浏览器
    ↓ 输入桥梁描述
Flask 后端服务器（server.py）
    ↓ 调用 DashScope API
阿里云通义千问 Qwen 大模型
    ↓ 返回分析结果
前端渲染（index.html）
```

- **前端**：原生 HTML + CSS + JavaScript，无框架依赖
- **后端**：Python Flask，提供 API 代理保护 API Key
- **AI 模型**：阿里云 DashScope（兼容 OpenAI 格式）
- **部署**：支持本地运行，可部署至 Render.com 等云平台

## 本地运行指南

### 环境要求

- Python 3.8+
- 阿里云 DashScope API Key（[获取地址](https://dashscope.console.aliyun.com/apiKey)）

### 安装步骤

**1. 克隆仓库**

```bash
git clone https://github.com/Agnes-wen/bridge-ai-assistant.git
cd bridge-ai-assistant
```

**2. 安装依赖**

```bash
pip install -r requirements.txt
```

**3. 配置 API Key**

在项目根目录创建 `.env` 文件，内容如下：

```env
DASHSCOPE_API_KEY=你的阿里云API密钥
MODEL=qwen-plus
```

> ⚠️ 注意：`.env` 文件已被 `.gitignore` 忽略，不会提交到仓库，请妥善保管。

**4. 启动服务**

```bash
python server.py
```

服务启动后，浏览器打开 `http://localhost:5000` 即可使用。

## 提示词工程说明

本项目的核心提示词（`SYSTEM_PROMPT`）包含以下设计：

1. **角色设定**：注册结构工程师资质的桥梁工程专家
2. **桥型分类体系**：明确定义 7 种桥型的识别特征
3. **深度控制**：通过 `depth` 参数动态调整讲解深度
4. **输出格式规范**：强制要求输出包含识别结果、结构原理、拓展说明三部分
5. **桥型标签**：要求 AI 在回复末尾附加 `[BRIDGE_TYPE: xxx]` 标签，用于前端匹配 SVG 结构图

## 项目结构

```
bridge-ai-assistant/
├── index.html          # 前端主页面（聊天界面 + 分析面板）
├── server.py           # 后端服务器（Flask + DashScope API 代理）
├── requirements.txt    # Python 依赖列表
├── .env                # API Key 配置（不提交，需自行创建）
├── .gitignore          # Git 忽略规则
└── README.md           # 本文件
```

## 依赖项

```
flask
flask-cors
requests
python-dotenv
```

## 课程作业要求对照

| 作业要求 | 实现情况 |
|---------|---------|
| 使用 AI 编程工具辅助开发 | ✅ 使用 WorkBuddy 辅助开发 |
| 使用阿里云 Qwen 系列模型 | ✅ 接入 DashScope API，默认使用 qwen-plus |
| 具备网页界面，用户输入与 AI 回复 | ✅ 对话式聊天界面 |
| 实现明确功能场景 | ✅ 桥梁特征识别与结构讲解 |
| API Key 安全（不泄露） | ✅ 通过 .env + 后端代理保护 |
| 部署到可访问的 Web 服务器 | ⚠️ 支持本地运行，可部署至 Render.com |

## 未来改进方向

- 接入知识库（RAG），基于规范文档增强回答准确性
- 支持图片上传，通过计算机视觉识别桥梁类型
- 增加桥梁病害识别与养护建议功能
- 部署至公网，提供在线演示地址

## 作者

Agnes — 人工智能概论课程作业

## 许可证

本项目仅供课程作业使用。
