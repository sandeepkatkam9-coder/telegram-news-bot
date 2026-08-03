import asyncio

from app.news_fetcher import fetch_news
from app.event_recognizer import recognize_event
from app.decision_engine import should_notify
from app.impact_engine import get_market_impact
from app.formatter import format_message
from app.telegram_sender import send_telegram
from app.storage import already_sent, mark_as_sent


def main():

    news = fetch_news()

    print("\n" + "=" * 80)
    print("           AUTO TRADE-HUB MARKET INTELLIGENCE")
    print("=" * 80)

    total_articles = len(news)
    important_articles = 0
    telegram_sent = 0
    duplicate_articles = 0

    print(f"\nTotal Articles Scanned : {total_articles}\n")

    for article in news:

        # ==========================================
        # Event Recognition
        # ==========================================

        event = recognize_event(article)

        if event is None:
            continue

        print("=" * 80)
        print(article["title"])
        print(event)    

        # ==========================================
        # Decision Engine
        # ==========================================

        if not should_notify(event):
            continue

        important_articles += 1

        # ==========================================
        # Duplicate Detection
        # ==========================================

        if already_sent(event):

            duplicate_articles += 1

            print(f"⏭ Already Sent : {article['title']}")

            continue

        # ==========================================
        # Market Impact
        # ==========================================

        impact = get_market_impact(event["event"])

        # ==========================================
        # Terminal Output
        # ==========================================

        print("=" * 80)
        print(f"Headline      : {article['title']}")
        print(f"Event         : {event['event']}")
        print(f"Category      : {event['category']}")
        print(f"Importance    : {event['importance']}")
        print(f"Confidence    : {event['confidence']}%")
        print(f"Markets       : {', '.join(event['markets'])}")
        print(f"Matched Words : {', '.join(event['matched_keywords'])}")

        print("\nExpected Market Impact")

        if impact:

            for market, level in impact.items():
                print(f"  {market:<10} : {level}")

        else:

            print("  No impact profile available.")

        # ==========================================
        # Format Telegram Message
        # ==========================================

        telegram_message = format_message(
            article,
            event,
            impact
        )

        # ==========================================
        # Send Telegram
        # ==========================================

        try:

            asyncio.run(
                send_telegram(
                    telegram_message
                )
            )

            telegram_sent += 1

            mark_as_sent(event)

            print("\n✅ Telegram Alert Sent Successfully")

        except Exception as e:

            print(f"\n❌ Telegram Error : {e}")

        print()

    # ==========================================
    # Summary
    # ==========================================

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"Articles Scanned     : {total_articles}")
    print(f"Important News Found : {important_articles}")
    print(f"Telegram Alerts Sent : {telegram_sent}")
    print(f"Duplicate Articles   : {duplicate_articles}")

    print("=" * 80)


if __name__ == "__main__":
    main()