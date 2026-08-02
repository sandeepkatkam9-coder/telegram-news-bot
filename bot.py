from app.news_fetcher import fetch_news
from app.asset_filter import detect_assets
from app.event_classifier import classify_article

news = fetch_news()

print(f"\nArticles Found: {len(news)}\n")

for article in news:

    assets = detect_assets(article)

    if not assets:
        continue

    categories = classify_article(article)

    print("=" * 80)
    print(article["title"])
    print("Assets     :", ", ".join(assets))

    if categories:
        print("Categories :", ", ".join(categories))
    else:
        print("Categories : General Market News")