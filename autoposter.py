#!/usr/bin/env python3
"""
autoposter.py — AppleDaily.news / iphonefeed.news
Автоматический парсинг RSS → перевод GPT-4o → публикация в WordPress + Telegram

Запуск:
  python autoposter.py

Переменные окружения (файл .env или GitHub Secrets):
  WP_URL              — URL сайта, напр. https://iphonefeed.news
  WP_PASSWORD         — API токен (X-AppDaily-Token)
  OPENAI_API_KEY      — ключ OpenAI API
  TELEGRAM_BOT_TOKEN  — токен Telegram-бота (опционально)
  TELEGRAM_CHANNEL_ID — ID канала, напр. @iphonefeed_news (опционально)
"""

import os
import re
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

# ─── Настройка ────────────────────────────────────────────────────────────────

load_dotenv()

WP_URL              = os.getenv("WP_URL", "https://iphonefeed.news")
WP_API_TOKEN        = os.getenv("WP_PASSWORD", "")
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY", "")
DB_PATH             = os.getenv("DB_PATH", "seen_articles.db")
TELEGRAM_BOT_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")

OPENAI_DELAY         = 3   # пауза между запросами к GPT (сек)
MAX_ARTICLES_PER_RUN = 7   # максимум публикаций за один запуск
TITLE_DEDUP_WINDOW   = 3   # дней — окно для дедупликации по заголовку
TITLE_DEDUP_THRESH   = 0.6 # Jaccard-порог схожести заголовков

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ─── RSS-источники ────────────────────────────────────────────────────────────

RSS_FEEDS = [
    # Tier 1 — крупнейшие Apple-издания
    {"name": "MacRumors",    "url": "https://feeds.macrumors.com/MacRumors-All"},
    {"name": "9to5Mac",      "url": "https://9to5mac.com/feed"},
    {"name": "AppleInsider", "url": "https://appleinsider.com/rss/news"},
    {"name": "The Verge",    "url": "https://www.theverge.com/apple/rss/index.xml"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/apple"},
    # Tier 2 — дополнительные источники
    {"name": "Cult of Mac",  "url": "https://www.cultofmac.com/feed/"},
    {"name": "MacStories",   "url": "https://www.macstories.net/feed/"},
    {"name": "iMore",        "url": "https://www.imore.com/rss.xml"},
    {"name": "MacWorld",     "url": "https://www.macworld.com/feed"},
    {"name": "Mac Observer", "url": "https://www.macobserver.com/feed/"},
    {"name": "TechCrunch",   "url": "https://techcrunch.com/tag/apple/feed/"},
]

# ─── Фильтр рекламных статей ────────────────────────────────────────────────

PROMO_KEYWORDS = [
    "deal", "deals", "discount", "sale", "% off", "save $",
    "coupon", "promo", "lowest price", "best price", "price drop",
    "on sale", "black friday", "cyber monday", "prime day",
    "get it for", "grab it for", "limited time", "limited offer",
    "for just $", "for only $", "starting at $",
]

def is_promo(title: str) -> bool:
    """Возвращает True, если заголовок статьи — рекламный/скидочный."""
    t = title.lower()
    return any(kw in t for kw in PROMO_KEYWORDS)

# ─── Дедупликация по схожести заголовков ─────────────────────────────────────

# Стоп-слова английского языка (убираем при сравнении заголовков)
_STOP = {
    'the','a','an','is','are','was','were','be','been','being',
    'has','have','had','do','does','did','will','would','could',
    'should','may','might','must','can','get','gets','got','now',
    'new','and','or','but','in','on','at','to','for','of','with',
    'as','by','from','up','about','into','through','during','before',
    'after','its','it','this','that','these','those','first','last',
    'one','two','three','four','five','also','just','like','over',
    'than','more','most','some','all','how','what','when','where',
    'why','which','who','says','report','according','via','here',
    'out','back','off','next','other','another','own','still',
}

def _title_sig(title: str) -> frozenset:
    """Возвращает набор значимых слов заголовка для Jaccard-сравнения."""
    words = re.findall(r'[a-zA-Z]+', title.lower())
    return frozenset(w for w in words if len(w) > 3 and w not in _STOP)

def is_similar_title_seen(conn: sqlite3.Connection, title: str) -> bool:
    """
    Проверяет, есть ли в базе статья с похожим заголовком за последние
    TITLE_DEDUP_WINDOW дней (Jaccard similarity >= TITLE_DEDUP_THRESH).
    """
    sig = _title_sig(title)
    if len(sig) < 2:
        return False
    rows = conn.execute(
        "SELECT title FROM seen WHERE posted_at > datetime('now', ? || ' days')",
        (f"-{TITLE_DEDUP_WINDOW}",),
    ).fetchall()
    for (stored_title,) in rows:
        stored_sig = _title_sig(stored_title)
        if not stored_sig:
            continue
        union = len(sig | stored_sig)
        if union == 0:
            continue
        jaccard = len(sig & stored_sig) / union
        if jaccard >= TITLE_DEDUP_THRESH:
            log.debug(f"    Jaccard={jaccard:.2f} '{stored_title[:50]}' ≈ '{title[:50]}'")
            return True
    return False

# ─── База дедупликации ────────────────────────────────────────────────────────

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

# ─── Извлечение изображения из RSS ───────────────────────────────────────────

def extract_image_url(entry: dict) -> str:
    """
    Пытается извлечь URL изображения из RSS-записи.
    Приоритет: media:thumbnail > media:content > <img> в контенте.
    """
    # 1. media:thumbnail (MacRumors, AppleInsider)
    thumbnails = getattr(entry, "media_thumbnail", None)
    if thumbnails and isinstance(thumbnails, list) and thumbnails[0].get("url"):
        url = thumbnails[0]["url"]
        if url.startswith("http"):
            return url

    # 2. media:content с type image/*
    media_content = getattr(entry, "media_content", None)
    if media_content:
        for mc in media_content:
            if mc.get("type", "").startswith("image") and mc.get("url", "").startswith("http"):
                return mc["url"]

    # 3. enclosures (подкасты и некоторые фиды)
    for enc in getattr(entry, "enclosures", []):
        if enc.get("type", "").startswith("image") and enc.get("href", "").startswith("http"):
            return enc["href"]

    # 4. Первый <img> в HTML-контенте summary
    content_html = entry.get("summary", "") or entry.get("description", "")
    img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content_html, re.IGNORECASE)
    if img_match:
        img_url = img_match.group(1)
        if img_url.startswith("http") and "pixel" not in img_url and "1x1" not in img_url:
            return img_url

    return ""

