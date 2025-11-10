from dotenv import load_dotenv
from app.crawler import run_crawler
from app.line_notify import push_to_line
from app.libs.utils import concat_items
from datetime import datetime
from zoneinfo import ZoneInfo

from config import RENT_RANGE, MIN_PING, MAX_PING, NEW_WITHIN_HOURS, KINDS, SEARCH_MODE

load_dotenv()

KINDS_TABLE = {
    "1": "整層住家",
    "2": "獨立套房",
    "3": "分租套房",
    "4": "雅房",
    "8": "車位",
    "24": "其他"
}

SEARCH_MODE_TABLE = {
    "district": "行政區",
    "metro": "捷運站"
}

def main():
    start_message = f"""現在時間: {datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M")}\n搜尋模式: {SEARCH_MODE_TABLE[SEARCH_MODE]}\n租金區間: {RENT_RANGE[0]}~{RENT_RANGE[1]}元\n坪數: {MIN_PING}~{MAX_PING}坪\n租屋類型:{'、'.join(KINDS_TABLE[k] for k in KINDS)}\n更新物件: {NEW_WITHIN_HOURS}小時內\n開始爬蟲...\n-----------------------"""
    end_message = "-----------------------\n爬蟲結束，請查看租屋資訊！"

    items = run_crawler()
    message = concat_items(items)
    push_to_line(start_message + "\n" + message + "\n" + end_message)

    print("[Crawler] Finished.")

if __name__ == "__main__":
    main()
