import os, requests
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

for ver in ["v1", "v1beta"]:
    url = f"https://generativelanguage.googleapis.com/{ver}/models?key={API_KEY}"
    r = requests.get(url)
    print(f"\n== {ver} == status {r.status_code}")
    print(r.text[:2000])
