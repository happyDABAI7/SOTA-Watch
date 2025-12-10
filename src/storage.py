import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# 初始化连接
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

# 如果没有配置 DB，给个空对象防止报错，但在 Phase 2 我们假设你一定配好了
supabase: Client = create_client(url, key) if url and key else None

def filter_new_items(raw_items: list) -> list:
    """
    [记忆过滤] 检查数据库，剔除已经处理过的 URL
    """
    if not raw_items or not supabase:
        return raw_items

    print("🔍 [Storage] Checking database for duplicates...")
    
    # 1. 提取本次抓取的所有 URL
    current_urls = [item['url'] for item in raw_items]
    
    # 2. 批量查询数据库：这些 URL 哪些已经存在？
    # 使用 'in_' 过滤器，一次性查完，效率极高
    try:
        response = supabase.table("sota_items") \
            .select("url") \
            .in_("url", current_urls) \
            .execute()
            
        # 3. 拿到“已存在”的 URL 集合
        existing_urls = {row['url'] for row in response.data}
        
        # 4. 做减法：只保留数据库里没有的
        new_items = [item for item in raw_items if item['url'] not in existing_urls]
        
        print(f"   - Raw items: {len(raw_items)}")
        print(f"   - Known items: {len(existing_urls)}")
        print(f"   - New items to process: {len(new_items)}")
        
        return new_items

    except Exception as e:
        print(f"❌ Database Check Error: {e}")
        # 如果数据库挂了，为了保险起见，返回所有数据（宁可重复，不可漏抓）
        return raw_items

def save_items(processed_items: list):
    """
    [记忆存储] 将 AI 处理好的高分内容存入数据库
    """
    if not processed_items or not supabase:
        return

    print(f"💾 [Storage] Saving {len(processed_items)} items to database...")
    
    # 构造符合数据库表结构的数据
    data_to_insert = []
    for item in processed_items:
        data_to_insert.append({
            "title": item.get('title'),
            "url": item.get('url'),
            "summary": item.get('summary'),
            "score": item.get('score', 0),
            "tags": item.get('tag'),
            "source": item.get('source'),
            "publish_date": item.get('publish_date')
        })
    
    try:
        # 批量插入
        supabase.table("sota_items").insert(data_to_insert).execute()
        print("✅ Data saved successfully.")
    except Exception as e:
        print(f"❌ Database Insert Error: {e}")
        