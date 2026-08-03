from app.event_fingerprint import create_fingerprint

event = {

    "event": "Fed Governor Speech",

    "category": "Central Bank",

    "markets": [
        "Gold",
        "USD"
    ],

    "matched_keywords": [
        "barkin"
    ]
}

print(create_fingerprint(event))