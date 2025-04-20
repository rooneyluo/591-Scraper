import random
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from app.crawler import run_crawler
from app.line_notify import push_to_line
from datetime import datetime

from config import RENT_RANGE, MIN_PING, MAX_PING, NEW_WITHIN_HOURS, RANDOM_DELAY

load_dotenv()

scheduler = BlockingScheduler(timezone='Asia/Taipei')

# run every 6 hours with random delay (0~60 seconds)
@scheduler.scheduled_job('interval', hours=12)
def scheduled_job():
    delay = random.randint(0, 1800)  # random delay between 0 and 30 minutes
    print(f"[Scheduler] Waiting for {delay} seconds to simulate human behavior...")
    if RANDOM_DELAY:
        time.sleep(delay)
    push_to_line(f"""現在時間: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n租金區間: {RENT_RANGE[0]}~{RENT_RANGE[1]}元\n坪數: {MIN_PING}~{MAX_PING}坪\n租屋類型:[獨立套房, 分租套房]\n更新物件: {NEW_WITHIN_HOURS}小時內\n開始爬蟲...""")
    run_crawler()
    push_to_line("爬蟲結束，請查看租屋資訊！")
    print("[Scheduler] Crawler finished.")

if __name__ == '__main__':
    print("[Scheduler] Starting...")
    scheduled_job()  # initial run
    scheduler.start()
