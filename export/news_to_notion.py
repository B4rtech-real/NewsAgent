import os
import sqlite3
import logging
from notion_client import Client
from typing import Dict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
notion = Client(auth=NOTION_TOKEN)


def make_heading(text: str, level: int = 1) -> Dict:
    typ = f"heading_{level}"
    return {"type": typ, typ: {"rich_text": [{"type":"text","text":{"content":text}}]}}


def make_paragraph(text: str) -> Dict:
    return {"type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":text}}]}}


def save_articles_by_site():
    conn = sqlite3.connect('news_cache.db')
    cur = conn.cursor()
    cur.execute("SELECT id, site, title, published, url, summary FROM articles WHERE notion_page IS NULL")
    rows = cur.fetchall()
    grouped = {}
    for art_id, site, title, published, url, summary in rows:
        grouped.setdefault(site, []).append((art_id, title, published, url, summary))

    for site, arts in grouped.items():
        page_title = site
        children = [make_heading(page_title, 1)]
        for art_id, title, published, url, summary in arts:
            children.append(make_heading(title, 2))
            children.append(make_paragraph(f"{published} — {url}"))
            for chunk in [summary[i:i+2000] for i in range(0, len(summary or ''), 2000)]:
                children.append(make_paragraph(chunk))
        try:
            page = notion.pages.create(
                parent={"database_id": DATABASE_ID},
                properties={"Name":{"title":[{"type":"text","text":{"content":page_title}}]}},
                children=children
            )
            page_id = page['id']
            for art_id, *_ in arts:
                cur.execute("UPDATE articles SET notion_page=? WHERE id=?", (page_id, art_id))
            conn.commit()
            logger.info("✅ Wyeksportowano do Notion: %s", site)
        except Exception as e:
            logger.error("❌ Błąd eksportu %s: %s", site, e)