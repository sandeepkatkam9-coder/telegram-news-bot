import json
import os

from app.event_fingerprint import create_fingerprint

STORAGE_FILE = "data/sent_news.json"


def load_sent_news():

    if not os.path.exists(STORAGE_FILE):
        return []

    try:

        with open(STORAGE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception:

        return []


def save_sent_news(news):

    with open(STORAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(news, file, indent=4)


def already_sent(event):

    sent_news = load_sent_news()

    fingerprint = create_fingerprint(event)

    return fingerprint in sent_news


def mark_as_sent(event):

    sent_news = load_sent_news()

    fingerprint = create_fingerprint(event)

    if fingerprint not in sent_news:

        sent_news.append(fingerprint)

        save_sent_news(sent_news)