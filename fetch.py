import feedparser
import requests
import html
import re
from datetime import datetime, timezone   # NEW: for building clean dates

# Each feed: a name, a category, and its URL.
FEEDS = [
    {"name": "GameSpot", "category": "games", "url": "https://www.gamespot.com/feeds/game-news/"},
    {"name": "Tom's Hardware", "category": "pc components", "url": "https://www.tomshardware.com/feeds.xml"},
]

HEADERS = {
    "User-Agent": "tech-news-bot/0.1 (+https://github.com/chris-pleska/tech-news)"
}


def clean_summary(text, max_length=300):
    if not text:                          # missing or empty summary: nothing to clean
        return None

    text = re.sub(r"<[^>]+>", " ", text)  # remove HTML tags like <p> or <img ...>
    text = html.unescape(text)            # turn codes like &amp; back into &
    text = " ".join(text.split())         # squash extra spaces and newlines into single spaces

    if len(text) <= max_length:           # already short enough: done
        return text

    cut = text[:max_length]               # take the first 300 characters
    cut = cut.rsplit(" ", 1)[0]           # back up to the last full word
    return cut + "..."


def clean_date(entry):                                    # NEW
    parsed = entry.get("published_parsed")                # the date already split into pieces, in UTC
    if not parsed:                                        # some entries have no date at all
        return None

    date = datetime(*parsed[:6], tzinfo=timezone.utc)     # year, month, day, hour, minute, second
    return date.isoformat()                               # e.g. "2026-10-01T15:38:13+00:00"


for feed_info in FEEDS:                          # repeat everything below once per feed
    print("---", feed_info["name"], "---")       # show which feed we're on

    try:                                         # attempt this feed...
        response = requests.get(feed_info["url"], timeout=10, headers=HEADERS)
        response.raise_for_status()              # turn a failed download into an error

        feed = feedparser.parse(response.content)

        for entry in feed.entries[:3]:
            item = {
                "source": feed_info["name"],
                "category": feed_info["category"],
                "title": entry.get("title"),
                "link": entry.get("link"),
                "summary": clean_summary(entry.get("summary")),
                "published_at": clean_date(entry),
            }
            print(item)

    except Exception as error:                   # ...and if anything above failed:
        print("Failed:", feed_info["name"], "-", error)   # say so, then the loop continues
        