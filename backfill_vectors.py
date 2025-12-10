import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from src.embedder import get_embedding

load_dotenv()

# 初始化 Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: Supabase credentials not found.")
    exit()

supabase: Client = create_client(url, key)

def run_backfill():
    print("🔍 Checking for items without embeddings...")
    
    # 1. 查找 embedding 为空的记录
    # is_("embedding", "null") 是 Supabase 过滤空值的写法
    try:
        response = supabase.table("sota_items") \
            .select("*") \
            .is_("embedding", "null") \
            .execute()
        
        items = response.data
    except Exception as e:
        print(f"❌ Failed to fetch items: {e}")
        return

    if not items:
        print("✅ All items already have embeddings. No backfill needed.")
        return

    print(f"📦 Found {len(items)} items to process. Starting backfill...")
    print("-" * 40)

    # 2. 逐条生成向量并更新
    for i, item in enumerate(items):
        try:
            # 组合文本：标题 + 摘要 + 标签 + 来源
            # 组合的信息越全，搜索越准
            text_to_embed = f"{item['title']} {item.get('summary', '')} {item.get('tags', '')} {item.get('source', '')}"
            
            # 生成向量 (本地 CPU 运算)
            vector = get_embedding(text_to_embed)
            
            # 更新回数据库
            supabase.table("sota_items") \
                .update({"embedding": vector}) \
                .eq("id", item['id']) \
                .execute()
                
            print(f"   ({i+1}/{len(items)}) ✅ Vectorized: {item['title']}")
            
        except Exception as e:
            print(f"   ({i+1}/{len(items)}) ❌ Failed: {item['title']} - {e}")

    print("-" * 40)
    print("🎉 Backfill completed!")

if __name__ == "__main__":
    run_backfill()
    