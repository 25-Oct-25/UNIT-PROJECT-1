# core/similarity.py
import math
import unicodedata
from rapidfuzz.distance import JaroWinkler, DamerauLevenshtein

CONFUSABLES = {
    # أرقام/حروف شائعة بالتلاعب
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t",
    # عربي ← لاتيني تقريبي
    "ا": "a", "أ": "a", "إ": "a", "آ": "a",
    "ب": "b", "ت": "t", "ث": "th", "ج": "j", "ح": "h", "خ": "kh",
    "ر": "r", "ز": "z", "س": "s", "ش": "sh", "ص": "s", "ض": "d",
    "ط": "t", "ظ": "z", "ع": "a", "غ": "gh", "ف": "f", "ق": "q",
    "ك": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h", "و": "w",
    "ي": "y", "ى": "a", "ئ": "y", "ؤ": "w", "ة": "h",
}

PHISH_HINTS = ("login","secure","verify","update","support","account","pay","bank","wallet","id","portal")

def _strip_tld(domain: str) -> str:
    # خذ آخر جزء قبل الـTLD: foo.bar.example.com.sa -> example
    parts = domain.split(".")
    if len(parts) >= 2:
        return parts[-2]
    return domain

def _normalize_token(s: str) -> str:
    if not s: return ""
    # NFKC + lowercase
    s = unicodedata.normalize("NFKC", s).lower()
    # أزل نقاط/شرطات/مسافات الشائعة
    for ch in "-_ .":
        s = s.replace(ch, "")
    # بدائل الهوموجليف
    out = []
    for ch in s:
        out.append(CONFUSABLES.get(ch, ch))
    s = "".join(out)
    # أزل أي شيء غير حرفي/رقمي بعد التطبيع
    s = "".join(c for c in s if c.isalnum())
    return s

def _char_ngrams(s: str, n=3):
    if len(s) < n:
        return [s] if s else []
    return [s[i:i+n] for i in range(len(s)-n+1)]

def _cosine_ngrams(a: str, b: str, n=3) -> float:
    A = _char_ngrams(a, n); B = _char_ngrams(b, n)
    if not A or not B: return 0.0
    fa = {}
    for g in A: fa[g] = fa.get(g,0) + 1
    fb = {}
    for g in B: fb[g] = fb.get(g,0) + 1
    # dot / (||a||*||b||)
    dot = sum(fa[g]*fb.get(g,0) for g in fa)
    na = math.sqrt(sum(v*v for v in fa.values()))
    nb = math.sqrt(sum(v*v for v in fb.values()))
    if na == 0 or nb == 0: return 0.0
    return dot/(na*nb)

def _brand_variants(brand: str):
    """بسيطة: رجّع البراند نفسه + بدون مسافة، + نسخ عربية/إنجليزية لو معروفة."""
    b = brand.lower().strip()
    out = {b, b.replace(" ", "")}
    if b in ("stc","saudi telecom","saudi telecom company","شركة الاتصالات السعودية","الاتصالات السعودية"):
        out |= {"stc","sauditelecom","الاتصالاتالسعودية","شركةالاتصالاتالسعودية","mystc"}
    if b in ("apple","apple inc","ابل","appleid"):
        out |= {"apple","appleid","ابل"}
    if "rajhi" in b or "الراجحي" in b:
        out |= {"alrajhi","rajhi","الراجحي","rajhibank","alrajhibank"}
    if "amazon" in b or "أمازون" in b:
        out |= {"amazon","amazonpay","أمازون"}
    return list(out)

def calculate_similarity(domain_token: str, brand_name: str) -> float:
    """
    ترجع درجة 0..1 تجمع مقاييس متعددة + bonus للكلمات الدالّة.
    استبدل استدعاء مشروعك لهذه الدالة مباشرة.
    """
    sld = _normalize_token(_strip_tld(domain_token))
    best = 0.0

    # bonus لو كلمات تصيّد ظهرت بجانب البراند (يطبق لاحقاً)
    has_hint = any(h in domain_token.lower() for h in PHISH_HINTS)

    for b in _brand_variants(brand_name):
        bb = _normalize_token(b)
        if not sld or not bb: 
            continue

        # مقاييس أساسية
        jw  = JaroWinkler.normalized_similarity(sld, bb)             # 0..1
        dl  = 1.0 - min(1.0, DamerauLevenshtein.normalized_distance(sld, bb))
        cos = _cosine_ngrams(sld, bb, n=3)

        # نسبة LCS التقريبية: طول المشترك/طول البراند
        # (تقريب خفيف: اعتبر jw بديل جيد لـ LCS في الأداء)
        lcs_like = jw

        # مكافآت بسيطة
        bonus = 0.0
        # البراند كبادئة/لاحقة بعد التطبيع
        if sld.startswith(bb) or sld.endswith(bb):
            bonus += 0.06
        # وجود كلمات تصيّد مع البراند في نفس الـtoken
        if has_hint:
            bonus += 0.05

        # دمج موزون
        score = 0.35*jw + 0.25*dl + 0.25*cos + 0.15*lcs_like + bonus
        score = max(0.0, min(1.0, score))
        best = max(best, score)

    return best
