import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. 页面基础配置
st.set_page_config(
    page_title="SOTA Watch Radar",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 连接数据库 (使用缓存，防止每次刷新都重连)
@st.cache_resource
def init_connection():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

supabase = init_connection()

# 3.以此获取数据 (使用缓存，TTL=600秒，即10分钟刷新一次)
@st.cache_data(ttl=600)
def load_data():
    # 查询所有数据，按创建时间倒序
    response = supabase.table("sota_items") \
        .select("*") \
        .order("created_at", desc=True) \
        .execute()
    
    # 转换为 Pandas DataFrame，方便处理
    df = pd.DataFrame(response.data)
    
    # 如果数据为空，返回空 DF
    if df.empty:
        return df
        
    # 格式化时间
    df['created_at'] = pd.to_datetime(df['created_at'])
    return df

# --- UI 渲染逻辑 ---

# 侧边栏：控制台
with st.sidebar:
    st.title("📡 SOTA Watch")
    st.markdown("---")
    
    st.header("🔍 Filters")
    
    # 分数筛选
    min_score = st.slider("Minimum Score", 0, 10, 6)
    
    # 来源筛选
    if 'source' in load_data().columns:
        all_sources = list(load_data()['source'].unique())
        selected_sources = st.multiselect("Source", all_sources, default=all_sources)
    else:
        selected_sources = []

    st.markdown("---")
    st.caption(f"Connected to Supabase")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# 主界面
st.title("🚀 AI Trend Radar")
st.markdown("Hardcore AI news filtered by **DeepSeek V3**.")

# 加载数据
df = load_data()

if df.empty:
    st.warning("📭 Database is empty. Run `python main.py` to fetch data first.")
else:
    # 应用筛选
    filtered_df = df[
        (df['score'] >= min_score) & 
        (df['source'].isin(selected_sources))
    ]
    
    # 顶部统计卡片
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", len(df))
    col2.metric("Filtered Items", len(filtered_df))
    col3.metric("Avg Score", f"{filtered_df['score'].mean():.1f}" if not filtered_df.empty else "0")

    st.markdown("---")

    # 展示列表
    for index, row in filtered_df.iterrows():
        # 根据分数决定颜色
        score_color = "green" if row['score'] >= 9 else "orange" if row['score'] >= 7 else "grey"
        
        with st.container():
            c1, c2 = st.columns([0.8, 0.2])
            
            with c1:
                st.subheader(f"[{row.get('tags', 'AI')}] {row['title']}")
                st.markdown(f"> 💡 {row['summary']}")
                st.caption(f"📅 Found: {row['created_at'].strftime('%Y-%m-%d %H:%M')} | Source: {row['source']}")
                st.markdown(f"[🔗 Original Link]({row['url']})")
            
            with c2:
                st.markdown(f"### :{score_color}[{row['score']}/10]")
            
            st.divider()
            