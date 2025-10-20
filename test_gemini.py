import os
import requests
import json
from dotenv import load_dotenv

# تحميل المفتاح من .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# استخدم الموديل الموجود فعلاً عندك (gemini-2.5-flash)
url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"

payload = {
    "contents": [
        {"parts": [{"text": "Write a short polite email requesting system access."}]}
    ]
}

headers = {"Content-Type": "application/json"}

response = requests.post(url, headers=headers, data=json.dumps(payload))

if response.status_code == 200:
    data = response.json()
    print("\n📩 AI Response:\n")
    print(data["candidates"][0]["content"]["parts"][0]["text"])
else:
    print(f"\n❌ Error {response.status_code}: {response.text}")
