# debug_env.py
import os
from dotenv import load_dotenv

# 1. 尝试加载
print("📂 Loading .env file...")
loaded = load_dotenv()

# 2. 检查结果
print(f"✅ .env loaded successfully: {loaded}")

# 3. 检查具体变量
token = os.getenv("GH_TOKEN")

if token:
    # 只打印前几位，保护隐私
    print(f"🎉 GH_TOKEN found: {token[:10]}******")
    print(f"   Length: {len(token)}")
else:
    print("❌ GH_TOKEN is None! Python did not find it.")
    
    # Windows 常见坑：检查是不是被命名成了 .env.txt
    files = os.listdir('.')
    if ".env.txt" in files:
        print("⚠️  WARNING: Found '.env.txt'! Please rename it to just '.env'")