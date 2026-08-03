"""
AutoTrade-HUB Intelligence Rules

This file contains all rules used to classify
and score market news.
"""

# ----------------------------------------------------
# ARTICLE TYPES
# ----------------------------------------------------

BREAKING_NEWS = [
    "breaking",
    "urgent",
    "just in",
    "developing"
]

CENTRAL_BANK = [
    "federal reserve",
    "fed",
    "fomc",
    "kevin warsh",
    "ecb",
    "christine lagarde",
    "bank of england",
    "boe",
    "andrew bailey",
    "interest rate",
    "rate decision"
]

ECONOMIC_DATA = [
    "cpi",
    "ppi",
    "core pce",
    "nfp",
    "nonfarm payrolls",
    "gdp",
    "retail sales",
    "employment",
    "unemployment",
    "ism",
    "pmi"
]

GEOPOLITICS = [
    "war",
    "tariff",
    "sanctions",
    "missile",
    "iran",
    "israel",
    "china",
    "russia",
    "ukraine",
    "middle east"
]

# ----------------------------------------------------
# ARTICLES WE WANT TO IGNORE
# ----------------------------------------------------

IGNORE_ARTICLES = [

    "price forecast",

    "technical analysis",

    "forecast:",

    "support",

    "resistance",

    "rsi",

    "macd",

    "moving average",

    "ema",

    "sma",

    "bollinger",

    "fibonacci",

    "elliott",

    "chart",

    "intraday",

    "daily outlook"
]

# ----------------------------------------------------
# LOW PRIORITY ARTICLES
# ----------------------------------------------------

LOW_PRIORITY = [

    "analyst says",

    "opinion",

    "commentary",

    "weekly outlook",

    "market wrap",

    "preview"
]