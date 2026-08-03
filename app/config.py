import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ==========================================
# Telegram
# ==========================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# ==========================================
# Notification Rules
# ==========================================

MIN_IMPORTANCE = 90

# ==========================================
# Tracked Assets
# ==========================================

TRACKED_ASSETS = [

    # Precious Metals
    "gold",
    "xau",
    "xauusd",
    "silver",
    "xag",
    "xagusd",

    # Oil
    "oil",
    "crude",
    "wti",
    "brent",

    # Crypto
    "bitcoin",
    "btc",

    # Forex
    "usd",
    "dollar",
    "eur",
    "euro",
    "gbp",
    "pound"
]