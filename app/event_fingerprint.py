"""
AutoTrade-HUB

Event Fingerprint Engine

Creates a unique identifier for each market event.

This helps detect the same event reported by
multiple news sources.
"""


def create_fingerprint(event):

    event_name = event["event"].lower()

    category = event["category"].lower()

    markets = sorted(
        market.lower()
        for market in event["markets"]
    )

    keywords = sorted(
        keyword.lower()
        for keyword in event["matched_keywords"]
    )

    fingerprint = "|".join(
        [event_name, category]
        + markets
        + keywords
    )

    return fingerprint