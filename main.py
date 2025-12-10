import sys
import logging
import time

from src.fetcher import fetch_all_data
from src.processor import process_data
from src.notifier import send_notification
# [新增] 引入存储模块
from src.storage import filter_new_items, save_items

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("🚀 SOTA Watch Pipeline Started (V0.2 with DB)")

    # --- Step 1: 抓取 ---
    logger.info("📡 Step 1: Fetching data...")
    try:
        raw_data = fetch_all_data()
        if not raw_data:
            logger.warning("⚠️ No data fetched. Stop.")
            return
    except Exception as e:
        logger.error(f"❌ Fetcher Error: {e}")
        return

    # --- [新增] Step 1.5: 去重 ---
    # 这一步非常关键！它决定了我们是不是在做无用功
    try:
        new_data = filter_new_items(raw_data)
        if not new_data:
            logger.info("💤 All items have been processed before. Nothing new.")
            return
        logger.info(f"✨ Found {len(new_data)} NEW items to analyze.")
    except Exception as e:
        logger.error(f"❌ Deduplication Error: {e}")
        new_data = raw_data # 降级策略

    # --- Step 2: 分析 ---
    logger.info("🧠 Step 2: Analyzing with AI...")
    try:
        # 注意：现在我们传入的是 new_data (去重后的数据)
        # Processor 里的 [:5] 限制依然存在用于测试，但在生产环境有了去重后，
        # 这里的 new_data 通常本身就不会太多，所以是安全的。
        report = process_data(new_data)
        
        # [新增] 提取出高分项目用于存储
        # 我们的 process_data 返回的是字符串报告，
        # 但我们需要把 update 后的字典存入数据库。
        # 这里的实现略有 Trick: process_data 修改了 new_data 列表里的字典对象(引用传递)
        # 所以 new_data 现在已经包含了 'score', 'summary' 等字段
        
        high_quality_items = [
            item for item in new_data 
            if item.get('score', 0) >= 6  # 只存 6 分以上的
        ]
        
    except Exception as e:
        logger.error(f"❌ Processor Error: {e}")
        return

    # --- [新增] Step 2.5: 存档 ---
    logger.info("💾 Step 2.5: Saving to database...")
    try:
        if high_quality_items:
            save_items(high_quality_items)
        else:
            logger.info("📭 No high-score items to save.")
    except Exception as e:
        logger.error(f"❌ Storage Error: {e}")

    # --- Step 3: 推送 ---
    logger.info("📨 Step 3: Notifying...")
    try:
        if "No high-score updates" in report or len(high_quality_items) == 0:
            logger.info("🔕 Low signal, skipping notification.")
        else:
            send_notification(report)
            logger.info("✅ Notification sent.")
    except Exception as e:
        logger.error(f"❌ Notifier Error: {e}")
        return

    logger.info("🎉 Pipeline Finished.")

if __name__ == "__main__":
    start_time = time.time()
    run_pipeline()
    print(f"\n⏱️ Execution Time: {time.time() - start_time:.2f}s")
    