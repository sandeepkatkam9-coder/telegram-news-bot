import os
import requests
import feedparser

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_FEEDS = [
    "https://www.forexfactory.com/rss/news",
    "https://www.fxstreet.com/rss/news"
]

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }

    requests.post(url, data=data)

def get_latest_news():
    news = []

    for feed in RSS_FEEDS:
        try:
            rss = feedparser.parse(feed)

            for entry in rss.entries[:3]:
                news.append(
                    f"📰 <b>{entry.title}</b>\n\n"
                    f"🔗 {entry.link}"
                )

        except Exception:
            pass

    return news

if __name__ == "__main__":

    articles = get_latest_news()

    if not articles:
        send_message("No news found.")
    else:
        for article in articles:
            send_message(article)
