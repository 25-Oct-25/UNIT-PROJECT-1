# modules/ai_poster.py
import os, io, time, requests, base64
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import qrcode

# ===== Gemini (optional) =====
try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except Exception:
    _GENAI_AVAILABLE = False

# ===== OpenAI Images (NEW) =====
try:
    from openai import OpenAI  # openai v2 client
    _OPENAI_AVAILABLE = True
except Exception:
    _OPENAI_AVAILABLE = False

load_dotenv()

# ===== Keys (.env) =====
REPLICATE_TOKEN   = os.getenv("REPLICATE_API_TOKEN", "").strip()
HF_TOKEN          = os.getenv("HF_API_TOKEN", "").strip()
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "").strip()

# ===== Model settings =====
REPLICATE_MODEL_OWNER = "black-forest-labs"
REPLICATE_MODEL_NAME  = "flux-1.1-pro"
HF_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

# Gemini init (if any)
if _GENAI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _GEMINI_READY = True
    except Exception:
        _GEMINI_READY = False
else:
    _GEMINI_READY = False

# ====================================
# OpenAI client (lazy) - Initialization fix
# ====================================
def _openai_client():
    if not (_OPENAI_AVAILABLE and OPENAI_API_KEY):
        raise RuntimeError("OpenAI not configured. Install `openai` and set OPENAI_API_KEY in .env")
    
    # Pass the key directly to ensure proper client initialization.
    return OpenAI(api_key=OPENAI_API_KEY)

# ==============================
# Utils
# ==============================
def _ensure_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def _auto_engine():
    """
    Prefer OpenAI for high-quality posters, then Replicate, then HF, then Gemini.
    """
    if OPENAI_API_KEY:
        return "openai"
    if REPLICATE_TOKEN:
        return "replicate"
    if HF_TOKEN:
        return "hf"
    if _GEMINI_READY:
        return "gemini"
    return None

def style_prompt(event_title: str, base_prompt: str = "", style: str = "") -> str:
    t = (event_title or "").lower()
    style_map = {
        "eid": ("elegant eid poster, emerald green & matte gold, glowing lanterns, "
                "crescent moon, subtle islamic geometry, premium serif typography, cinematic rim light"),
        "graduation": ("premium graduation poster, black & gold, mortarboard, depth of field, "
                       "elegant serif typography, dramatic studio lighting"),
        "birthday": ("luxury birthday party poster, deep navy with soft vignette, glossy balloons and confetti, "
                      "center composition for bold title, 3D lighting, bokeh sparks"),
        "meeting": ("minimal corporate poster, blue/gray palette, clean grid, professional sans-serif typography, "
                    "high-contrast modern look"),
        "generic": ("high-end event poster, tasteful palette, professional typography, cinematic lighting"),
        "new_year": ("luxury New Year's Eve poster, black and metallic gold, shimmering confetti, "
                     "elegant champagne glasses, large numerals (e.g., 2025), dramatic spotlight, cinematic look")
    }

    preset = style_map["generic"]

    if any(k in t for k in ["eid", "عيد", "ramadan", "رمضان", "alftar", "إفطار"]):
        preset = style_map["eid"]
    elif any(k in t for k in ["grad", "graduation", "تخرج"]):
        preset = style_map["graduation"]
    elif any(k in t for k in ["birth", "ميلاد", "party", "حفلة"]):
        preset = style_map["birthday"]
    elif any(k in t for k in ["meeting", "اجتماع", "workshop", "training", "conference"]):
        preset = style_map["meeting"]
    elif any(k in t for k in ["new year", "راس السنه"]):
        preset = style_map["new_year"]

    # Bias “football” → soccer unless explicitly American.
    soccer_hint = (
        "realistic soccer stadium pitch with vivid green grass, classic black-and-white soccer ball, "
        "natural lighting, cinematic sports photography"
    )
    if "football" in t and "american" not in t and "nfl" not in t and "rugby" not in t:
        preset = f"{soccer_hint}. {preset}"

    final = f"{preset}. {base_prompt}".strip().rstrip(".")
    if style:
        final += f". {style}"
    final += ". poster layout, centered composition, 4k, ultra-detailed"
    return final

