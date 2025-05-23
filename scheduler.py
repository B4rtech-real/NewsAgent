# scheduler.py

"""
Uruchamia agenta codziennie o 15:00 przy użyciu biblioteki `schedule`.
"""

import schedule
import time
import subprocess

# Funkcja, która wywołuje główny skrypt
def run_pipeline():
    print("🕒 Uruchamianie agenta newsowego...")
    subprocess.run(["python", "run_pipeline.py"])

# Zaplanuj uruchomienie codziennie o 15:00
schedule.every().day.at("15:00").do(run_pipeline)

print("🗓️  Agent gotowy. Będzie uruchamiany codziennie o 15:00.")

while True:
    schedule.run_pending()
    time.sleep(60)
