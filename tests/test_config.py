import sys
from pathlib import Path

# Add the project root to Python's path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import BOT_TOKEN, CHANNEL_ID

print("Bot Token Loaded :", BOT_TOKEN is not None)
print("Channel ID Loaded:", CHANNEL_ID is not None)

print("Bot Token Length :", len(BOT_TOKEN) if BOT_TOKEN else 0)
print("Channel ID       :", CHANNEL_ID)