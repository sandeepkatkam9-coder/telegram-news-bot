import feedparser

from app.rss_sources import RSS_FEEDS


def fetch_news():
    """
    Download latest news from all RSS feeds.
    """

    all_news = []

    for source_name, url in RSS_FEEDS.items():

        try:
            feed = feedparser.parse(url)

            for entry in feed.entries:

                article = {
                    "source": source_name,
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", "")
                }

                all_news.append(article)

        except Exception as e:
            print(f"Error reading {source_name}: {e}")

    return all_news