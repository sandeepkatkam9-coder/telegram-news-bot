def format_message(article, event, impact):

    message = ""

    message += "🚨 AUTO TRADE-HUB\n\n"

    message += f"🏦 Event\n{event['event']}\n\n"

    message += f"📰 Headline\n{article['title']}\n\n"

    message += f"📂 Category\n{event['category']}\n\n"

    message += f"⭐ Importance\n{event['importance']}/100\n\n"

    message += "📈 Expected Market Impact\n"

    if impact:

        for market, level in impact.items():
            message += f"\n• {market}: {level}"

    return message