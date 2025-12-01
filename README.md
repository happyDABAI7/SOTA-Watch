# 📡 SOTA Watch

> An automated "Hardcore Tech Radar" powered by LLM (DeepSeek).
> 监控 GitHub、HuggingFace 和 HackerNews，只为你推送最硬核的 AI 突破。

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-green)
![Status](https://img.shields.io/badge/status-MVP%20v0.1-orange)

## 🧐 What is SOTA Watch?

**SOTA (State-of-the-Art) Watch** solves the problem of AI information overload. 
Instead of scrolling through endless newsletters, this bot:
1.  **Fetches** trending projects from GitHub, HuggingFace, and Hacker News.
2.  **Filters** out noise (tutorials, listicles, marketing fluff) using Regex.
3.  **Analyzes** the core value using **DeepSeek V3 (LLM)**.
4.  **Delivers** a structured, scored report to **Feishu (Lark)**.

## 🚀 Features

- **Multi-Source**: GitHub (Search API), HuggingFace (Trends), HackerNews (TopStories).
- **High Signal-to-Noise**: Filters out "How to learn AI" content, keeping only new Models/Frameworks.
- **AI Powered**: Uses LLM to score (0-10) and summarize content in Chinese.
- **Push Notification**: Beautiful interactive cards via Feishu Webhook.

## 🛠️ Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/YourUsername/SOTA-Watch.git
cd SOTA-Watch
pip install -r requirements.txt
```

### 2. Configuration
Create a .env file in the root directory:
```
# GitHub Token (Fine-grained or Classic)
GH_TOKEN=your_github_token

# Hugging Face Token
HF_TOKEN=your_hf_token

# LLM Provider (SiliconCloud / DeepSeek)
DEEPSEEK_API_KEY=sk-your_api_key

# Feishu/Lark Webhook
FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
```

### 3. Run
```
python main.py
```

## 🗺️ Roadmap

v0.1 MVP: Core Pipeline (Fetch -> Process -> Notify).

v0.2: Database integration (Supabase).

v0.3: Web Dashboard.

## 🤝 Contributing
Issues and Pull Requests are welcome!

## 📄 License
MIT
