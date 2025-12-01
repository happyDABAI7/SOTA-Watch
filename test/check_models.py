import os
import google.generativeai as genai
from dotenv import load_dotenv

# ===========================
# 1. 强制代理 (确保端口正确!)
# ===========================
os.environ["HTTP_PROXY"] = "http://127.0.0.1:33210"  # <--- 检查这里
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:33210" # <--- 检查这里

# 2. 加载 API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Error: No API Key found.")
else:
    genai.configure(api_key=api_key)
    print("⏳ Asking Google for available models...")
    
    try:
        # 列出所有支持 generateContent 的模型
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ Found: {m.name}")
    except Exception as e:
        print(f"❌ Error: {e}")