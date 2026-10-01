import sqlite3

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

if __name__ == "__main__":     # only runs when you do: python3 db.py
    create_table()
    print("Table ready.")

