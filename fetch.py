import feedparser
import requests
import html
import re
from datetime import datetime, timezone
import db                                   # NEW: your own db.py file

FEEDS = [
    {"name": "GameSpot", "category": "games", "url": "https://www.gamespot.com/feeds/game-news/"},
    {"name": "Tom's Hardware", "category": "pc components", "url": "https://www.tomshardware.com/feeds.xml"},
]

HEADERS = {
    "User-Agent": "tech-news-bot/0.1 (+https://github.com/chris-pleska/tech-news)"
}


def clean_summary(text, max_length=300):
    if not text:
        return None

    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = " ".join(text.split())

    if len(text) <= max_length:
        return text

    cut = text[:max_length]
    cut = cut.rsplit(" ", 1)[0]
    return cut + "..."


def clean_date(entry):
    parsed = entry.get("published_parsed")
    if not parsed:
        return None

    date = datetime(*parsed[:6], tzinfo=timezone.utc)
    return date.isoformat()


def fetch_and_store():
    db.create_table()                                        # make sure the table exists
    conn = db.get_connection()                               # open the database once for the whole run
    grabbed_at = datetime.now(timezone.utc).isoformat()      # the time of this run
    new_items = []                                           # NEW: collects every new item across all feeds

    for feed_info in FEEDS:
        try:
            response = requests.get(feed_info["url"], timeout=10, headers=HEADERS)
            response.raise_for_status()

            feed = feedparser.parse(response.content)
            new_count = 0

            for entry in feed.entries:
                item = {
                    "source": feed_info["name"],
                    "category": feed_info["category"],
                    "title": entry.get("title"),
                    "link": entry.get("link"),
                    "summary": clean_summary(entry.get("summary")),
                    "published_at": clean_date(entry),
                    "grabbed_at": grabbed_at,
                }
                if db.save_item(conn, item):
                    new_count += 1
                    new_items.append(item)                   # NEW: remember it for whoever called us

            conn.commit()
            print(feed_info["name"], ":", new_count, "new")

        except Exception as error:
            print("Failed:", feed_info["name"], "-", error)

    conn.close()
    return new_items                                         # NEW: hand the new items back to the caller


if __name__ == "__main__":                 # only true when you run: python3 fetch.py
    new_items = fetch_and_store()
    print("Total new items:", len(new_items))