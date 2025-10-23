"""
config/settings.py
-------------------
Handles environment configuration and Gemini API setup.
Loads API keys securely from environment variables.
"""
import os
import google.generativeai as genai

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not YOUTUBE_API_KEY:
    raise EnvironmentError("❌ Missing YOUTUBE_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("❌ Missing GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
