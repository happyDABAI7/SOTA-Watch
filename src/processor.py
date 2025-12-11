import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI
# [新增] 引入爬虫
from src.crawler import scrape_content

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = None
if API_KEY:
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://api.deepseek.com"
    )
else:
    print("⚠️ Warning: DEEPSEEK_API_KEY not found")

def analyze_item_deeply(item):
    if not client: return None

    # 1. [深度阅读] 爬取全文
    full_content = scrape_content(item['url'])
    
    # 如果爬取失败，回退到使用原来的描述
    context = full_content if full_content else item['description']

    # 2. [V4.0 终极 Prompt]
    prompt = f"""
    你是 SOTA Watch 的首席技术官。请基于以下【项目详情】，严格评估其技术价值。
    
    标题: {item['title']}
    链接: {item['url']}
    原始描述: {item['description']}
    
    【项目详情 (Markdown)】:
    {context[:4000]} ...
    
    【任务】:
    1. **判定噪音**:
       - 如果是 课程(Course)、教程(Tutorial)、面试题、资源列表(Awesome List)、营销软文 -> 标记为 is_noise: true。
       - 如果是 真实的代码库、模型权重、技术论文 -> 标记为 is_noise: false。
    
    2. **技术评分 (0-10)**:
       - 10分: 行业里程碑 (如 DeepSeek-V3, Llama 3, Sora)。
       - 8-9分: 高质量 SOTA 工具/框架 (如 LangChain 更新, 新的 Agent 框架)。
       - 6-7分: 普通的 Demo 或 论文实现。
       - <6分: 缺乏创新的 Wrapper 或 简单脚本。

    3. **深度总结**: 用中文，基于【项目详情】写 50-80 字的硬核技术摘要。
    
    4. **标签**: (LLM, Vision, Agent, Framework, Hardware, Audio)。

    输出纯 JSON:
    {{
        "is_noise": <bool>,
        "score": <int>,
        "summary": "<string>",
        "tag": "<string>"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You output JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=1024
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1].rsplit("\n", 1)[0]
        return json.loads(content)

    except Exception as e:
        print(f"   ❌ Analysis Error: {e}")
        return None

def process_data(raw_items: list) -> str:
    # 1. [粗筛] 关键词过滤，省钱省时间
    candidates = []
    # 这些词出现在标题里，直接枪毙，不需要 AI 看
    noise_keywords = ["course", "tutorial", "learn ", "101", "roadmap", "cheatsheet", "interview", "awesome"]
    
    for item in raw_items:
        title_lower = item['title'].lower()
        if any(k in title_lower for k in noise_keywords):
            print(f"   🗑️ [Pre-Filter] Dropped noise: {item['title']}")
            continue
        candidates.append(item)

    print(f"\n🧠 [Processor] Deep analyzing {len(candidates)} items (Filtered from {len(raw_items)})...")
    
    if not candidates: return "No qualified data."
    
    sota_items = []
    
    # 全量跑
    for i, item in enumerate(candidates):
        print(f"   ({i+1}/{len(candidates)}) Deep Reading: {item['title']} ...")
        
        analysis = analyze_item_deeply(item)
        
        if analysis:
            score = analysis.get('score', 0)
            is_noise = analysis.get('is_noise', False)
            print(f"      -> Score: {score} | Noise: {is_noise}")
            
            # [严选标准] 非噪音 且 分数 >= 7
            if not is_noise and score >= 7:
                item.update(analysis)
                sota_items.append(item)
        else:
            print("      -> Skipped (Error)")
        
        # 爬虫需要礼貌，间隔 1.5 秒
        time.sleep(1.5)

    if not sota_items:
        return "🔕 No SOTA updates found (Strict filtering)."

    report = f"# 🚨 SOTA Watch Daily (Deep Dive)\n\n"
    for item in sota_items:
        report += f"### [{item.get('tag','AI')}] {item['title']}\n"
        report += f"**得分:** {item.get('score',0)}/10\n"
        report += f"> 📝 {item.get('summary', '暂无')}\n\n"
        report += f"🔗 [查看详情]({item['url']})\n"
        report += "---\n"
        
    return report