# ==============================
# Overlay (title/subtitle/footer/QR)
# ==============================
def _overlay_text(img: Image.Image, title: str = "", subtitle: str = "", footer: str = "", qr_text: str | None = None):
    # Note: This function is still needed for the fallback image on failure.
    draw = ImageDraw.Draw(img)
    W, H = img.size

    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    font_big = font_med = None
    for fp in candidates:
        if os.path.exists(fp):
            try:
                font_big = ImageFont.truetype(fp, 84)
                font_med = ImageFont.truetype(fp, 44)
                break
            except Exception:
                pass
    if font_big is None:
        font_big = ImageFont.load_default()
        font_med = ImageFont.load_default()

    def draw_centered(text, y, font, fill="white"):
        if not text:
            return
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (W - w) // 2
        draw.rectangle([x - 24, y - 14, x + w + 24, y + h + 14], fill=(0, 0, 0, 160))
        draw.text((x, y), text, font=font, fill=fill)

    if title:
        draw_centered(title.upper(), int(H * 0.10), font_big)
    if subtitle:
        draw_centered(subtitle, int(H * 0.22), font_med)
    if footer:
        draw_centered(footer, int(H * 0.88), font_med)

    if qr_text:
        qr = qrcode.make(qr_text).resize((220, 220))
        img.paste(qr, (W - 240, H - 260))
    return img

# ==============================
# Replicate
# ==============================
def _replicate_headers():
    if not REPLICATE_TOKEN:
        raise RuntimeError("REPLICATE_API_TOKEN missing in .env")
    return {"Authorization": f"Token {REPLICATE_TOKEN}", "Content-Type": "application/json"}

def _get_latest_version_id(owner: str, name: str) -> str:
    url = f"https://api.replicate.com/v1/models/{owner}/{name}/versions"
    r = requests.get(url, headers=_replicate_headers(), timeout=30)
    r.raise_for_status()
    data = r.json()
    versions = data.get("results") or []
    if not versions:
        raise RuntimeError("No versions found for Replicate model")
    return versions[0]["id"]

def _sd_via_replicate(prompt: str) -> Image.Image:
    version_id = _get_latest_version_id(REPLICATE_MODEL_OWNER, REPLICATE_MODEL_NAME)
    create_url = "https://api.replicate.com/v1/predictions"
    payload = {
        "version": version_id,
        "input": {"prompt": prompt, "width": 1024, "height": 1536, "num_inference_steps": 28, "guidance_scale": 7.0},
    }
    r = requests.post(create_url, headers=_replicate_headers(), json=payload, timeout=60)
    r.raise_for_status()
    pred = r.json()
    status_url = pred.get("urls", {}).get("get")
    if not status_url:
        raise RuntimeError("Prediction status URL missing")
    while True:
        pr = requests.get(status_url, headers=_replicate_headers(), timeout=60)
        pr.raise_for_status()
        data = pr.json()
        status = data.get("status")
        if status in ("succeeded", "failed", "canceled"):
            if status != "succeeded":
                raise RuntimeError(f"Replicate failed: {status} - {data.get('error')}")
            outputs = data.get("output") or []
            if not outputs:
                raise RuntimeError("Replicate returned no outputs")
            img_url = outputs[0]
            img_resp = requests.get(img_url, timeout=60)
            img_resp.raise_for_status()
            return Image.open(io.BytesIO(img_resp.content)).convert("RGB")
        time.sleep(2)

# ==============================
# Hugging Face
# ==============================
def _sd_via_hf(prompt: str) -> Image.Image:
    if not HF_TOKEN:
        raise RuntimeError("HF_API_TOKEN missing in .env")
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    payload = {"inputs": prompt}
    r = requests.post(url, headers=headers, json=payload, timeout=180)
    if r.status_code == 503:
        time.sleep(5)
        r = requests.post(url, headers=headers, json=payload, timeout=180)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")

