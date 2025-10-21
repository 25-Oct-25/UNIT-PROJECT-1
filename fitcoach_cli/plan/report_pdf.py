# Path: fitcoach_cli/plan/report_pdf.py
from __future__ import annotations

from pathlib import Path
import datetime, os
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

# مسار مجلد المشروع ثم الخطوط
ROOT_DIR = Path(__file__).resolve().parents[2]
FONT_DIR = ROOT_DIR / "assets" / "fonts"
FONT_REG = FONT_DIR / "NotoSansArabic-Regular.ttf"
FONT_BOLD = FONT_DIR / "NotoSansArabic-Bold.ttf"

def shape_ar(text: str) -> str:
    """
    يهيّئ العربية (ligatures) ويعكس الاتجاه (RTL) حتى تظهر صحيحة في PDF.
    مرّر النص العربي عبرها قبل الكتابة.
    نصوص إنجليزية/أرقام ما تحتاج هذا عادة.
    """
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def _ascii_sanitize(s: str) -> str:
    """استبدال رموز Unicode الشائعة بنسخ ASCII (حل احتياطي للعنوانين فقط)."""
    if not s: return s
    repl = {"—": "-", "–": "-", "…": "...", "“": '"', "”": '"', "’": "'", "‘": "'"}
    for k, v in repl.items():
        s = s.replace(k, v)
    return s

class ReportPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحميل الخطوط اليونيكود مرة واحدة
        # uni=True ضروري لدعم Unicode
        self.add_font("NotoArabic", "", str(FONT_REG), uni=True)
        self.add_font("NotoArabic", "B", str(FONT_BOLD), uni=True)
        self.set_auto_page_break(auto=True, margin=12)

    def header(self):
        self.set_font("NotoArabic", "B", 16)
        # استخدم عنوان ASCII-safe لتجنّب مشاكل لو نسيت الخط
        title = _ascii_sanitize("FitCoach — Weekly Report")
        # لو تبي عربي:
        # title = shape_ar("تقرير FitCoach الأسبوعي")
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("NotoArabic", "", 11)
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("NotoArabic", "", 9)
        txt = f"Page {self.page_no()} / {{nb}}"
        self.cell(0, 10, txt, align="C")

def build_weekly_pdf(state, file_path: str, days: int = 7) -> None:
    """
    يبني تقرير أسبوعي إلى PDF.
    state: كائن الحالة العام (نفس الذي تستخدمه في بقية المشروع).
    file_path: مسار ملف الإخراج.
    days: كم يوم يشمل التقرير (افتراضي 7).
    """
    # إشارة اختيارية: لو حاب تفرض ASCII فقط من المجدول
    ascii_only = os.environ.get("FITCOACH_PDF_ASCII_FALLBACK") == "1"

    pdf = ReportPDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("NotoArabic", "", 12)

    # مثال: عنوان/ملخص عربي
    summary_title = "ملخص الأسبوع"
    summary_body  = "هذا تقرير موجز لنشاطك خلال الأيام الماضية."

    if ascii_only:
        # إن احتجت إجبار ASCII لأي سبب
        summary_title = _ascii_sanitize(summary_title)
        summary_body  = _ascii_sanitize(summary_body)
        writer_title  = summary_title
        writer_body   = summary_body
    else:
        writer_title  = shape_ar(summary_title)
        writer_body   = shape_ar(summary_body)

    # عنوان القسم
    pdf.set_font("NotoArabic", "B", 14)
    pdf.cell(0, 8, writer_title, ln=1, align="R")  # R للاتجاه من اليمين
    pdf.set_font("NotoArabic", "", 12)
    pdf.multi_cell(0, 7, writer_body, align="R")
    pdf.ln(2)

    # أمثلة بيانات (استبدلها ببياناتك الفعلية من state)
    today = datetime.date.today()
    period = f"{(today - datetime.timedelta(days=days-1)).isoformat()} → {today.isoformat()}"
    pdf.set_font("NotoArabic", "B", 12)
    pdf.cell(0, 7, _ascii_sanitize(f"Period: {period}"), ln=1)

    # مثال جدول بسيط
    pdf.set_font("NotoArabic", "", 11)
    rows = [
        ("Weight trend", "−0.4 kg"),   # لاحظ الإشارة السالبة؛ مدعومة في Unicode
        ("Workouts", "4 sessions"),
        ("Best lift", "Bench 80×8 @ RPE 8"),
    ]
    for k, v in rows:
        pdf.cell(60, 7, _ascii_sanitize(k))
        pdf.cell(0, 7, _ascii_sanitize(v), ln=1)

    # في نهاية الوثيقة
    out_path = Path(file_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
