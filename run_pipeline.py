import argparse
import yaml
import openai
from pathlib import Path
from dotenv import load_dotenv
import os
from schemas import FeedsConfig
from ingest.news_ingestor import init_db, clear_cache, fetch_all_news
from process.news_summarizer import process_summaries
from export.news_to_notion import save_articles_by_site

# Wczytaj klucz OpenAI
load_dotenv(dotenv_path=Path(__file__).parent / ".env")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("Brak OPENAI_API_KEY. Upewnij się, że plik .env istnieje i zawiera poprawny klucz.")
openai.api_key = api_key

def load_config(path: str) -> FeedsConfig:
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return FeedsConfig(**data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--clear-cache', action='store_true')
    args = parser.parse_args()

    if args.clear_cache:
        clear_cache()
    init_db()

    cfg = load_config(args.config)
    fetch_all_news(cfg)
    process_summaries()
    save_articles_by_site()

if __name__ == '__main__':
    main()
