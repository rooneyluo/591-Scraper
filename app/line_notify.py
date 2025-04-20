import os
import sys
import requests
import traceback
from config import SEND_LINE_MESSAGE

from dotenv import load_dotenv

load_dotenv()

LINE_API = "https://api.line.me/v2/bot/message/push"
LINE_TO_GROUP = os.getenv("LINE_TO_GROUP_ID")

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_TO_USER = os.getenv("LINE_TO_USER_ID")

def push_to_line(message: str):
    """
    Send a message to LINE
    
    Args:
        message (str): The message to send
        
    Returns:
        bool: True if the message was sent successfully, False otherwise
    """
    if not message or not isinstance(message, str):
        print("[LINE] Invalid message format")
        return False
        
    # Truncate message if it's too long (LINE has a limit of 5000 characters)
    if len(message) > 5000:
        message = message[:4997] + "..."
        print("[LINE] Message truncated due to length limit")
    
    if not SEND_LINE_MESSAGE:
        print("[LINE] Debug mode, not sending message.")
        return True

    # Check for required environment variables
    if not LINE_TOKEN:
        print("[LINE] Missing LINE_CHANNEL_ACCESS_TOKEN in .env")
        return False
        
    # Determine recipient - prefer group if available, fallback to user
    recipient = LINE_TO_GROUP
    if not recipient:
        if not LINE_TO_USER:
            print("[LINE] Missing both LINE_TO_GROUP_ID and LINE_TO_USER_ID in .env")
            return False
        recipient = LINE_TO_USER
        print("[LINE] Using user ID as recipient")

    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": recipient,
        "messages": [
            {
                "type": "text",
                "text": message
            }
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
