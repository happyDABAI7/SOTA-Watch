import requests
import time
import logging

logger = logging.getLogger(__name__)

def scrape_content(url: str) -> str:
    """
    使用 Jina Reader 将任意 URL 转换为对 LLM 友好的 Markdown。
    原理：在 URL 前加 https://r.jina.ai/
    """
    # 构造 Jina Reader API 地址
    jina_url = f"https://r.jina.ai/{url}"
    
    headers = {
        "User-Agent": "SotaWatchBot/4.0",
        # 告诉 Jina 我们不需要图片，只要纯文本，节省 token
        "X-Retain-Images": "none" 
    }
    
    # print(f"   🕷️ [Crawler] Deep reading: {url} ...")
    
    try:
        # 设置 20秒超时，防止卡死
        response = requests.get(jina_url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            content = response.text
            # 截断策略：
            # DeepSeek V3 窗口很大，但为了响应速度，我们取前 6000 字符
            # 这通常包含了 README 的 Header, Features, 和 Quick Start
            return content[:6000]
        else:
            logger.warning(f"Crawler failed ({response.status_code}): {url}")
            return ""
            
    except Exception as e:
        logger.error(f"Crawler Exception: {e}")
        return ""

if __name__ == "__main__":
    # 测试一下
    print("Testing crawler...")
    text = scrape_content("https://github.com/deepseek-ai/DeepSeek-V3")
    print(f"Content Length: {len(text)}")
    print(text[:500])
    