# ==============================
# Gemini (optional)
# ==============================
def _sd_via_gemini(prompt: str) -> Image.Image:
    if not _GEMINI_READY:
        raise RuntimeError("Gemini not configured. Install google-generativeai and set GEMINI_API_KEY")
    model = genai.GenerativeModel("gemini-2.5-flash")
    result = model.generate_content([prompt], generation_config={"response_mime_type": "image/png"})
    try:
        part = result._result.response.candidates[0].content.parts[0]
        img_bytes = getattr(getattr(part, "inline_data", None), "data", None)
        if not img_bytes:
            raise RuntimeError("Gemini response did not contain inline PNG data")
        return Image.open(io.BytesIO(img_bytes)).convert("RGB")
    except Exception as e:
        raise RuntimeError(f"Failed to decode Gemini image output: {e}")

# ============================================
# OpenAI Images (DALL-E 3) - Handles URL response
# ============================================
def _sd_via_openai(prompt: str) -> Image.Image:
    """
    Uses OpenAI Images API (DALL-E 3) to create a 1024x1792 poster.
    Handles URL response (most common) and Base64 (fallback).
    """
    print(f"DEBUG (OpenAI): Attempting generation with prompt length {len(prompt)}. Prompt start: {prompt[:50]}...")

    try:
        client = _openai_client()
        resp = client.images.generate(
            model="dall-e-3",       
            prompt=prompt,          
            size="1024x1792",       # The correct portrait size for DALL-E 3
            quality="standard",     
            n=1,
            # Requesting URL format for efficiency (DALL-E 3 standard).
            response_format="url", 
        )
        
        # 1. Check for URL first (DALL-E 3 preference)
        image_source = resp.data[0].url
        
        if image_source:
            print("DEBUG (OpenAI): Received Image URL. Attempting download.")
            img_resp = requests.get(image_source, timeout=60)
            img_resp.raise_for_status() # Raise error for bad status codes
            return Image.open(io.BytesIO(img_resp.content)).convert("RGB")
        
        # 2. Fallback to Base64 if URL is missing
        b64 = resp.data[0].b64_json
        if b64:
            print("DEBUG (OpenAI): Received Base64 data. Attempting decode.")
            return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")
            
        raise RuntimeError("OpenAI returned neither a URL nor Base64 data.")

    except Exception as api_err:
        print(f"ERROR (OpenAI API): Generation failed unexpectedly. Error details: {api_err}")
        # Re-raise the error to the outer except block for fallback execution
        raise 

# ==============================
# Public API
# ==============================
def generate_poster_for_event(
    event_title: str,
    base_prompt: str = "",
    style: str = "",
    engine: str = "auto",            # auto/openai/replicate/hf/gemini
    output_path: str | None = None,
    subtitle: str = "",
    footer: str = "",
    qr_text: str | None = None,
) -> str:
    """Generate a high-quality poster, add overlays, and save."""
    if output_path is None:
        safe = event_title.replace(" ", "_").replace(":", "").replace("/", "")
        output_path = f"data/posters/{safe}.png"
    _ensure_dir(output_path)

    if engine == "auto":
        engine = _auto_engine() or "openai"

    prompt = style_prompt(event_title, base_prompt, style)

    try:
        if engine == "openai":
            img = _sd_via_openai(prompt)
        elif engine == "replicate":
            img = _sd_via_replicate(prompt)
        elif engine == "hf":
            img = _sd_via_hf(prompt)
        elif engine == "gemini":
            img = _sd_via_gemini(prompt)
        else:
            raise ValueError("Unknown engine. Use 'auto', 'openai', 'replicate', 'hf', or 'gemini'.")
    except Exception as e:
        print(f"[Poster AI] Engine failed ({engine}): {e}\nFalling back to local design.")
        # Fallback executed on failure: generate the simple dark image with error details
        img = Image.new("RGB", (1024, 1536), "#0f172a")
        # Pass the title here only on failure, not on success.
        _overlay_text(img, title=event_title, subtitle="Event Poster", footer=datetime.now().strftime("%Y-%m-%d %H:%M"))
        img.save(output_path)
        return output_path

    # === Final adjustment to remove text overlay on success ===
    # Pass empty strings to disable title/footer overlay on the generated poster.
    final = _overlay_text(img, title="", subtitle="", footer="", qr_text=qr_text) 
    # ==========================================================

    final.save(output_path)
    print(f"[Poster AI] Saved → {output_path}")
    return output_path