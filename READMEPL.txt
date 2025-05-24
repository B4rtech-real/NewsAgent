Opis projektu
AI News Agent to kompleksowy pipeline do automatycznego:

Pozyskiwania artykułów z RSS (feedy technologiczne i ogólne).

Scraping’u pełnej treści stron.

Generowania podsumowań z użyciem OpenAI (GPT-3.5).

Eksportu podsumowań do Notion, pogrupowanych według źródła.

Wymagania

Python 3.8 lub wyższy

Konto OpenAI i klucz API (OPENAI_API_KEY)

Integracja Notion i token (NOTION_TOKEN, NOTION_DATABASE_ID)

Instalacja

git clone https://github.com/<your-org>/ai-news-agent.git
cd ai-news-agent
pip install -r requirements.txt

W pliku requirements.txt powinny znaleźć się: pyyaml pydantic feedparser requests beautifulsoup4 backoff notion-client openai

Konfiguracja

Utwórz plik .env lub ustaw zmienne środowiskowe:

export OPENAI_API_KEY="twój_klucz"
export NOTION_TOKEN="twój_token"
export NOTION_DATABASE_ID="id_bazy_notion"

Edytuj config.yaml, aby dodać/zmienić RSS feedy.

Struktura projektu

├── schemas.py              # Definicja konfiguracji Pydantic
├── ingest/                 # Moduł do pobierania i cache’owania artykułów
│   └── news_ingestor.py
├── process/                # Moduł do podsumowywania tekstu
│   └── news_summarizer.py
├── export/                 # Moduł do eksportu do Notion
│   └── news_to_notion.py
├── run_pipeline.py         # Główny skrypt uruchamiający pipeline
└── config.yaml             # Lista źródeł RSS

Użytkowanie

Aby uruchomić cały proces:

python run_pipeline.py

Aby wyczyścić lokalny cache i zacząć od nowa:

python run_pipeline.py --clear-cache

Licencja & Kontakt
Projekt dostępny na licencji MIT. Wszelkie pytania lub pomysły proszę kierować przez GitHub Issues lub kontakt mailowy.

