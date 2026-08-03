IMPACT_MATRIX = {

    "Fed Rate Decision": {
        "Gold": "Very High",
        "USD": "Very High",
        "EUR": "High",
        "GBP": "High",
        "Oil": "Medium",
        "Bitcoin": "Medium"
    },

    "Fed Governor Speech": {
        "Gold": "High",
        "USD": "High",
        "EUR": "Medium",
        "GBP": "Medium",
        "Oil": "Low",
        "Bitcoin": "Low"
    },

    "CPI": {
        "Gold": "Very High",
        "USD": "Very High",
        "EUR": "Medium",
        "GBP": "Medium",
        "Oil": "Low",
        "Bitcoin": "Medium"
    },

    "GDP": {
        "Gold": "Medium",
        "USD": "High",
        "EUR": "Medium",
        "GBP": "Medium",
        "Oil": "Low",
        "Bitcoin": "Low"
    },

    "PMI": {
        "Gold": "Medium",
        "USD": "Medium",
        "EUR": "Medium",
        "GBP": "Medium"
    },

    "OPEC+": {
        "Oil": "Very High",
        "Gold": "High",
        "USD": "Medium",
        "Bitcoin": "Low"
    },

    "War": {
        "Gold": "Very High",
        "Oil": "Very High",
        "USD": "High",
        "Bitcoin": "Medium"
    }
}


def get_market_impact(event_name):
    return IMPACT_MATRIX.get(event_name, {})