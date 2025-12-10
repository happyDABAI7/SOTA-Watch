import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client, Client
# [新增] 引入向量生成器
from src.embedder import get_embedding

# 1. 页面配置
st.set_page_config(page_title="SOTA Watch AI", page_icon="🧠", layout="wide")

# 2. 资源初始化 (使用 cache_resource 避免重复加载模型)
@st.cache_resource
def init_resources():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

supabase = init_resources()

# 3. 数据加载逻辑 (普通模式 vs AI 搜索模式)
def get_data(query_text=None):
    if not query_text:
        # --- 普通模式：直接查最新的 ---
        response = supabase.table("sota_items") \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(50) \
            .execute()
        df = pd.DataFrame(response.data)
        if not df.empty:
            df['similarity'] = 1.0 # 默认相似度为 1
        return df, False
    else:
        # --- AI 模式：语义搜索 ---
        # 1. 把用户的文字变成向量
        query_vector = get_embedding(query_text)
        
        # 2. 调用数据库的 RPC 函数进行搜索
        response = supabase.rpc(
            "match_sota_items",
            {
                "query_embedding": query_vector,
                "match_threshold": 0.3, # 相似度阈值
                "match_count": 20
            }
        ).execute()
        
        df = pd.DataFrame(response.data)
        return df, True

# --- UI 渲染 ---

# 侧边栏
with st.sidebar:
    st.title("🧠 SOTA Brain")
    st.caption("Powered by DeepSeek & Vector Search")
    st.markdown("---")
    
    st.header("🔍 Filters")
    min_score = st.slider("Minimum Score", 0, 10, 6)
    
    st.markdown("---")
    if st.button("🔄 Clear Cache"):
        st.cache_data.clear()
        st.rerun()

# 主界面
st.title("📡 SOTA Watch Radar")

# [核心] 搜索框
search_query = st.text_input("🤖 Semantic Search", placeholder="Try: 'video generation' or 'autonomous agents'...")

# 获取数据
with st.spinner("Thinking..."):
    df, is_search_mode = get_data(search_query)

if df.empty:
    st.info("No items found. Try a different query.")
else:
    # 转换时间格式
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'])

    # 本地再次筛选 (分数)
    filtered_df = df[df['score'] >= min_score]

    # 统计信息
    c1, c2, c3 = st.columns(3)
    c1.metric("Items Found", len(filtered_df))
    if is_search_mode:
        c2.metric("Search Mode", "Semantic 🧠")
    else:
        c2.metric("Search Mode", "Latest 🕒")

    st.markdown("---")

    # 渲染列表
    for index, row in filtered_df.iterrows():
        # 分数颜色
        score_color = "green" if row['score'] >= 9 else "orange"
        
        with st.container():
            col_main, col_stats = st.columns([0.85, 0.15])
            
            with col_main:
                prefix = f"[{row.get('tags', 'AI')}]"
                st.subheader(f"{prefix} {row['title']}")
                st.markdown(f"> {row['summary']}")
                st.caption(f"Source: {row['source']} | Date: {row['created_at'].strftime('%Y-%m-%d')}")
                st.markdown(f"[🔗 Original Link]({row['url']})")
            
            with col_stats:
                st.markdown(f"### :{score_color}[{row['score']}]")
                if is_search_mode:
                    # 显示相似度匹配分
                    sim = row['similarity'] * 100
                    st.caption(f"Match: {sim:.1f}%")
            
            st.divider()
            