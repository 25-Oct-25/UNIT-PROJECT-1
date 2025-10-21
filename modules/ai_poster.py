# modules/ai_poster.py
import os, io, time, requests
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
import qrcode

# ===== Gemini (اختياري) =====
try:
    import google.generativeai as genai
    _GENAI_AVAILABLE = True
except Exception:
    _GENAI_AVAILABLE = False

load_dotenv()

# ===== مفاتيح من .env =====
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN", "").strip()
HF_TOKEN        = os.getenv("HF_API_TOKEN", "").strip()
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "").strip()

# ===== إعدادات الموديلات =====
# أفضل جودة حالياً للبوسترات (FLUX 1.1 Pro على Replicate)
REPLICATE_MODEL_OWNER = "black-forest-labs"
REPLICATE_MODEL_NAME  = "flux-1.1-pro"

# خيار بديل واقعي:
# REPLICATE_MODEL_OWNER = "replicate"
# REPLICATE_MODEL_NAME  = "realistic-vision-v5"

HF_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"

# تهيئة Gemini (إن وُجد)
if _GENAI_AVAILABLE and GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        _GEMINI_READY = True
    except Exception:
        _GEMINI_READY = False
else:
    _GEMINI_READY = False


# ==============================
# Utilities
# ==============================
def _ensure_dir(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def _auto_engine():
    """اختيار المحرك تلقائياً: Replicate ثم HF ثم Gemini."""
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
        "eid": ("elegant eid poster, emerald green & matte gold, glowing lanterns, crescent moon, "
                "subtle islamic geometry pattern, premium serif typography, cinematic rim light"),
        "graduation": ("premium graduation poster, black & gold, mortarboard, depth of field, "
                       "elegant serif typography, dramatic studio lighting"),
        "birthday": ("luxury birthday party poster, deep navy background with soft vignette, "
                     "glossy balloons and confetti, center composition for bold title, 3D lighting, bokeh sparks"),
        "meeting": ("minimal corporate poster, blue/gray palette, clean grid, professional sans-serif typography, "
                    "high-contrast modern look"),
        "generic": ("high-end event poster, tasteful palette, professional typography, cinematic lighting")
    }
    if any(k in t for k in ["eid", "عيد", "ramadan", "رمضان"]):
        preset = style_map["eid"]
    elif any(k in t for k in ["grad", "graduation", "تخرج"]):
        preset = style_map["graduation"]
    elif any(k in t for k in ["birth", "ميلاد", "party", "حفلة"]):
        preset = style_map["birthday"]
    elif any(k in t for k in ["meeting", "اجتماع", "workshop", "training", "conference"]):
        preset = style_map["meeting"]
    else:
        preset = style_map["generic"]

    final = f"{preset}. {base_prompt}".strip().rstrip(".")
    if style:
        final += f". {style}"
    final += ". poster layout, centered composition, award-winning design, 4k, ultra-detailed"
    return final


# ==============================
# Drawing overlay (title/subtitle/footer/QR)
# ==============================
def _overlay_text(img: Image.Image, title: str = "", subtitle: str = "", footer: str = "", qr_text: str | None = None):
    draw = ImageDraw.Draw(img)
    W, H = img.size

    # ابحث عن خط متوفر (ويندوز/ماك/لينكس)
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
        # خلفية نصف شفافة لزيادة وضوح النص
        draw.rectangle([x - 24, y - 14, x + w + 24, y + h + 14], fill=(0, 0, 0, 160))
        draw.text((x, y), text, font=font, fill=fill)

    if title:
        draw_centered(title.upper(), int(H * 0.10), font_big)
    if subtitle:
        draw_centered(subtitle, int(H * 0.22), font_med)
    if footer:
        draw_centered(footer, int(H * 0.88), font_med)

    if qr_text:
        qr = qrcode.make(qr_text)
        qr = qr.resize((220, 220))
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
        "input": {
            "prompt": prompt,
            "width": 1024, "height": 1536,           # أبعاد بوستر عمودية
            "num_inference_steps": 28,
            "guidance_scale": 7.0
        }
    }
    r = requests.post(create_url, headers=_replicate_headers(), json=payload, timeout=60)
    r.raise_for_status()
    pred = r.json()
    status_url = pred.get("urls", {}).get("get")
    if not status_url:
        raise RuntimeError("Prediction status URL missing")

    # Polling
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
# Gemini (اختياري – قد لا يكون ثابت لإرجاع صور inline)
# ==============================
def _sd_via_gemini(prompt: str) -> Image.Image:
    if not _GEMINI_READY:
        raise RuntimeError("Gemini not configured. Install google-generativeai and set GEMINI_API_KEY")
    # قد تختلف طريقة الإرجاع حسب النسخة والمنطقة؛ هذا الفرع يعمل إذا رجع PNG inline
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


# ==============================
# Public API
# ==============================
def generate_poster_for_event(
    event_title: str,
    base_prompt: str = "",
    style: str = "",
    engine: str = "auto",           # auto/replicate/hf/gemini
    output_path: str | None = None,
    subtitle: str = "",
    footer: str = "",
    qr_text: str | None = None
) -> str:
    """يولّد بوستر عالي الجودة ويضيف Overlay وعناصر اختيارية."""
    if output_path is None:
        safe = event_title.replace(" ", "_")
        output_path = f"data/posters/{safe}.png"
    _ensure_dir(output_path)

    if engine == "auto":
        engine = _auto_engine() or "replicate"

    prompt = style_prompt(event_title, base_prompt, style)

    try:
        if engine == "replicate":
            img = _sd_via_replicate(prompt)
            footer_text = footer or "Powered by Replicate · FLUX"
        elif engine == "hf":
            img = _sd_via_hf(prompt)
            footer_text = footer or "Powered by Hugging Face · SDXL"
        elif engine == "gemini":
            img = _sd_via_gemini(prompt)
            footer_text = footer or "Powered by Gemini"
        else:
            raise ValueError("Unknown engine. Use 'auto', 'replicate', 'hf', or 'gemini'.")
    except Exception as e:
        print(f"[Poster AI] Engine failed ({engine}): {e}\nFalling back to local design.")
        img = Image.new("RGB", (1024, 1536), "#0f172a")
        _overlay_text(img, title=event_title, subtitle="Event Poster", footer=datetime.now().strftime("%Y-%m-%d %H:%M"))
        img.save(output_path)
        return output_path

    # Overlay
    final = _overlay_text(img, title=event_title, subtitle=subtitle, footer=footer_text, qr_text=qr_text)
    final.save(output_path)
    print(f"[Poster AI] Saved → {output_path}")
    return output_path
