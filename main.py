import sys
import logging
import time

# 导入我们可以工作的模块
from src.fetcher import fetch_all_data
from src.processor import process_data
from src.notifier import send_notification

# 配置日志格式，让你看清楚每一步在干嘛
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("🚀 SOTA Watch Pipeline Started (V1.0 MVP)")

    # --- Step 1: 抓取 (The Hand) ---
    logger.info("📡 Step 1: Fetching data from GitHub/HF/HN...")
    try:
        # 调用 fetcher.py
        raw_data = fetch_all_data()
        logger.info(f"📦 Step 1 Finished: Captured {len(raw_data)} raw items.")
        
        if not raw_data:
            logger.warning("⚠️ No new data found. Stopping pipeline.")
            return
            
    except Exception as e:
        logger.error(f"❌ Critical Error in Fetcher: {e}")
        return

    # --- Step 2: 分析 (The Brain) ---
    logger.info("🧠 Step 2: Analyzing data with LLM (DeepSeek/SiliconCloud)...")
    try:
        # 调用 processor.py
        # 注意：目前 processor 内部为了测试只处理了前 5 条
        report = process_data(raw_data)
        logger.info("📝 Step 2 Finished: Daily report generated.")
        
    except Exception as e:
        logger.error(f"❌ Critical Error in Processor: {e}")
        return

    # --- Step 3: 推送 (The Mouth) ---
    logger.info("📨 Step 3: Delivering notification (Feishu)...")
    try:
        # 简单的检查：如果报告里包含 "No SOTA updates" 且只有极短的内容，就不发飞书打扰你了
        if "No SOTA updates" in report and len(report) < 100:
            logger.info("🔕 Report is empty (Low Signal), skipping Feishu notification.")
        else:
            # 调用 notifier.py 发送给飞书
            send_notification(report)
            logger.info("✅ Step 3 Finished: Notification sent.")
            
    except Exception as e:
        logger.error(f"❌ Critical Error in Notifier: {e}")
        return

    logger.info("🎉 Pipeline Completed Successfully.")

if __name__ == "__main__":
    start_time = time.time()
    run_pipeline()
    print(f"\n⏱️ Total Execution Time: {time.time() - start_time:.2f} seconds")