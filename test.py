import os
import google.generativeai as genai

api = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
assert api, "No GEMINI_API_KEY/GOOGLE_API_KEY in environment"
genai.configure(api_key=api)

model = genai.GenerativeModel("gemini-1.5-flash")
resp = model.generate_content("Say only: OK")
print("OK?" , getattr(resp, "text", None))
