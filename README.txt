Project description
AI News Agent is a full end-to-end pipeline for:

Fetching articles from RSS feeds (tech & general channels).

Scraping full content from web pages.

Generating summaries using OpenAI (GPT-3.5).

Exporting summaries to Notion, grouped by source.

Requirements

Python 3.8+

OpenAI account & API key (OPENAI_API_KEY)

Notion integration & token (NOTION_TOKEN, NOTION_DATABASE_ID)

Installation

git clone https://github.com/<your-org>/ai-news-agent.git
cd ai-news-agent
pip install -r requirements.txt

requirements.txt should include: pyyaml pydantic feedparser requests beautifulsoup4 backoff notion-client openai

Configuration

Create a .env file or set environment variables:

export OPENAI_API_KEY="your_key"
export NOTION_TOKEN="your_token"
export NOTION_DATABASE_ID="your_database_id"

Edit config.yaml to add or modify RSS feeds.

Project structure

├── schemas.py              # Pydantic config definitions
├── ingest/                 # Module for fetching & caching articles
│   └── news_ingestor.py
├── process/                # Module for summarizing text
│   └── news_summarizer.py
├── export/                 # Module for exporting to Notion
│   └── news_to_notion.py
├── run_pipeline.py         # Main script to run the pipeline
└── config.yaml             # List of RSS sources

Usage

To run the full pipeline:

python run_pipeline.py

To clear the cache and start fresh:

python run_pipeline.py --clear-cache

License & Contact
This project is MIT licensed. For questions or feedback open an issue on GitHub or reach out via email.

