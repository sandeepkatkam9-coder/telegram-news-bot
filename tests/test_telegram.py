import asyncio

from app.telegram_sender import send_telegram


async def main():
    await send_telegram(
        "✅ AutoTrade-HUB Test\n\n"
        "Congratulations!\n\n"
        "Your Telegram bot is connected successfully."
    )


if __name__ == "__main__":
    asyncio.run(main())