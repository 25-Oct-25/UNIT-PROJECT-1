# core/dns_intel/config.py
from pathlib import Path
import os
from dotenv import load_dotenv

# === Paths ===
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results" / "level1"
HISTORY_FILE = DATA_DIR / "dns_history_level1.json"
DOMAINS_FILE = DATA_DIR / "domains.txt"

# === Environment Variables ===
env_path = ROOT / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# API Keys (used in higher levels)
IPINFO_TOKEN = os.getenv("IPINFO_TOKEN", "")
ABUSEIPDB_KEY = os.getenv("ABUSEIPDB_KEY", "")
VT_APIKEY = os.getenv("VT_APIKEY", "")
