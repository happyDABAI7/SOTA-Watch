import os
import json
import requests
import re
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 读取 Token，如果没有则为 None
GITHUB_TOKEN = os.getenv("GH_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")

# 构造请求头
GH_HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    GH_HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

HF_HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

NOISE_PATTERNS = [
    r"tutorial", r"course", r"learn", r"101", r"introduction", r"guide for beginners",
    r"interview", r"awesome-", r"resources", r"cheat sheet", r"roadmap"
]

def is_noise(text: str) -> bool:
    if not text: return False
    combined_pattern = "|".join(NOISE_PATTERNS)
    return bool(re.search(combined_pattern, text, re.IGNORECASE))

def fetch_github_trends():
    print("🔄 Fetching GitHub Data...")
    
    # [CTO 修复版]
    # 简化查询逻辑，避免 422 语法错误
    # q: "AI topic:ai" -> 搜索包含 "AI" 关键词且打了 "ai" 标签的项目
    # 这样绝对符合语法，不会报错
    params = {
        "q": "AI topic:ai", 
        "sort": "created",
        "order": "desc",
        "per_page": 20
    }
    
    try:
        response = requests.get("https://api.github.com/search/repositories", headers=GH_HEADERS, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ GitHub API Error: Status {response.status_code}")
            print(f"   Reason: {response.text}")
            return []
            
        items = response.json().get("items", [])
        
        results = []
        for item in items:
            desc = item.get("description") or ""
            if is_noise(item["name"]) or is_noise(desc): continue
            
            results.append({
                "source": "github",
                "title": item["full_name"],
                "url": item["html_url"],
                "description": f"⭐ {item['stargazers_count']} | {desc}",
                "publish_date": item["created_at"]
            })
        print(f"✅ GitHub: Found {len(results)} items.")
        return results
    except Exception as e:
        print(f"❌ GitHub Connection Error: {e}")
        return []

def fetch_huggingface_trends():
    print("🔄 Fetching HF Data...")
    url = "https://huggingface.co/api/models?sort=likes&direction=-1&limit=20&full=true"
    try:
        response = requests.get(url, headers=HF_HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ HF API Error: {response.status_code}")
            return []
            
        models = response.json()
        results = []
        for model in models:
            if not model.get("lastModified"): continue
            desc = f"❤️ {model.get('likes', 0)} | Task: {model.get('pipeline_tag', 'Unknown')}"
            results.append({
                "source": "huggingface",
                "title": model["modelId"],
                "url": f"https://huggingface.co/{model['modelId']}",
                "description": desc,
                "publish_date": model["lastModified"]
            })
        print(f"✅ HF: Found {len(results)} items.")
        return results
    except Exception as e:
        print(f"❌ HF Error: {e}")
        return []

def fetch_hackernews_ai():
    print("🔄 Fetching HN Data (Top 15)...", end="")
    try:
        ids_resp = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=5)
        if ids_resp.status_code != 200:
             print("\n❌ HN API Error")
             return []
        ids = ids_resp.json()[:15]
        
        results = []
        for item_id in ids:
            print(".", end="", flush=True)
            try:
                item_resp = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json", timeout=3)
                if item_resp.status_code != 200: continue
                item = item_resp.json()
                if not item or "title" not in item: continue
                title = item["title"]
                if any(k in title.lower() for k in ["gpt", "llm", "ai", "transformer", "openai", "nvidia", "google"]):
                    if is_noise(title): continue
                    results.append({
                        "source": "hackernews",
                        "title": title,
                        "url": item.get("url", ""),
                        "description": f"Score: {item.get('score',0)}",
                        "publish_date": str(item.get("time"))
                    })
            except: continue
        print(f"\n✅ HN: Found {len(results)} items.")
        return results
    except Exception as e:
        print(f"\n❌ HN Error: {e}")
        return []

def fetch_all_data():
    data = []
    data.extend(fetch_github_trends())
    data.extend(fetch_huggingface_trends())
    data.extend(fetch_hackernews_ai())
    
    seen_urls = set()
    unique_data = []
    for item in data:
        if item["url"] not in seen_urls:
            unique_data.append(item)
            seen_urls.add(item["url"])
    return unique_data

if __name__ == "__main__":
    data = fetch_all_data()
    with open("latest_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"🎉 Done! Saved {len(data)} items to latest_data.json")