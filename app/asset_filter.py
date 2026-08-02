from app.market_dictionary import MARKET_KEYWORDS


def detect_assets(article):

    text = (
        article["title"] +
        " " +
        article["summary"]
    ).lower()

    detected = []

    for market, keywords in MARKET_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:

                detected.append(market)
                break

    return detected