
import feedparser
import requests
from bs4 import BeautifulSoup
import sqlite3
import logging
import backoff
import os
from datetime import datetime
from urllib.parse import urlparse
from typing import List, Dict
from schemas import FeedsConfig

DB_PATH = 'news_cache.db'

# SQL schema for articles table
TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS articles (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    site        TEXT,
    title       TEXT,
    url         TEXT,
    published   DATETIME,
    content     TEXT,
    summary     TEXT,
    notion_page TEXT,
    UNIQUE(site, title)
);
"""

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')


def init_db():
    """Tworzy tabelę articles jeśli nie istnieje."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(TABLE_SCHEMA)


def clear_cache():
    """Usuwa plik bazy i tworzy go na nowo."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        logger.info("Usunięto stary plik bazy: %s", DB_PATH)
    init_db()
    logger.info("Utworzono nową bazę: %s", DB_PATH)


def is_article_seen(conn, site: str, title: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM articles WHERE site=? AND title=?",
        (site, title)
    )
    return cur.fetchone() is not None


def mark_article(conn, site: str, title: str, url: str, published: datetime, content: str):
    conn.execute(
        "INSERT OR IGNORE INTO articles(site,title,url,published,content) VALUES(?,?,?,?,?)",
        (site, title, url, published, content)
    )

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException,),
                      max_tries=5)
def fetch_url(url: str) -> requests.Response:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp


def scrape_full_text(url: str) -> str:
    resp = fetch_url(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    article = soup.find('article') or soup.find('main') or soup
    paragraphs = article.find_all('p')
    return "\n\n".join(p.get_text() for p in paragraphs)


def fetch_all_news(feeds: FeedsConfig) -> List[Dict]:
    init_db()
    new_count = 0
    for feed_url in feeds.tech_ai_feeds + feeds.general_feeds:
        url_str = str(feed_url)
        site = urlparse(url_str).netloc
        try:
            feed = feedparser.parse(url_str)
        except Exception as e:
            logger.error("Nie można sparsować %s: %s", url_str, e)
            continue

        with sqlite3.connect(DB_PATH) as conn:
            for entry in feed.entries:
                title = entry.title
                if is_article_seen(conn, site, title):
                    continue

                pub_struct = getattr(entry, 'published_parsed', None)
                published = datetime(*pub_struct[:6]) if pub_struct else datetime.utcnow()
                try:
                    content = scrape_full_text(entry.link)
                except Exception:
                    content = entry.get('summary', '')

                mark_article(conn, site, title, entry.link, published, content)
                new_count += 1
    logger.info(f"Pobrano {new_count} nowych artykułów")
    return []  # nie zwracamy artykułów, bo pracujemy na DB