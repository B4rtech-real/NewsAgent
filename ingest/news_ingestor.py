# news_ingestor.py

"""
Moduł do pobierania najnowszych newsów ze wskazanych źródeł
(np. RSS + scraping) i przygotowania ich do przetworzenia
(przez LLM i zapis do Notion).
Pobiera pełną treść artykułu i sprawdza, czy news był już wcześniej dodany
na podstawie SQLite cache.
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import sqlite3
import yaml
import os
from pathlib import Path


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}
BASE_DIR = Path(__file__).resolve().parent.parent  # project root
DB_PATH = BASE_DIR / "news_cache.db"
def load_sources():
    """
    Ładuje źródła RSS z config.yaml z katalogu nadrzędnego.
    """
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    config_path = os.path.abspath(config_path)
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("tech_ai_feeds", []) + config.get("general_feeds", [])

def init_db():
    """
    Inicjalizuje bazę danych SQLite i tworzy tabelę cache, jeśli nie istnieje.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seen_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT,
            title TEXT,
            url TEXT,
            published TEXT,
            UNIQUE(site, title)
        )
    """)
    conn.commit()
    conn.close()

def is_article_seen(site: str, title: str) -> bool:
    """
    Sprawdza, czy artykuł o danym tytule z danego źródła już istnieje.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM seen_articles WHERE site = ? AND title = ?", (site, title))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_article_seen(site: str, title: str, url: str, published: str):
    """
    Dodaje artykuł do cache jako przetworzony.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO seen_articles (site, title, url, published)
        VALUES (?, ?, ?, ?)
    """, (site, title, url, published))
    conn.commit()
    conn.close()

def extract_full_text(url: str) -> str:
    """
    Próbuje pobrać pełną treść artykułu ze strony URL.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(response.text, "html.parser")
        article_tags = soup.find_all(['article', 'main', 'section'])
        paragraphs = []
        for tag in article_tags:
            paragraphs.extend([p.get_text(strip=True) for p in tag.find_all('p') if len(p.get_text(strip=True)) > 40])

        if not paragraphs:
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if len(p.get_text(strip=True)) > 40]

        return "\n".join(paragraphs[:10])

    except Exception as e:
        print(f"Błąd pobierania artykułu: {url}\n{e}")
        return ""

def fetch_rss_news():
    """
    Pobiera newsy z listy RSS i zwraca te, które są nowe (nie były zapisane w cache).
    """
    init_db()
    all_news = []

    sources = load_sources()
    for feed_url in sources:
        feed = feedparser.parse(feed_url)
        site_name = feed_url.split("/")[2]  # np. www.money.pl -> money.pl

        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "")
            published = entry.get("published", "")

            if is_article_seen(site_name, title):
                continue

            full_text = extract_full_text(link)
            if not full_text:
                full_text = summary

            all_news.append({
                "title": title,
                "url": link,
                "content": full_text
            })

            mark_article_seen(site_name, title, link, published)
            time.sleep(1)
            print(title, link, site_name)

    return all_news

if __name__ == "__main__":
    news = fetch_rss_news()
    print(f"Pobrano {len(news)} nowych newsów")
