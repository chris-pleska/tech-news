import db
import fetch
import telegram_bot

# A tiny hand-written RSS feed, so tests never need the internet.
# The second item has no <description>, on purpose.
FAKE_FEED = b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>Fake</title>
  <item>
    <title>First story</title>
    <link>https://example.com/1</link>
    <description>Hello</description>
    <pubDate>Thu, 01 Oct 2026 15:00:00 +0000</pubDate>
  </item>
  <item>
    <title>Second story</title>
    <link>https://example.com/2</link>
    <pubDate>Thu, 01 Oct 2026 16:00:00 +0000</pubDate>
  </item>
</channel></rss>"""


class FakeResponse:                       # pretends to be what requests.get() returns
    content = FAKE_FEED

    def raise_for_status(self):           # a real download that worked: nothing to raise
        pass


def fake_get(url, **kwargs):              # pretends to be requests.get()
    return FakeResponse()


def use_fakes(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))       # temporary database, not your real news.db
    monkeypatch.setattr(fetch.requests, "get", fake_get)               # no real downloads
    monkeypatch.setattr(fetch, "FEEDS", [                              # one fake feed instead of your real list
        {"name": "Fake", "category": "games", "url": "https://example.com/feed"},
    ])


def test_no_duplicates(tmp_path, monkeypatch):
    use_fakes(tmp_path, monkeypatch)

    first = fetch.fetch_and_store()       # first run: both stories are new
    second = fetch.fetch_and_store()      # second run: same feed, nothing new

    assert len(first) == 2
    assert len(second) == 0

def test_missing_summary(tmp_path, monkeypatch):
    use_fakes(tmp_path, monkeypatch)

    fetch.fetch_and_store()                                        # save the fake feed

    saved = {item["title"]: item for item in db.get_latest_items()}   # read back what's in the database

    assert saved["First story"]["summary"] == "Hello"              # a normal summary is kept
    assert saved["Second story"]["summary"] is None                # a missing one is saved as empty, no crash

def test_failed_post_is_retried(tmp_path, monkeypatch):
    use_fakes(tmp_path, monkeypatch)
    monkeypatch.setattr(telegram_bot.time, "sleep", lambda seconds: None)   # skip the 3-second pauses in tests
    fetch.fetch_and_store()                                                 # 2 unposted items in the database

    # Round 1: Telegram is "down"
    def failing_send(text):
        raise RuntimeError("Telegram is down")

    monkeypatch.setattr(telegram_bot, "send_message", failing_send)
    assert telegram_bot.post_new_items() == 0          # nothing posted...

    # Round 2: Telegram works again
    sent = []

    def working_send(text):
        sent.append(text)                              # record the message instead of really sending it

    monkeypatch.setattr(telegram_bot, "send_message", working_send)
    assert telegram_bot.post_new_items() == 2          # ...so both items are posted now
    assert len(sent) == 2

    # Round 3: nothing is ever sent twice
    assert telegram_bot.post_new_items() == 0