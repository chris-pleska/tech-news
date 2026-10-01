import os
import time

import requests

import db

API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_message(text):
    token = os.environ["TELEGRAM_BOT_TOKEN"]     # from your terminal, never from the code
    chat_id = os.environ["TELEGRAM_CHAT_ID"]

    try:
        response = requests.post(
            API_URL.format(token=token),
            data={"chat_id": chat_id, "text": text},
            timeout=10,
        )
    except requests.RequestException:
        raise RuntimeError("Could not reach Telegram") from None    # hide the URL, it contains the token

    if not response.ok:                          # Telegram said no (wrong token, wrong chat...)
        raise RuntimeError(f"Telegram error {response.status_code}: {response.text[:200]}")


def format_message(item):
    return f"{item['title']}\n{item['source']}\n{item['link']}"


def post_new_items():
    conn = db.get_connection()
    items = db.get_unposted_items(conn)
    posted = 0

    for item in items:
        try:
            send_message(format_message(item))
        except Exception as error:
            print("Failed to post:", item["title"], "-", error)
            break                                # if Telegram is down, the rest would fail too: stop here

        db.mark_posted(conn, item["id"])         # only reached if the send succeeded
        conn.commit()                            # save right away, one item at a time
        posted += 1
        time.sleep(3)                            # Telegram allows about 20 messages a minute in a channel

    conn.close()
    print("Posted", posted, "of", len(items))
    return posted


if __name__ == "__main__":
    post_new_items()