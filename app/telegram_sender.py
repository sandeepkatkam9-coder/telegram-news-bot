from telegram import Bot
from app.config import BOT_TOKEN, CHANNEL_ID


async def send_telegram(message):

    bot = Bot(token=BOT_TOKEN)

    await bot.send_message(
        chat_id=CHANNEL_ID,
        text=message
    )