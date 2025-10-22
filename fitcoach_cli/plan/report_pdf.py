# Path: fitcoach_cli/plan/report_pdf.py
from __future__ import annotations

from pathlib import Path
import datetime
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

# ===== مسارات الخطوط =====
ROOT_DIR = Path(__file__).resolve().parents[2]
FONT_DIR = ROOT_DIR / "assets" / "fonts"

# العربي (موجود عندك)
FONT_AR_REG  = FONT_DIR / "NotoSansArabic-Regular.ttf"
FONT_AR_BOLD = FONT_DIR / "NotoSansArabic-Bold.ttf"

# اللاتيني (ويندوز) — لا يحتاج تنزيل
WIN_FONTS = Path(r"C:\Windows\Fonts")
FONT_LAT_REG  = WIN_FONTS / "arial.ttf"
FONT_LAT_BOLD = WIN_FONTS / "arialbd.ttf"

# علامات اتجاه عند خلط RTL/LTR
LRE, PDF_ = "\u202A", "\u202C"   # فرض LTR داخل سطر عربي

def ar(text: str) -> str:
    """تهيئة العربية: وصل الحروف + اتجاه RTL."""
    if not text:
        return ""
    return get_display(arabic_reshaper.reshape(text))

def ltr(s: str) -> str:
    """يفرض اتجاه LTR لقطعة لاتينية/تواريخ داخل سطر عربي."""
    return f"{LRE}{s}{PDF_}"

def gray(pdf: FPDF, val: int):
    pdf.set_text_color(val, val, val)

def black(pdf: FPDF):
    pdf.set_text_color(0, 0, 0)

class ReportPDF(FPDF):
    """
    خطّان:
      - ArabicWin  -> NotoSansArabic (العربي)
      - LatinWin   -> Arial (اللاتيني/التواريخ/الرموز)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # تسجيل الخطوط
        self.add_font("ArabicWin", "",  str(FONT_AR_REG),  uni=True)
        self.add_font("ArabicWin", "B", str(FONT_AR_BOLD), uni=True)
        self.add_font("LatinWin",  "",  str(FONT_LAT_REG),  uni=True)
        self.add_font("LatinWin",  "B", str(FONT_LAT_BOLD), uni=True)

        # هوامش وترويس
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(left=18, top=18, right=18)

    # ——— ترويسة وتذييل ———
    def header(self):
        # عنوان لاتيني في الوسط
        self.set_y(16)
        self.set_draw_color(220, 220, 220)
        self.set_line_width(0.2)

        self.set_font("LatinWin", "B", 20)
        black(self)
        self.cell(0, 10, "FitCoach - Weekly Report", align="C", new_x="LMARGIN", new_y="NEXT")

        # خط فاصل رفيع
        y = self.get_y() + 2
        self.line(18, y, self.w - 18, y)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("LatinWin", "", 9)
        gray(self, 120)
        today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cell(0, 8, f"Generated: {today}   •   Page {self.page_no()} / {{nb}}",
                  align="C")
        black(self)

    # ——— أدوات طباعة ———
    def font_ar(self, size=12, bold=False):
        self.set_font("ArabicWin", "B" if bold else "", size)

    def font_lat(self, size=12, bold=False):
        self.set_font("LatinWin", "B" if bold else "", size)

    def kv_row(self, label: str, value: str, w_label=45, h=8):
        """صف ثنائي الأعمدة (لاتيني)."""
        self.font_lat(11, False)
        gray(self, 40)
        self.cell(w_label, h, label)
        black(self)
        self.font_lat(11, False)
        self.cell(0, h, value, ln=1)

def build_weekly_pdf(state, file_path: str, days: int = 7) -> None:
    pdf = ReportPDF(orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.add_page()

    # ——— عنوان قسم عربي يمين ———
    pdf.font_ar(16, True)
    pdf.cell(0, 10, ar("ملخص الأسبوع"), ln=1, align="R")

    # وصف عربي
    pdf.font_ar(12, False)
    gray(pdf, 60)
    pdf.multi_cell(0, 7, ar("هذا تقرير موجز لنشاطك خلال الأيام الماضية."), align="R")
    black(pdf)
    pdf.ln(2)

    # ——— فترة التقرير (لاتيني) ———
    today = datetime.date.today()
    start = today - datetime.timedelta(days=days - 1)
    period = f"{start.isoformat()} → {today.isoformat()}"

    pdf.font_lat(12, True)
    pdf.cell(0, 8, f"Period: {ltr(period)}", ln=1)
    pdf.ln(2)

    # ——— جدول بيانات ———
    rows = [
        ("Weight trend", "-0.4 kg"),
        ("Workouts", "4 sessions"),
        ("Best lift", "Bench 80×8 @ RPE 8"),
    ]
    for k, v in rows:
        pdf.kv_row(k, v)

    # ——— حفظ الملف ———
    out = Path(file_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out))
