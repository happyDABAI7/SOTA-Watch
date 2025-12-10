import os
from dotenv import load_dotenv
from supabase import create_client, Client
# [新增] 引入向量生成器
from src.embedder import get_embedding

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key) if url and key else None

def filter_new_items(raw_items: list) -> list:
    # ... (这部分代码保持不变，不需要改) ...
    if not raw_items or not supabase: return raw_items
    current_urls = [item['url'] for item in raw_items]
    try:
        response = supabase.table("sota_items").select("url").in_("url", current_urls).execute()
        existing_urls = {row['url'] for row in response.data}
        return [item for item in raw_items if item['url'] not in existing_urls]
    except Exception:
        return raw_items

def save_items(processed_items: list):
    """
    [V3.0 升级版] 存储同时也存入向量
    """
    if not processed_items or not supabase: return

    print(f"💾 [Storage] Saving {len(processed_items)} items with Embeddings...")
    
    data_to_insert = []
    for item in processed_items:
        # 1. 准备要向量化的文本 (标题 + 摘要 + 标签)
        # 这样用户搜标签或搜内容都能搜到
        text_to_embed = f"{item.get('title')} {item.get('summary')} {item.get('tags')}"
        
        # 2. 生成向量
        vector = get_embedding(text_to_embed)
        
        data_to_insert.append({
            "title": item.get('title'),
            "url": item.get('url'),
            "summary": item.get('summary'),
            "score": item.get('score', 0),
            "tags": item.get('tag'),
            "source": item.get('source'),
            "publish_date": item.get('publish_date'),
            "embedding": vector  # [新增] 存入向量列
        })
    
    try:
        supabase.table("sota_items").insert(data_to_insert).execute()
        print("✅ Data saved successfully.")
    except Exception as e:
        print(f"❌ Database Insert Error: {e}")
        