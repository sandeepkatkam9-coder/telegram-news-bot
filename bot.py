from app.news_fetcher import fetch_news
from app.event_recognizer import recognize_event
from app.decision_engine import should_notify

news = fetch_news()

print("\nIMPORTANT NEWS\n")

for article in news:

    event = recognize_event(article)

    if not should_notify(event):
        continue

    print("=" * 80)
    print("Headline      :", article["title"])
    print("Event         :", event["event"])
    print("Category      :", event["category"])
    print("Importance    :", event["importance"])
    print("Confidence    :", f"{event['confidence']}%")
    print("Markets       :", ", ".join(event["markets"]))
    print("Matched Words :", ", ".join(event["matched_keywords"]))