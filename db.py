import sqlite3

from datetime import datetime, timezone     # NEW: to timestamp when an item was posted

DB_PATH = "news.db"     # the database file; it's created automatically the first time


def get_connection():
    return sqlite3.connect(DB_PATH)     # opens the database file (creates it if missing)


def create_table():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id           INTEGER PRIMARY KEY,
            source       TEXT NOT NULL,
            category     TEXT NOT NULL,
            title        TEXT NOT NULL,
            summary      TEXT,
            link         TEXT NOT NULL UNIQUE,
            published_at TEXT,
            grabbed_at   TEXT NOT NULL,
            posted_at    TEXT
        )
    """)
    conn.commit()     # save the change to the file
    conn.close()      # close the database when done

def save_item(conn, item):
    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO items
            (source, category, title, summary, link, published_at, grabbed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item["source"],
            item["category"],
            item["title"],
            item["summary"],
            item["link"],
            item["published_at"],
            item["grabbed_at"],
        ),
    )
    return cursor.rowcount == 1     # True if a new row was added, False if it was a duplicate


def get_latest_items(limit=50, category=None):
    conn = get_connection()
    conn.row_factory = sqlite3.Row     # lets us read columns by name, like row["title"]

    query = "SELECT source, category, title, summary, link, published_at FROM items"
    params = []
    if category:                       # only filter when a category was asked for
        query += " WHERE category = ?"
        params.append(category)
    query += " ORDER BY COALESCE(published_at, grabbed_at) DESC LIMIT ?"     # newest first; fall back to grab time if no date
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]     # plain dicts are easier to use in templates

def get_unposted_items(conn):
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT id, source, title, link FROM items
        WHERE posted_at IS NULL
        ORDER BY COALESCE(published_at, grabbed_at) ASC
        """
    ).fetchall()
    return [dict(row) for row in rows]     # oldest first, so the channel reads in time order


def mark_posted(conn, item_id):
    conn.execute(
        "UPDATE items SET posted_at = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), item_id),
    )

if __name__ == "__main__":     # only runs when you do: python3 db.py
    create_table()
    print("Table ready.")

