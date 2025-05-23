# run_pipeline.py

"""
Główny skrypt, który uruchamia:
1. Pobieranie newsów,
2. Streszczanie przez OpenAI,
3. Zapis do Notion.
"""
from cache.summary_cache import init_summary_db, get_cached_summary, store_summary
from ingest.news_ingestor import fetch_rss_news
from process.news_summarizer import summarize_article
from export.news_to_notion import save_to_notion
from dotenv import load_dotenv
load_dotenv()

print("🔥 RUN_PIPELINE.PY URUCHOMIONY")
init_summary_db()
def main():
    print("📥 Pobieranie newsów...")
    articles = fetch_rss_news()
    # Lista słów kluczowych związanych z AI
    AI_KEYWORDS = ["ai", "artificial intelligence", "machine learning", "deep learning", "gpt", "openai",
                   "neural network", "llm", "chatbot"]

    def is_ai_related(article):
        content = f"{article['title']} {article['content']}".lower()
        return any(keyword in content for keyword in AI_KEYWORDS)

    # Filtrowanie tylko wiadomości związanych z AI
    articles = list(filter(is_ai_related, articles))
    print(f"🧠 AI-related articles: {len(articles)}")
    if not articles:
        print("Brak nowych newsów do przetworzenia.")
        return

    summarized = []
    print("✍️  Tworzenie streszczeń...")
    for article in articles:
        cached = get_cached_summary(article['url'])
        if cached:
            summary = cached
            print(f"📄 Z cache: {article['title']}")
        else:
            summary = summarize_article(article['title'], article['content'])
            store_summary(article['url'], article['title'], summary)
            print(f"🧠 Nowe streszczenie: {article['title']}")

        summarized.append({
            "title": article['title'],
            "url": article['url'],
            "summary": summary,
            "site": article.get('site') or "Unknown"
        })
    print("📤 Zapis do Notion...")
    save_to_notion(summarized)


if __name__ == "__main__":
    main()
