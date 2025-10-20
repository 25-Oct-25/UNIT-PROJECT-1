# modules/ai_poster.py
import os, json, requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL   = "gemini-2.5-flash"

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL}:generateContent?key={API_KEY}"
HEADERS = {"Content-Type": "application/json"}

def _ai_suggest_design(prompt: str) -> dict:
    """Ask Gemini for title/subtitle and colors. Returns a dict."""
    instruction = f"""
You are a creative poster designer. Given a theme/prompt, respond in **valid JSON only**
with: title (<=6 words), subtitle (<=16 words), bg_color (HEX), fg_color (HEX).

Rules:
- Prefer high contrast between bg_color and fg_color
- Keep it minimal, modern, bold
- JSON keys: title, subtitle, bg_color, fg_color
Prompt: {prompt}
Return JSON only.
"""
    payload = {"contents": [{"parts": [{"text": instruction}]}]}
    r = requests.post(URL, headers=HEADERS, data=json.dumps(payload))
    if r.status_code != 200:
        raise RuntimeError(f"Gemini design error {r.status_code}: {r.text}")
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

    # نظّف أي كود بلوك إن وُجد
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[-1]
        if text.startswith("json"):
            text = text[4:]
    data = json.loads(text)
    # قيم افتراضية آمنة
    return {
        "title": data.get("title", "Inspire"),
        "subtitle": data.get("subtitle", "Make it happen."),
        "bg_color": data.get("bg_color", "#111827"),
        "fg_color": data.get("fg_color", "#F9FAFB"),
    }

def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """Try common fonts; fallback to default bitmap font."""
    # جرّب خطوط ويندوز المعروفة إن توفرت
    for path in [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except:
                pass
    return ImageFont.load_default()

def generate_poster(prompt: str, output_path: str) -> str:
    """
    Generate a simple poster PNG using Gemini suggestions + PIL.
    Returns the saved output_path.
    """
    try:
        design = _ai_suggest_design(prompt)
    except Exception as e:
        # فشل AI؟ نكمل بلا اقتراحات
        design = {
            "title": prompt[:20] or "Poster",
            "subtitle": "Generated locally",
            "bg_color": "#222222",
            "fg_color": "#FFFFFF",
        }

    bg = design["bg_color"]
    fg = design["fg_color"]
    title = design["title"]
    subtitle = design["subtitle"]

    W, H = 1024, 1280  # بوستر رأسي
    img = Image.new("RGB", (W, H), color=bg)
    d = ImageDraw.Draw(img)

    # خطوط
    title_font = _get_font(90)
    sub_font   = _get_font(38)

    # حساب تمركز النص
    title_w, title_h = d.textbbox((0,0), title, font=title_font)[2:]
    sub_w, sub_h     = d.textbbox((0,0), subtitle, font=sub_font)[2:]

    # مارجن علوي
    y = H//3 - title_h//2
    x_title = (W - title_w)//2
    x_sub   = (W - sub_w)//2

    # ظل خفيف للنص (جمالية)
    shadow = (0, 0, 0)
    d.text((x_title+2, y+2), title, font=title_font, fill=shadow)
    d.text((x_title, y), title, font=title_font, fill=fg)

    y2 = y + title_h + 40
    d.text((x_sub+1, y2+1), subtitle, font=sub_font, fill=shadow)
    d.text((x_sub, y2), subtitle, font=sub_font, fill=fg)

    # فوتر بسيط
    footer = "UNIT PROJECT • Generated with Gemini"
    fw, fh = d.textbbox((0,0), footer, font=_get_font(22))[2:]
    d.text(((W-fw)//2, H-80), footer, font=_get_font(22), fill=fg)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path)
    return output_path
