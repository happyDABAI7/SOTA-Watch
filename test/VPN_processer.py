import os
import json
import time
import random
from dotenv import load_dotenv
import google.generativeai as genai

# ==========================================
# 🛑【最后确认】请确认你的 VPN 端口！
# Clash = 7890
# v2rayN = 10809
# ==========================================
PROXY_PORT = "33210"  # <--- 如果报错 Connection Refused，请把这里改成 10809 试试

os.environ["HTTP_PROXY"] = f"http://127.0.0.1:{PROXY_PORT}"
os.environ["HTTPS_PROXY"] = f"http://127.0.0.1:{PROXY_PORT}"

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_KEY:
    # [CTO 关键修复] transport='rest' 
    # 强制使用 HTTP 协议，避免 gRPC 在代理下报错
    genai.configure(api_key=GEMINI_KEY, transport='rest')

def analyze_item_with_llm(item):
    if not GEMINI_KEY: return None

    # [CTO 修正] 使用你列表里确认存在的模型
    # 如果 2.0 还是 429，就自动降级
    target_models = ['gemini-2.0-flash-lite', 'gemini-flash-latest', 'gemini-pro']
    
    for model_name in target_models:
        try:
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""
            你是 AI 科技媒体编辑。请将以下内容改写为中文简报：
            Title: {item['title']}
            Desc: {item['description']}
            
            输出纯 JSON:
            {{
                "score": (0-10分),
                "summary": (一句话中文介绍),
                "tag": (LLM/Agent/Tool)
            }}
            """
            
            response = model.generate_content(prompt)
            # 清洗 JSON
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("\n", 1)[0]
            
            return json.loads(text)

        except Exception as e:
            if "429" in str(e):
                print(f"   ⚠️ Model {model_name} busy (429). Trying next...")
                time.sleep(2)
                continue # 换下一个模型试
            elif "404" in str(e):
                print(f"   ⚠️ Model {model_name} not found. Trying next...")
                continue
            else:
                print(f"   ❌ Error with {model_name}: {e}")
                break # 其他错误直接停止

    return None

def process_data(raw_items: list) -> str:
    print(f"\n🧠 [Processor] Starting AI analysis on {len(raw_items)} items...")
    
    if not raw_items: return "No data."
        
    sota_items = []
    # 仍然只跑前 3 条
    test_batch = raw_items[:3] 
    
    for i, item in enumerate(test_batch):
        print(f"   ({i+1}/{len(test_batch)}) Analyzing: {item['title']} ...", end="")
        
        analysis = analyze_item_with_llm(item)
        
        if analysis:
            print(f" Score: {analysis.get('score')}")
            item.update(analysis)
            sota_items.append(item)
        else:
            print(" Skipped")
        
        time.sleep(3)

    # --- 兜底逻辑 ---
    if not sota_items:
        return """
# 🚨 SOTA Watch Daily (Mock Report)
> ⚠️ AI 接口暂时无法连接，请检查 VPN 端口设置 (7890 vs 10809)。
"""

    report = f"# 🚨 SOTA Watch Daily ({len(sota_items)} Updates)\n\n"
    for item in sota_items:
        report += f"### [{item.get('tag', 'AI')}] {item['title']}\n"
        report += f"**得分:** {item.get('score', 0)}/10\n"
        report += f"> 💡 {item.get('summary', '暂无摘要')}\n\n"
        report += f"🔗 [Original Link]({item['url']})\n"
        report += "---\n"
        
    return report

if __name__ == "__main__":
    try:
        with open("latest_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        report = process_data(data)
        print("\n" + "="*40)
        print(report)
        print("="*40)
    except FileNotFoundError:
        print("❌ File not found.")