# ─── Парсинг RSS ──────────────────────────────────────────────────────────────

def fetch_new_articles(conn: sqlite3.Connection) -> list[dict]:
    new_articles = []
    for feed_info in RSS_FEEDS:
        log.info(f"Читаю RSS: {feed_info['name']}")
        try:
            feed = feedparser.parse(feed_info["url"])
        except Exception as e:
            log.warning(f"Ошибка при парсинге {feed_info['name']}: {e}")
            continue
        for entry in feed.entries:
            url = entry.get("link", "")
            if not url:
                continue

            # 1. Пропускаем уже виденные URL
            if is_seen(conn, url):
                continue

            raw_title = entry.get("title", "")

            # 2. Фильтр рекламных статей
            if is_promo(raw_title):
                log.info(f"  [SKIP promo] {raw_title[:70]}")
                mark_seen(conn, url, raw_title)
                continue

            # 3. Дедупликация по схожести заголовка (та же история из другого источника)
            if is_similar_title_seen(conn, raw_title):
                log.info(f"  [SKIP dup]   {raw_title[:70]}")
                mark_seen(conn, url, raw_title)
                continue

            content = entry.get("summary", "") or entry.get("description", "")
            image_url = extract_image_url(entry)
            new_articles.append({
                "source":    feed_info["name"],
                "url":       url,
                "title":     raw_title,
                "content":   content,
                "image_url": image_url,
            })

    log.info(f"Найдено новых уникальных статей: {len(new_articles)}")
    return new_articles

# Категории сайта и их slug-и
CATEGORIES = {
    "iphone": ["iphone", "ios", "ipad", "ipados"],
    "mac": ["mac", "macos", "macbook", "imac", "mac mini", "mac studio", "mac pro"],
    "apple": ["apple watch", "airpods", "apple tv", "homepod", "apple card", "apple pay", "apple intelligence", "siri", "apple"],
    "apps": ["app store", "приложени", "игр", "safari", "garageband", "imovie", "xcode"],
    "ipad": ["ipad"],
}

def classify_category(title_ru: str, content_ru: str) -> str:
    """Простая классификация по ключевым словам."""
    text = (title_ru + " " + content_ru).lower()
    for slug, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in text:
                return slug
    return "apple"  # По умолчанию

# ─── GPT-4o: перевод + рерайт ────────────────────────────────────────────────

