import os
import requests
from dotenv import load_dotenv
load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
print(NOTION_TOKEN, NOTION_DATABASE_ID)

url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

response = requests.post(url, headers=headers)

# ✅ Check and print status code before trying to access the data
if response.status_code != 200:
    print("❌ Error occurred!")
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
else:
    print("✅ Success. Processing data...")
    data = response.json()
    for result in data["results"]:
        print(result)