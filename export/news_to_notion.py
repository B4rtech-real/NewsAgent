# export/news_to_notion.py

"""
Zapisuje zestaw streszczonych newsów do Notion jako osobną stronę na dany dzień.
"""

import requests
from datetime import datetime
from dotenv import load_dotenv
import os
from collections import defaultdict
from urllib.parse import urlparse

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def publisher_from_url(url: str) -> str:
    netloc = urlparse(url).netloc
    domain_parts = netloc.replace("www.", "").split(".")
    if "co" in domain_parts[-2]:  # e.g., bbc.co.uk
        return domain_parts[-3].capitalize()
    return domain_parts[-2].capitalize()


def save_to_notion(news_items: list):
    """
    Zapisuje listę newsów jako stronę w Notion.

    Args:
        news_items (list): Lista dictów z 'title', 'url', 'summary'
    """
    date_str = datetime.now().strftime('%Y-%m-%d')

    MAX_BLOCKS = 100
    children_blocks = []

    # Grupuj newsy po nazwie wydawcy z URL
    grouped = defaultdict(list)
    for news in news_items:
        site = publisher_from_url(news['url'])
        grouped[site].append(news)

    # Twórz sekcje w ramach jednej strony
    for site, news_list in grouped.items():
        children_blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": f"{site}"}
                }]
            }
        })

        for news in news_list:
            children_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": f"• {news['title']}\n{news['summary']}\n{news['url']}"
                            }
                        }
                    ]
                }
            })

    children_blocks = children_blocks[:MAX_BLOCKS]

    page_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": f"News - {date_str}"}}]
            }
        },
        "children": children_blocks
    }

    response = requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=page_data)
    if response.status_code != 200:
        raise Exception(f"Błąd Notion API: {response.status_code} - {response.text}")

    print(f"✅ Zapisano {len(news_items)} newsów do Notion na {date_str}.")
