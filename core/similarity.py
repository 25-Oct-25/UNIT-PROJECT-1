import re
from rapidfuzz import fuzz

_GENERIC_WORDS = {"bank", "company", "co", "group", "inc", "ltd", "corp", "sa", "ksa"}
_NEUTRAL_SEGMENTS = {"example", "test", "demo", "sample", "sandbox"}  # تقلل الإيجابيات الكاذبة

def _brand_core(brand: str) -> str:
    words = [w for w in re.split(r"\s+", brand.lower()) if w]
    words = [w for w in words if w not in _GENERIC_WORDS]
    core = re.sub(r"[^a-z0-9]+", "", "".join(words))
    return core

def _canon(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())

def calculate_similarity(domain_token: str, brand: str) -> float:
    """
    درجة تشابه 0..1 مع:
      - وعي بالمقاطع (segment-aware)
      - Boost ديناميكي محسوب
      - تخفيض عند وجود مقاطع محايدة مثل 'example'
    """
    d = domain_token.lower()
    b = brand.lower()

    s_partial = fuzz.partial_ratio(d, b)
    s_tokens  = fuzz.token_set_ratio(d, b)
    s_ratio   = fuzz.ratio(d, b)
    base = max(s_partial, s_tokens, s_ratio) / 100.0  # 0..1

    brand_core = _brand_core(brand)         # مثال: "AlRajhi Bank" -> "alrajhi"
    dom_core   = _canon(domain_token)       # "alrajhi-login" -> "alrajhilogin"

    segments = [seg for seg in re.split(r"[-_]+", d) if seg]

    if any(seg in _NEUTRAL_SEGMENTS for seg in segments):
        base *= 0.85  # تقليل 15%

    exact_core_match = (brand_core != "" and dom_core == brand_core)
    seg_exact = brand_core in segments                     # مطابق لمقطع كامل
    seg_sub   = any(brand_core in seg for seg in segments) # بداخل مقطع أكبر

    length_boost = min(len(brand_core) / 100.0, 0.10) if brand_core else 0.0  # 0..0.10
    if seg_exact:
        boost = length_boost
    elif seg_sub:
        boost = length_boost * 0.4  # أضعف بكثير لو داخل مقطع أكبر
    else:
        boost = 0.0

    if len(brand_core) <= 3 and not exact_core_match:
        base *= 0.9
        boost *= 0.5

    score = base + boost

    if not exact_core_match:
        score = min(score, 0.95)
    else:
        score = min(score, 1.0)

    return round(score, 2)
