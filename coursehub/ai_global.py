import os
from dotenv import load_dotenv
import google.generativeai as genai
from .utils import cgood

load_dotenv()

SYSTEM = (
    "You are a helpful course assistant. "
    "Answer clearly and concisely. Use lists/steps when useful. "
    "If the question is ambiguous, state assumptions briefly."
)

PREFERRED_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
    "gemini-flash-latest",
]

def _configure():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        return False, (
            "No Gemini API key found.\n"
            "Please add GEMINI_API_KEY=your_key_here in a .env file."
        )
    genai.configure(api_key=key)
    return True, None

def _pick_available_model():
    try:
        models = list(genai.list_models())
        full_supported = [
            m.name
            for m in models
            if "generateContent" in getattr(m, "supported_generation_methods", [])
        ]
        short_supported = {name.split("/", 1)[-1] for name in full_supported}
        for short in PREFERRED_MODELS:
            if short in short_supported:
                return short
        return next(iter(short_supported), None)
    except Exception:
        return PREFERRED_MODELS[0]

def ask_global(question: str, model_name: str | None = None) -> str:
    ok, err = _configure()
    if not ok:
        return err

    name = model_name or _pick_available_model()
    if not name:
        return "No compatible Gemini model found."

    try:
        model = genai.GenerativeModel(name, system_instruction=SYSTEM)
        resp = model.generate_content(question)

        if getattr(resp, "prompt_feedback", None) and getattr(resp.prompt_feedback, "block_reason", None):
            return f"[{name}] Blocked by safety filters: {resp.prompt_feedback.block_reason}"

        text = (resp.text or "").strip()
        return cgood(f"(Using model: {name})\n{text}")

    except Exception as e:
        msg = str(e)
        if "quota" in msg.lower() or "429" in msg:
            return (
                f"(Using {name})\n"
                "Quota exceeded for this model/project.\n"
                "Try a lighter model (e.g. gemini-2.5-flash-lite)\n"
                "Or enable billing / use another API key."
            )
        return f"(Using {name})\nGemini error: {e}"