import os, time
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

load_dotenv(override=True)

api = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
assert api, "No GEMINI/GOOGLE API KEY in env"
genai.configure(api_key=api)

# نفضّل موديلات الفلاش المتاحة عادة في المجاني
PREFERRED = [
    "gemini-2.5-flash-lite",       # إن وجد
    "gemini-2.0-flash",            # ثابت
    "gemini-flash-latest",
    "gemini-2.0-flash-lite",
]

def pick_model():
    models = [m for m in genai.list_models() if "generateContent" in getattr(m, "supported_generation_methods", [])]
    names = [m.name for m in models]
    print("Available:", *names, sep="\n - ")
    for pref in PREFERRED:
        for n in names:
            if pref in n:
                return n
    # تجنّب pro/exp
    for n in names:
        if "pro" not in n and "exp" not in n:
            return n
    return names[0] if names else None

model_name = pick_model()
assert model_name, "No available models"
print("Using:", model_name)

model = genai.GenerativeModel(model_name=model_name)
try:
    resp = model.generate_content("Say only: OK")
    print("Response:", getattr(resp, "text", None))
except ResourceExhausted as e:
    print("⚠️ Rate/Quota hit on this model:", model_name)
    print("Details:", e.message)
