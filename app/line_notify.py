import os
import requests
from config import SEND_LINE_MESSAGE

from dotenv import load_dotenv

load_dotenv()

LINE_API = "https://api.line.me/v2/bot/message/push"
LINE_TO_GROUP = os.getenv("LINE_TO_GROUP_ID")

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_TO_USER = os.getenv("LINE_TO_USER_ID")

def push_to_line(message: str):
    if not SEND_LINE_MESSAGE:
        print("[LINE] Debug mode, not sending message.")
        return

    if not LINE_TOKEN or not LINE_TO_USER:
        print("[LINE] Missing token or user ID in .env")
        return

    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": LINE_TO_GROUP,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    try:       
        res = requests.post(LINE_API, headers=headers, json=payload)
        if res.status_code != 200:
            print("[LINE] Failed:", res.text)
    except Exception as e:
        print("[LINE] Exception:", e)


