import feedparser
import requests

URL = "https://www.gamespot.com/feeds/game-news/"
HEADERS = {
    "User-Agent": "tech-news-bot/0.1 (+https://github.com/chris-pleska/tech-news)"
    
}

response = requests.get(URL, timeout=10, headers=HEADERS)
response.raise_for_status()

feed = feedparser.parse(response.content)

for entry in feed.entries:
    print(entry.title)
    print(entry.link)
    print()
