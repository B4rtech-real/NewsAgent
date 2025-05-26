import openai
import backoff
import logging
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()


def split_into_chunks(text, max_length=6000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

openai.api_key = os.getenv("OPENAI_API_KEY")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

# Ustaw OPENAI_API_KEY w środowisku
# openai.api_key = os.getenv("OPENAI_API_KEY")  # jeśli potrzebne

@backoff.on_exception(
    backoff.expo,
    (openai.error.ServiceUnavailableError, openai.error.RateLimitError),
    max_tries=5, jitter=backoff.full_jitter
)
def summarize_text(text: str) -> str:
    chunks = split_into_chunks(text)

    summaries = []
    for chunk in chunks:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a concise summarizer."},
                {"role": "user", "content": f"Summarize the following text:\n\n{chunk}"}
            ],
            max_tokens=300,
            temperature=0.3,
            timeout=15
        )
        summaries.append(resp.choices[0].message.content.strip())

    # Możesz połączyć te części w jedno podsumowanie (albo skrócić jeszcze raz)
    joined = " ".join(summaries)

    # Finalne streszczenie łącznego tekstu (opcjonalne drugie podsumowanie)
    final_resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You summarize multiple partial summaries into a single short summary."},
            {"role": "user", "content": joined}
        ],
        max_tokens=300,
        temperature=0.3,
        timeout=15
    )
    return final_resp.choices[0].message.content.strip()


def process_summaries():
    conn = sqlite3.connect('news_cache.db')
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM articles WHERE summary IS NULL")
    rows = cur.fetchall()
    logger.info(f"Znaleziono {len(rows)} artykułów do podsumowania")
    for art_id, content in rows:
        logger.info(f"Podsumowuję artykuł ID={art_id}...")
        summary = summarize_text(content)
        cur.execute("UPDATE articles SET summary=? WHERE id=?", (summary, art_id))
        conn.commit()