def translate_and_rewrite(client: OpenAI, title: str, content: str, source: str, url: str) -> dict | None:
    prompt = f"""Ты редактор русскоязычного новостного сайта об Apple и технологиях.

Тебе дана новостная статья из источника «{source}».
Твоя задача:
1. Перевести заголовок на русский язык — ёмко и чётко.
2. Написать НОВЫЙ текст на русском — рерайт, не прямой перевод.
   Стиль: информационный, живой, без воды. Длина: 150–300 слов.
3. Первый абзац (1–2 предложения) — уникальное авторское вступление: почему эта новость важна для пользователей Apple в России или что она означает на практике. Это должно отличать нашу статью от простого перевода.
4. В конце текста добавь строку: «Источник: <a href="{url}">{source}</a>»

Ответь строго в формате JSON:
{{"title_ru": "...", "content_ru": "..."}}

Оригинальный заголовок: {title}

Оригинальный текст:
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
        log.error(f"Ошибка GPT-4o: {e}")
        return None

# ─── WordPress REST API ───────────────────────────────────────────────────────

def post_to_wordpress(title_ru: str, content_ru: str, image_url: str = "", category: str = "apple") -> int | None:
    """
    Публикует статью в WordPress через кастомный REST API эндпоинт.
    Если есть image_url — использует /post-v2 (с поддержкой featured image).
    Аутентификация по токену X-AppDaily-Token.
    Возвращает ID новой записи или None при ошибке.
    """
    try:
        endpoint = "post-v2" if image_url else "post"
        api_url = f"{WP_URL.rstrip('/')}/wp-json/iphonefeed/v1/{endpoint}"
        payload = {"title": title_ru, "content": content_ru, "category": category}
        if image_url:
            payload["image_url"] = image_url
            log.info(f"  → Изображение: {image_url[:80]}")

        resp = requests.post(
            api_url,
            json=payload,
            headers={
                "Content-Type": "application/json",
                "X-AppDaily-Token": WP_API_TOKEN,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        post_id = data.get("id")
        log.info(f"✅ Опубликовано (ID={post_id}): {title_ru[:60]}")
        return int(post_id) if post_id else None
    except requests.HTTPError as e:
        log.error(f"❌ WP REST API HTTP {e.response.status_code}: {e.response.text[:200]}")
        return None
    except Exception as e:
        log.error(f"❌ Ошибка публикации: {e}")
        return None

# ─── Telegram ─────────────────────────────────────────────────────────────────

def post_to_telegram(title_ru: str, post_url: str, excerpt: str = "") -> bool:
    """
    Публикует анонс статьи в Telegram-канал.
    Требует TELEGRAM_BOT_TOKEN и TELEGRAM_CHANNEL_ID в .env.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
        return False

    # Берём первые 200 символов текста как краткое описание
    clean_excerpt = re.sub(r'<[^>]+>', '', excerpt)[:200].strip()
    if clean_excerpt and not clean_excerpt.endswith(('.',  '!', '?')):
        clean_excerpt += '…'

    text = f"*{title_ru}*"
    if clean_excerpt:
        text += f"\n\n{clean_excerpt}"
    text += f"\n\n[Читать полностью →]({post_url})"

    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id":    TELEGRAM_CHANNEL_ID,
                "text":       text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False,
            },
            timeout=15,
        )
        resp.raise_for_status()
        log.info(f"📱 Telegram: отправлено «{title_ru[:50]}»")
        return True
    except Exception as e:
        log.warning(f"⚠️  Telegram ошибка: {e}")
        return False

# ─── Главная функция ──────────────────────────────────────────────────────────

def main():
    log.info("=" * 50)
    log.info("AppleDaily autoposter — запуск")
    log.info("=" * 50)

    if not WP_API_TOKEN:
        log.error("WP_PASSWORD (API token) не задан в .env")
        return
    if not OPENAI_API_KEY:
        log.error("OPENAI_API_KEY не задан в .env")
        return

    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID:
        log.info(f"Telegram: включён → {TELEGRAM_CHANNEL_ID}")
    else:
        log.info("Telegram: не настроен (TELEGRAM_BOT_TOKEN / TELEGRAM_CHANNEL_ID отсутствуют)")

    client = OpenAI(api_key=OPENAI_API_KEY)
    conn   = init_db(DB_PATH)

    new_articles = fetch_new_articles(conn)
    if not new_articles:
        log.info("Новых статей нет. Завершение.")
        conn.close()
        return

    to_process = new_articles[:MAX_ARTICLES_PER_RUN]
    log.info(f"Обрабатываю {len(to_process)} из {len(new_articles)} статей")

    published = 0
    for article in to_process:
        log.info(f"Перевожу: {article['title'][:70]}")

        result = translate_and_rewrite(
            client, article["title"], article["content"],
            article["source"], article["url"]
        )

        mark_seen(conn, article["url"], article["title"])

        if not result:
            log.warning("Пропускаю (ошибка GPT)")
            continue

        title_ru   = result.get("title_ru", "").strip()
        content_ru = result.get("content_ru", "").strip()

        if not title_ru or not content_ru:
            log.warning("GPT вернул пустой результат, пропускаю")
            continue

        category = classify_category(title_ru, content_ru)
        log.info(f"  → Категория: {category}")
        post_id = post_to_wordpress(title_ru, content_ru, article.get("image_url", ""), category)

        if post_id:
            published += 1
            # Формируем URL опубликованной статьи для Telegram
            post_url = f"{WP_URL.rstrip('/')}/?p={post_id}"
            post_to_telegram(title_ru, post_url, content_ru)

        time.sleep(OPENAI_DELAY)

    log.info(f"Готово. Опубликовано: {published}/{len(to_process)}")
    conn.close()


if __name__ == "__main__":
    main()
