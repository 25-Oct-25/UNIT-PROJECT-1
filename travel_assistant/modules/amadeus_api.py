import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

TOKEN_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"

def _check_credentials():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET must be set in .env")

def get_access_token() -> Optional[str]:
    try:
        _check_credentials()
    except RuntimeError as e:
        print("❌", e)
        return None

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    try:
        resp = requests.post(TOKEN_URL, data=data, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        print("❌ Network error while requesting access token:", e)
        return None

    try:
        token = resp.json().get("access_token")
        if not token:
            print("❌ No access_token in response:", resp.text)
            return None
        return token
    except ValueError:
        print("❌ Invalid JSON in token response:", resp.text)
        return None