# run_pipeline.py

"""
Główny skrypt, który uruchamia:
1. Pobieranie newsów,
2. Streszczanie przez OpenAI,
3. Zapis do Notion.
"""

from ingest.news_ingestor import fetch_rss_news
from process.news_summarizer import summarize_article
from export.news_to_notion import save_to_notion

print("🔥 RUN_PIPELINE.PY URUCHOMIONY")

def main():
    print("📥 Pobieranie newsów...")
    articles = fetch_rss_news()

    if not articles:
        print("Brak nowych newsów do przetworzenia.")
        return

    summarized = []
    print("✍️  Tworzenie streszczeń...")
    for article in articles:
        summary = summarize_article(article['title'], article['content'])
        summarized.append({
            "title": article['title'],
            "url": article['url'],
            "summary": summary,
            "site": article.get('site', 'unknown')
        })

    print("📤 Zapis do Notion...")
    save_to_notion(summarized)


if __name__ == "__main__":
    main()
