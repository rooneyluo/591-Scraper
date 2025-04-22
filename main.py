import random
import time
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from app.crawler import run_crawler
from app.line_notify import push_to_line
from app.libs.utils import concat_items
from datetime import datetime

from config import RENT_RANGE, MIN_PING, MAX_PING, NEW_WITHIN_HOURS, RANDOM_DELAY, TEST_MODE

load_dotenv()

scheduler = BlockingScheduler(timezone='Asia/Taipei')

def log_and_run():
    delay = random.randint(0, 1800)  # random delay between 0 and 30 minutes
    print(f"[Scheduler] Waiting for {delay} seconds to simulate human behavior...")

    if RANDOM_DELAY:
        time.sleep(delay)

    start_message = f"""現在時間: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n租金區間: {RENT_RANGE[0]}~{RENT_RANGE[1]}元\n坪數: {MIN_PING}~{MAX_PING}坪\n租屋類型:[獨立套房, 分租套房]\n更新物件: {NEW_WITHIN_HOURS}小時內\n開始爬蟲...\n-----------------------"""
    end_message = "-----------------------\n爬蟲結束，請查看租屋資訊！"

    items = run_crawler()
    message = concat_items(items)
    push_to_line(start_message + "\n" + message + "\n" + end_message)

    print("[Scheduler] Crawler finished.")

# Run at specific hours
# 7, 10, 12, 15, 18, 20, 22, 24
@scheduler.scheduled_job('cron', hour='7, 10, 12, 15, 18, 20, 22, 24', minute=0)
def scheduled_job():
    log_and_run()

if __name__ == '__main__':
    print("[Scheduler] Starting...")

    if TEST_MODE:
        print("[Test Mode] Running crawler immediately...")
        log_and_run()

    scheduler.start()
