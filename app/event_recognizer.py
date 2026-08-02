import re

from app.market_events import MARKET_EVENTS


def recognize_event(article):
    """
    Find the best matching market event.
    """

    text = (
        article["title"] + " " + article.get("summary", "")
    ).lower()

    best_event = None
    highest_matches = 0

    # Check every event
    for event_name, event in MARKET_EVENTS.items():

        matches = []

        # Check every keyword
        for keyword in event["keywords"]:

            pattern = r"\b" + re.escape(keyword.lower()) + r"\b"

            if re.search(pattern, text):
                matches.append(keyword)

        # Keep only the best matching event
        if len(matches) > highest_matches:

            highest_matches = len(matches)

            best_event = {
                "event": event_name,
                "category": event["category"],
                "importance": event["importance"],
                "urgency": event["urgency"],
                "markets": event["markets"],
                "confidence": min(100, len(matches) * 25),
                "matched_keywords": matches
            }

    return best_event