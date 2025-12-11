import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client
from src.embedder import get_embedding

# 1. 页面配置 (居中布局，阅读感更好)
st.set_page_config(
    page_title="SOTA Watch V4",
    page_icon="⚡",
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# 2. V4.0 终极美颜 CSS
st.markdown("""
<style>
    /* 全局字体 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* 搜索框美化 */
    .stTextInput input {
        border-radius: 20px;
        padding: 10px 20px;
        border: 1px solid #ddd;
    }

    /* 卡片容器 */
    .sota-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    
    .sota-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.08);
        border-color: #e0e0e0;
    }

    /* 头部信息栏 */
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }

    /* 标签样式 */
    .tech-tag {
        display: inline-block;
        background-color: #f1f5f9;
        color: #475569;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* 分数样式 */
    .score-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        font-weight: 700;
        font-size: 0.9rem;
        color: white;
    }
    .score-10, .score-9 { background: linear-gradient(135deg, #10b981, #059669); }
    .score-8, .score-7 { background: linear-gradient(135deg, #f59e0b, #d97706); }
    .score-low { background-color: #94a3b8; }

    /* 标题样式 */
    .card-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        text-decoration: none;
        margin-bottom: 8px;
        display: block;
    }
    .card-title:hover {
        color: #2563eb;
    }

    /* 摘要样式 */
    .card-summary {
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 16px;
    }

    /* 底部元数据 */
    .card-meta {
        font-size: 0.8rem;
        color: #94a3b8;
        display: flex;
        align-items: center;
        gap: 12px;
    }
</style>
""", unsafe_allow_html=True)

# 3. 资源加载
@st.cache_resource
def init_resources():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

supabase = init_resources()

# 4. 数据获取 (含 AI 搜索)
def get_data(query_text=None, min_score=7):
    if not query_text:
        # 普通模式
        response = supabase.table("sota_items") \
            .select("*") \
            .gte("score", min_score) \
            .order("created_at", desc=True) \
            .limit(50) \
            .execute()
        return pd.DataFrame(response.data), False
    else:
        # AI 搜索模式
        query_vector = get_embedding(query_text)
        response = supabase.rpc(
            "match_sota_items",
            {
                "query_embedding": query_vector,
                "match_threshold": 0.25, 
                "match_count": 20
            }
        ).execute()
        return pd.DataFrame(response.data), True

# --- 页面布局 ---

# 顶部 Hero 区域
st.markdown("<h1 style='text-align: center; margin-bottom: 30px;'>⚡ SOTA Watch <span style='font-size:0.5em; color:#94a3b8;'>V4.0</span></h1>", unsafe_allow_html=True)

# 搜索与筛选 (一行两列)
c1, c2 = st.columns([3, 1])
with c1:
    search = st.text_input("", placeholder="🔍 Search concepts like 'video generation'...", label_visibility="collapsed")
with c2:
    # 简单的分数过滤器
    min_val = st.selectbox("Quality", [7, 8, 9], index=0, format_func=lambda x: f"{x}+ Score")

# 获取数据
with st.spinner("Scanning database..."):
    df, is_search = get_data(search, min_val)

# 结果展示
if df.empty:
    st.markdown("<div style='text-align: center; color: #94a3b8; padding: 40px;'>No signals found. Try adjusting filters.</div>", unsafe_allow_html=True)
else:
    # 统计条
    if is_search:
        st.caption(f"🤖 Found {len(df)} semantic matches for '{search}'")
    else:
        st.caption(f"🕒 Showing latest {len(df)} high-quality items")

    # 渲染卡片流
    for index, row in df.iterrows():
        score = row['score']
        score_class = "score-10" if score >= 9 else ("score-8" if score >= 7 else "score-low")
        date_str = pd.to_datetime(row['created_at']).strftime('%b %d')
        source = row['source'].upper()
        
        # HTML 模板
        card_html = f"""
        <div class="sota-card">
            <div class="card-header">
                <span class="tech-tag">{row.get('tags', 'TECH')}</span>
                <div class="score-badge {score_class}">{score}</div>
            </div>
            
            <a href="{row['url']}" target="_blank" class="card-title">
                {row['title']} ↗
            </a>
            
            <div class="card-summary">
                {row['summary']}
            </div>
            
            <div class="card-meta">
                <span>📅 {date_str}</span>
                <span>•</span>
                <span>{source}</span>
                {f"<span>• Match: {row['similarity']*100:.0f}%</span>" if is_search and 'similarity' in row else ""}
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        