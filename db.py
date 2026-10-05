import os

import psycopg
from psycopg.rows import dict_row

# Where the database lives. On your Mac this default points at your local Postgres.
# On AWS, DATABASE_URL will be set to the RDS address instead.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/tech_news")


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)   # rows come back as dictionaries


def create_table():
    with get_connection() as conn:                # "with" commits and closes automatically
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                source       TEXT NOT NULL,
                category     TEXT NOT NULL,
                title        TEXT NOT NULL,
                summary      TEXT,
                link         TEXT NOT NULL UNIQUE,
                published_at TIMESTAMPTZ,
                grabbed_at   TIMESTAMPTZ NOT NULL,
                posted_at    TIMESTAMPTZ
            )
        """)


def save_item(conn, item):
    cursor = conn.execute(
        """
        INSERT INTO items
            (source, category, title, summary, link, published_at, grabbed_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (link) DO NOTHING
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
    return cursor.rowcount == 1     # 1 = new row added, 0 = duplicate link, skipped


def get_latest_items(limit=50, category=None):
    query = "SELECT source, category, title, summary, link, published_at FROM items"
    params = []
    if category:
        query += " WHERE category = %s"
        params.append(category)
    query += " ORDER BY COALESCE(published_at, grabbed_at) DESC LIMIT %s"
    params.append(limit)

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def get_unposted_items(conn):
    return conn.execute(
        """
        SELECT id, source, title, link FROM items
        WHERE posted_at IS NULL
        ORDER BY COALESCE(published_at, grabbed_at) ASC
        """
    ).fetchall()


def mark_posted(conn, item_id):
    conn.execute("UPDATE items SET posted_at = NOW() WHERE id = %s", (item_id,))


if __name__ == "__main__":
    create_table()
    print("Table ready.")