from app.formatter import format_message

article = {
    "title": "Fed's Barkin: Inflation remains too high"
}

event = {
    "event": "Fed Governor Speech",
    "category": "Central Bank",
    "importance": 90
}

impact = {
    "Gold": "High",
    "USD": "High",
    "EUR": "Medium"
}

print(format_message(article, event, impact))