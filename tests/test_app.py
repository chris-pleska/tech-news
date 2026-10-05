import os
import db
import fetch
import telegram_bot

# A separate database just for tests, because each test empties the table first.
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://localhost/tech_news_test")

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


def use_fakes(monkeypatch):
    monkeypatch.setattr(db, "DATABASE_URL", TEST_DATABASE_URL)     #the test database, never your real one
    db.create_table()                                               # NEW: make sure the table exists
    with db.get_connection() as conn:
        conn.execute("TRUNCATE items")                              # NEW: start every test with an empty table
    monkeypatch.setattr(fetch.requests, "get", fake_get)
    monkeypatch.setattr(fetch, "FEEDS", [
        {"name": "Fake", "category": "games", "url": "https://example.com/feed"},
    ])


def test_no_duplicates(monkeypatch):
    use_fakes(monkeypatch)

    first = fetch.fetch_and_store()       # first run: both stories are new
    second = fetch.fetch_and_store()      # second run: same feed, nothing new

    assert len(first) == 2
    assert len(second) == 0

def test_missing_summary(monkeypatch):
    use_fakes(monkeypatch)

    fetch.fetch_and_store()                                        # save the fake feed

    saved = {item["title"]: item for item in db.get_latest_items()}   # read back what's in the database

    assert saved["First story"]["summary"] == "Hello"              # a normal summary is kept
    assert saved["Second story"]["summary"] is None                # a missing one is saved as empty, no crash

def test_failed_post_is_retried(monkeypatch):
    use_fakes(monkeypatch)
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