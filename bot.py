import os
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("BOT_TOKEN exists:", BOT_TOKEN is not None)
print("CHAT_ID:", CHAT_ID)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": "✅ Test Message from GitHub Actions!\n\nIf you received this, your Telegram bot is working."
}

response = requests.post(url, data=payload)

print("Status Code:", response.status_code)
print("Response:", response.text)
