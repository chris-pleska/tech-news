import feedparser
import requests

# Each feed: a name, a category, and its URL.
# Note the commas after each } except the last one.
FEEDS = [
    {"name": "GameSpot", "category": "games", "url": "https://www.gamespot.com/feeds/game-news/"},
    {"name": "Tom's Hardware", "category": "pc components", "url": "https://www.tomshardware.com/feeds.xml"},
]

HEADERS = {
    "User-Agent": "tech-news-bot/0.1 (+https://github.com/chris-pleska/tech-news)"
}

for feed_info in FEEDS:                          # repeat everything below once per feed
    print("---", feed_info["name"], "---")       # show which feed we're on

    try:                                         # attempt this feed...
        response = requests.get(feed_info["url"], timeout=10, headers=HEADERS)
        response.raise_for_status()              # turn a failed download into an error

        feed = feedparser.parse(response.content)

        for entry in feed.entries:               # each headline in this feed
            print(entry.title)
            print(entry.link)
            print()

    except Exception as error:                   # ...and if anything above failed:
        print("Failed:", feed_info["name"], "-", error)   # say so, then the loop continues