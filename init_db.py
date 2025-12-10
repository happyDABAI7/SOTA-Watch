import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: Missing SUPABASE variables in .env")
    exit()

print("🔌 Connecting to Supabase...")
try:
    # 初始化客户端
    supabase: Client = create_client(url, key)
    
    # 测试插入一条假数据
    data = {
        "title": "Test Database Connection",
        "url": "https://example.com/test-db-001", # 这个 URL 是唯一的
        "summary": "This is a test row to verify connection.",
        "score": 10,
        "source": "test",
        "tags": "Database"
    }
    
    # 执行插入
    response = supabase.table("sota_items").insert(data).execute()
    
    print("✅ Success! Inserted data:", response.data)
    
except Exception as e:
    print(f"❌ Connection Failed: {e}")
    # 常见错误：如果是 duplicate key value，说明你已经运行过一次了，也是成功的标志
    if "duplicate key" in str(e):
        print("💡 (This means the connection is working, but the test data already exists.)")