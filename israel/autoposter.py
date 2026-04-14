#!/usr/bin/env python3
"""
autoposter.py — AppleDaily Israel (Hebrew)
פרסום אוטומטי: RSS → GPT-4o → WordPress

סביבת עבודה (.env):
  WP_URL         — כתובת האתר, למשל https://appledaily.co.il
  WP_PASSWORD    — טוקן API (X-AppDaily-Token)
  OPENAI_API_KEY — מפתח OpenAI API
"""

import os
import time
import sqlite3
import hashlib
import logging
import json
import requests
import feedparser
from datetime import datetime, timezone
from openai import OpenAI
from dotenv import load_dotenv

# ─── Configuration ────────────────────────────────────────────────────────────

load_dotenv()

WP_URL         = os.getenv("WP_URL", "https://appledaily.co.il")
WP_API_TOKEN   = os.getenv("WP_PASSWORD", "")   # stored as WP_PASSWORD secret
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DB_PATH        = os.getenv("DB_PATH", "seen_articles_il.db")

OPENAI_DELAY = 3          # pause between GPT requests (seconds)
MAX_ARTICLES_PER_RUN = 5  # max articles per run

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── RSS Sources ──────────────────────────────────────────────────────────────

RSS_FEEDS = [
    {"name": "MacRumors",    "url": "https://feeds.macrumors.com/MacRumors-All"},
    {"name": "9to5Mac",      "url": "https://9to5mac.com/feed"},
    {"name": "AppleInsider", "url": "https://appleinsider.com/rss/news"},
    {"name": "The Verge",    "url": "https://www.theverge.com/apple/rss/index.xml"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/apple"},
]

# ─── Deduplication DB ─────────────────────────────────────────────────────────

def init_db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen (
            url_hash  TEXT PRIMARY KEY,
            url       TEXT,
            title     TEXT,
            posted_at TEXT
        )
    """)
    conn.commit()
    return conn

def is_seen(conn: sqlite3.Connection, url: str) -> bool:
    h = hashlib.md5(url.encode()).hexdigest()
    return conn.execute("SELECT 1 FROM seen WHERE url_hash=?", (h,)).fetchone() is not None

def mark_seen(conn: sqlite3.Connection, url: str, title: str):
    h = hashlib.md5(url.encode()).hexdigest()
    conn.execute(
        "INSERT OR IGNORE INTO seen (url_hash, url, title, posted_at) VALUES (?,?,?,?)",
        (h, url, title, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()

# ─── RSS Parsing ──────────────────────────────────────────────────────────────

def fetch_new_articles(conn: sqlite3.Connection) -> list[dict]:
    new_articles = []
    for feed_info in RSS_FEEDS:
        log.info(f"Reading RSS: {feed_info['name']}")
        try:
            feed = feedparser.parse(feed_info["url"])
        except Exception as e:
            log.warning(f"Error parsing {feed_info['name']}: {e}")
            continue
        for entry in feed.entries:
            url = entry.get("link", "")
            if not url or is_seen(conn, url):
                continue
            content = entry.get("summary", "") or entry.get("description", "")
            new_articles.append({
                "source":  feed_info["name"],
                "url":     url,
                "title":   entry.get("title", ""),
                "content": content,
            })
    log.info(f"New articles found: {len(new_articles)}")
    return new_articles

# ─── GPT-4o: Translate + Rewrite to Hebrew ───────────────────────────────────

def translate_and_rewrite(client: OpenAI, title: str, content: str, source: str, url: str) -> dict | None:
    prompt = f"""אתה עורך של אתר חדשות ישראלי בעברית העוסק באפל וטכנולוגיה.

קיבלת מאמר חדשותי מהמקור "{source}".
המשימה שלך:
1. תרגם את הכותרת לעברית — בצורה תמציתית וברורה.
2. כתוב טקסט חדש בעברית — עיבוד מחדש, לא תרגום ישיר.
   סגנון: עיתונאי, תוסס, ללא מילים מיותרות. אורך: 150–300 מילים.
3. הכתיבה צריכה להיות מימין לשמאל (RTL) בעברית תקינה.
4. בסוף הטקסט הוסף את השורה: «מקור: <a href="{url}">{source}</a>»

ענה אך ורק בפורמט JSON:
{{"title_he": "...", "content_he": "..."}}

כותרת מקורית: {title}

טקסט מקורי:
{content[:3000]}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=800,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        log.error(f"GPT-4o error: {e}")
        return None

# ─── WordPress REST API ───────────────────────────────────────────────────────

def post_to_wordpress(title_he: str, content_he: str) -> int | None:
    """
    Publishes article to WordPress via custom REST API endpoint.
    Authentication via X-AppDaily-Token header.
    Returns new post ID or None on error.
    """
    try:
        api_url = f"{WP_URL.rstrip('/')}/wp-json/appledaily/v1/post"
        resp = requests.post(
            api_url,
            json={"title": title_he, "content": content_he},
            headers={
                "Content-Type": "application/json",
                "X-AppDaily-Token": WP_API_TOKEN,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        post_id = data.get("id")
        log.info(f"✅ Published (ID={post_id}): {title_he[:60]}")
        return int(post_id) if post_id else None
    except requests.HTTPError as e:
        log.error(f"❌ WP REST API HTTP {e.response.status_code}: {e.response.text[:200]}")
        return None
    except Exception as e:
        log.error(f"❌ Publish error: {e}")
        return None

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    log.info("=" * 50)
    log.info("AppleDaily IL autoposter — start")
    log.info("=" * 50)

    if not WP_API_TOKEN:
        log.error("WP_PASSWORD (API token) not set in .env")
        return
    if not OPENAI_API_KEY:
        log.error("OPENAI_API_KEY not set in .env")
        return

    client = OpenAI(api_key=OPENAI_API_KEY)
    conn   = init_db(DB_PATH)

    new_articles = fetch_new_articles(conn)
    if not new_articles:
        log.info("No new articles. Exiting.")
        conn.close()
        return

    to_process = new_articles[:MAX_ARTICLES_PER_RUN]
    log.info(f"Processing {len(to_process)} of {len(new_articles)} articles")

    published = 0
    for article in to_process:
        log.info(f"Translating: {article['title'][:70]}")

        result = translate_and_rewrite(
            client, article["title"], article["content"],
            article["source"], article["url"]
        )

        mark_seen(conn, article["url"], article["title"])

        if not result:
            log.warning("Skipping (GPT error)")
            continue

        title_he   = result.get("title_he", "").strip()
        content_he = result.get("content_he", "").strip()

        if not title_he or not content_he:
            log.warning("GPT returned empty result, skipping")
            continue

        post_id = post_to_wordpress(title_he, content_he)
        if post_id:
            published += 1

        time.sleep(OPENAI_DELAY)

    log.info(f"Done. Published: {published}/{len(to_process)}")
    conn.close()


if __name__ == "__main__":
    main()
