# process/news_summarizer.py

"""
Streszcza treść artykułów za pomocą OpenAI GPT-3.5.
"""

import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def summarize_article(title: str, content: str) -> str:
    """
    Tworzy streszczenie 2–3 zdania dla danego artykułu.

    Args:
        title (str): Tytuł artykułu
        content (str): Pełna treść

    Returns:
        str: streszczenie
    """
    prompt = f"""
    Streść poniższy artykuł w maksymalnie 2–3 zdaniach, podkreślając najważniejsze informacje.

    Tytuł: {title}
    Treść: {content[:2000]}  # ograniczamy długość prompta
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Stwórz krótkie podsumowanie artykułu."},
                {"role": "user", "content": f"Tytuł: {title}\n\nTreść: {content}"}
            ],
            max_tokens=300,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Błąd podczas streszczania:\n", e)
        return "[Błąd w streszczaniu]"

