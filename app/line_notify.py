import os
import json
import sys
import requests
import traceback
from config import SEND_LINE_MESSAGE

from dotenv import load_dotenv

load_dotenv()

LINE_API = "https://api.line.me/v2/bot/message/push"
LINE_TO_GROUP = os.getenv("LINE_TO_GROUP_ID_2")

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN_2")
LINE_TO_USER = os.getenv("LINE_TO_USER_ID_2")

def split_message_by_entry(message: str, max_length: int = 4000) -> list[str]:
    """
    將訊息依照「一筆一筆物件」進行分段，避免切到中間。
    每筆以兩個換行 \n\n 分隔。
    """
    entries = message.strip().split("\n\n")  # 每筆資料間用兩個換行分隔
    chunks = []
    current_chunk = ""

    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue

        # 預估加入這筆後是否超過最大長度
        if len(current_chunk) + len(entry) + 2 > max_length:  # +2 為 \n\n
            chunks.append(current_chunk.strip())
            current_chunk = entry + "\n\n"
        else:
            current_chunk += entry + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def push_to_line(message: str):
    """
    Send a message to LINE, but only if the item has not been pushed before.
    
    Args:
        message (str): The message to send
        item_id (str): A unique identifier for the item being pushed
        
    Returns:
        bool: True if the message was sent successfully, False otherwise
    """

    if not message or not isinstance(message, str):
        print("[LINE] Invalid message format")
        return False
        
    if not SEND_LINE_MESSAGE:
        print("[LINE] Debug mode, not sending message.")
        return True

    # Check for required environment variables
    if not LINE_TOKEN:
        print("[LINE] Missing LINE_CHANNEL_ACCESS_TOKEN in .env")
        return False
        
    # Determine recipient - prefer group if available, fallback to user
    recipient = LINE_TO_GROUP or LINE_TO_USER
    if not recipient:
        print("[LINE] Missing both LINE_TO_GROUP_ID and LINE_TO_USER_ID in .env")
        return False

    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }

    MAX_LEN = 4000
    chunks = chunks = split_message_by_entry(message, max_length=MAX_LEN) #[message[i:i + MAX_LEN] for i in range(0, len(message), MAX_LEN)]

    if len(chunks) > 1:
        print(f"[LINE] Message too long, splitting into {len(chunks)} parts")
    else:
        print("[LINE] Sending single message part")

    payload = {
        "to": recipient,
        "messages": [
            {
                "type": "text",
                "text": chunk
            }
            for chunk in chunks
        ]
    }

    try:       
        res = requests.post(LINE_API, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            print("[LINE] Message sent successfully")
            return True
        else:
            print(f"[LINE] Failed with status code {res.status_code}: {res.text}")
            return False
    except requests.exceptions.Timeout:
        print("[LINE] Request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("[LINE] Connection error - check network connectivity")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[LINE] Request exception: {str(e)}")
        return False
    except Exception as e:
        print(f"[LINE] Unexpected exception: {str(e)}")
        traceback.print_exc()
        return False
