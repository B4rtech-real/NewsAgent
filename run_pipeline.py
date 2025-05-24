import argparse
import yaml
from schemas import FeedsConfig
from ingest.news_ingestor import init_db, clear_cache, fetch_all_news, DB_PATH
from process.news_summarizer import process_summaries
from export.news_to_notion import save_articles_by_site


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