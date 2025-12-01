import os
import requests
import json
from dotenv import load_dotenv

# 1. 加载 Token
load_dotenv()
token = os.getenv("GH_TOKEN")
print(f"🔑 Token used: {token[:15]}******")

# 2. 构造最最简单的请求 (查 Python 项目，按星数排)
# 只要 GitHub 没倒闭，这个查询一定会有结果
url = "https://api.github.com/search/repositories?q=language:python&sort=stars&per_page=3"
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

print(f"📡 Sending request to: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"📶 Status Code: {response.status_code}")
    print("-" * 30)
    
    # 3. 打印原始数据的“内脏”
    data = response.json()
    
    # 看看 GitHub 说的 total_count 是多少
    total_count = data.get("total_count", "Not Found")
    print(f"🔢 Total Count (GitHub claims): {total_count}")
    
    items = data.get("items", [])
    print(f"📦 Items returned in list: {len(items)}")
    
    if len(items) == 0:
        print("\n❌ CRITICAL: GitHub returned 0 items!")
        print("💡 Diagnosis: Your Token has NO permission to view Public Repositories.")
    else:
        print("\n✅ Data received! First item:", items[0]['full_name'])
        
except Exception as e:
    print(f"❌ Connection Error: {e}")