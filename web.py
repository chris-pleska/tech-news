from flask import Flask, render_template_string, request
import db
from fetch import FEEDS
import os

app = Flask(__name__)

CATEGORIES = sorted({feed["category"] for feed in FEEDS})     # e.g. ["games", "pc components"]

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tech News</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 760px; margin: 0 auto; padding: 16px; }
    nav a { margin-right: 12px; }
    nav a.active { font-weight: bold; }
    li { margin-bottom: 16px; }
    .meta { color: #666; font-size: 0.85em; }
  </style>
</head>
<body>
  <h1>Tech News</h1>
  <nav>
    <a href="/" class="{{ 'active' if not category }}">All</a>
    {% for c in categories %}
      <a href="/?category={{ c | urlencode }}" class="{{ 'active' if c == category }}">{{ c }}</a>
    {% endfor %}
  </nav>
  <ul>
    {% for item in items %}
      <li>
        <a href="{{ item.link }}">{{ item.title }}</a>
        <div class="meta">{{ item.source }} · {{ item.category }} · {{ item.published_at or "" }}</div>
        {% if item.summary %}<div>{{ item.summary }}</div>{% endif %}
      </li>
    {% else %}
      <li>No items yet. Run: python3 fetch.py</li>
    {% endfor %}
  </ul>
</body>
</html>
"""


@app.route("/")
def index():
    category = request.args.get("category")     # from the URL, e.g. /?category=games
    items = db.get_latest_items(limit=50, category=category)
    return render_template_string(PAGE, items=items, categories=CATEGORIES, category=category)


@app.route("/health")
def health():
    return {"status": "ok"}, 200     # the load balancer just needs a fast 200 back


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")    # CHANGED: debug only if FLASK_DEBUG=1
