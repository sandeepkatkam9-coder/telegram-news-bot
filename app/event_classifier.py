"""
AutoTrade-HUB Market Event Classifier
"""

from app.intelligence_rules import (
    BREAKING_NEWS,
    CENTRAL_BANK,
    ECONOMIC_DATA,
    GEOPOLITICS,
    IGNORE_ARTICLES,
    LOW_PRIORITY,
)


def classify_article(article):

    text = (
        article["title"] + " " + article["summary"]
    ).lower()

    categories = []

    # Ignore Technical Analysis
    if any(word in text for word in IGNORE_ARTICLES):
        categories.append("Technical Analysis")

    # Opinion
    if any(word in text for word in LOW_PRIORITY):
        categories.append("Opinion")

    # Breaking News
    if any(word in text for word in BREAKING_NEWS):
        categories.append("Breaking News")

    # Central Bank
    if any(word in text for word in CENTRAL_BANK):
        categories.append("Central Bank")

    # Economic Data
    if any(word in text for word in ECONOMIC_DATA):
        categories.append("Economic Data")

    # Geopolitics
    if any(word in text for word in GEOPOLITICS):
        categories.append("Geopolitics")

    return categories