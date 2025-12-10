import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ==========================================
# [DeepSeek 官网版] 
# 使用官方 API，稳定且你已经充值了余额
# ==========================================

API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = None
if API_KEY:
    client = OpenAI(
        api_key=API_KEY,
        # [关键修改] 改回 DeepSeek 官方地址
        base_url="https://api.deepseek.com"
    )
else:
    print("⚠️ Warning: DEEPSEEK_API_KEY not found in env")

def analyze_item_with_llm(item):
    if not client: return None

    prompt = f"""
    你是 AI 科技编辑。分析以下项目：
    标题: {item['title']}
    描述: {item['description']}
    
    任务：
    1. 评分 (0-10分, SOTA/重磅更新=9-10)。
    2. 中文一句话总结。
    3. 标签 (LLM, Vision, Agent, Tool)。
    
    输出纯 JSON:
    {{
        "score": <数字>,
        "summary": "<中文总结>",
        "tag": "<标签>"
    }}
    """
    try:
        # [关键修改] 改回 DeepSeek 官方模型名称
        model_name = "deepseek-chat" 
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You output JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=512
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
            
        return json.loads(content)

    except Exception as e:
        print(f"   ❌ API Error: {e}")
        return None

def process_data(raw_items: list) -> str:
    print(f"\n🧠 [Processor] Starting AI analysis on {len(raw_items)} items...")
    
    if not raw_items: return "No data."
        
    sota_items = []
    # 云端运行速度快，处理前 10 条
    # test_batch = raw_items[:10] 
    items_to_process = raw_items 
    
    print(f"\n🧠 [Processor] Starting AI analysis on {len(items_to_process)} items...")

    sota_items = []
    
    for i, item in enumerate(test_batch):
        print(f"   ({i+1}/{len(test_batch)}) Analyzing: {item['title']} ...", end="")
        
        analysis = analyze_item_with_llm(item)
        
        if analysis:
            print(f" Score: {analysis.get('score')}")
            if analysis.get('score', 0) >= 6:
                item.update(analysis)
                sota_items.append(item)
        else:
            print(" Skipped (Error)")
        
        time.sleep(0.5)

    if not sota_items:
        return "🔕 No high-score updates found."

    report = f"# 🚨 SOTA Watch Daily\n\n"
    for item in sota_items:
        report += f"### [{item.get('tag','AI')}] {item['title']}\n"
        report += f"**得分:** {item.get('score',0)}/10\n"
        report += f"> 💡 {item.get('summary', '暂无')}\n\n"
        report += f"🔗 [Link]({item['url']})\n"
        report += "---\n"
        
    return report
