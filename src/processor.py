import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# ==========================================
# [CTO 架构升级] 切换至 OpenAI 兼容协议 (DeepSeek)
# 优势：无需 VPN，国内直连，标准接口，速度快
# ==========================================

# 读取 DeepSeek Key
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

# 初始化客户端 (DeepSeek 使用 OpenAI 的 SDK)
client = None
if DEEPSEEK_KEY:
    client = OpenAI(
        api_key=DEEPSEEK_KEY,
        base_url="https://api.deepseek.com"  # DeepSeek 官方接口地址
    )
else:
    print("⚠️ Warning: DEEPSEEK_API_KEY not found in .env")

def analyze_item_with_llm(item):
    """
    使用 DeepSeek (DeepSeek-Chat/V3) 分析数据
    """
    if not client:
        return None

    prompt = f"""
    你是 SOTA Watch 的首席技术分析师。请阅读以下 AI 项目/新闻：
    
    标题: {item['title']}
    描述: {item['description']}
    来源: {item['source']}
    
    任务：
    1. 判断其重要性 (0-10分)。SOTA模型/重大框架更新=9-10分；普通Demo/论文=6-8分；教程/水文=0-3分。
    2. 用简练的中文一句话总结其核心价值。
    3. 给出标签 (LLM, Agent, Vision, Audio, Hardware, Tool)。
    
    请仅输出合法的 JSON 格式，不要包含 Markdown 格式标记(如 ```json):
    {{
        "score": <数字>,
        "summary": "<中文总结>",
        "tag": "<标签>"
    }}
    """
    
    try:
        # 调用 DeepSeek V3 (deepseek-chat)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1, # 低温度，保证输出格式稳定
            stream=False
        )
        
        # 解析结果
        content = response.choices[0].message.content.strip()
        
        # 清洗可能存在的 Markdown 代码块标记
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
            
        return json.loads(content)

    except Exception as e:
        print(f"   ❌ DeepSeek Error: {e}")
        return None

def process_data(raw_items: list) -> str:
    print(f"\n🧠 [Processor] Starting AI analysis on {len(raw_items)} items using DeepSeek...")
    
    if not raw_items:
        return "No data to process."
        
    sota_items = []
    
    # ⚠️ 此时我们可以大胆一点，处理前 5 条，因为 DeepSeek 很快且不限流
    test_batch = raw_items[:5] 
    
    for i, item in enumerate(test_batch):
        print(f"   ({i+1}/{len(test_batch)}) Analyzing: {item['title']} ...", end="")
        
        analysis = analyze_item_with_llm(item)
        
        if analysis:
            print(f" Score: {analysis.get('score')}")
            # 过滤掉低分内容 (阈值设为 6)
            if analysis.get('score', 0) >= 6:
                item.update(analysis)
                sota_items.append(item)
        else:
            print(" Skipped (Error)")
            
        # DeepSeek 几乎不需要冷却时间，但为了礼貌，停顿 1 秒
        time.sleep(1)

    # 如果没有高分内容，为了测试，我们强制显示所有处理过的内容(如果想要严格模式再改回去)
    if not sota_items:
        return "🔕 No SOTA updates found today (Low Signal-to-Noise Ratio)."

    report = f"# 🚨 SOTA Watch Daily (DeepSeek Edition)\n\n"
    for item in sota_items:
        report += f"### [{item.get('tag','AI')}] {item['title']}\n"
        report += f"**得分:** {item.get('score',0)}/10  |  **来源:** {item['source']}\n\n"
        report += f"> 💡 **摘要:** {item.get('summary', '无摘要')}\n\n"
        report += f"🔗 [查看原链接]({item['url']})\n"
        report += "---\n"
        
    return report

if __name__ == "__main__":
    try:
        with open("latest_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 运行处理
        report = process_data(data)
        
        print("\n" + "="*40)
        print(report)
        print("="*40)
        
    except FileNotFoundError:
        print("❌ latest_data.json not found. Run fetcher.py first.")