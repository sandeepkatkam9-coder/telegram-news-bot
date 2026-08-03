from app.intelligence_rules import (
    BREAKING_NEWS,
    CENTRAL_BANK,
    ECONOMIC_DATA,
    GEOPOLITICS,
    IGNORE_ARTICLES,
    LOW_PRIORITY
)


def score_article(article):

    text = (
        article["title"] +
        " " +
        article["summary"]
    ).lower()

    score = 0

    reasons = []

    # --------------------------
    # Breaking News
    # --------------------------

    if any(word in text for word in BREAKING_NEWS):
        score += 40
        reasons.append("Breaking News")

    # --------------------------
    # Central Bank
    # --------------------------

    if any(word in text for word in CENTRAL_BANK):
        score += 35
        reasons.append("Central Bank")

    # --------------------------
    # Economic Data
    # --------------------------

    if any(word in text for word in ECONOMIC_DATA):
        score += 35
        reasons.append("Economic Data")

    # --------------------------
    # Geopolitics
    # --------------------------

    if any(word in text for word in GEOPOLITICS):
        score += 25
        reasons.append("Geopolitics")

    # --------------------------
    # Ignore Articles
    # --------------------------

    if any(word in text for word in IGNORE_ARTICLES):
        score -= 80
        reasons.append("Technical Analysis")

    # --------------------------
    # Low Priority
    # --------------------------

    if any(word in text for word in LOW_PRIORITY):
        score -= 20
        reasons.append("Opinion")

    return score, reasons