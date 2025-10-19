from fpdf import FPDF
import datetime, os
from ..core.models import AppState
from ..nutrition.calculator import bmr_mifflin_st_jeor, tdee, macro_targets

def _brand(state: AppState):
    brand = state.settings.get("brand", {}) if getattr(state, "settings", None) else {}
    color = brand.get("color", "#0A84FF"); title = brand.get("title", "FitCoach — Weekly Report")
    logo = brand.get("logo", "")
    color = color.lstrip("#"); r, g, b = int(color[0:2],16), int(color[2:4],16), int(color[4:6],16)
    return (r,g,b), title, logo

class ReportPDF(FPDF):
    def __init__(self, *a, **kw):
        self.brand_rgb = (10,132,255); self.brand_title = "FitCoach — Weekly Report"; self.brand_logo = ""
        super().__init__(*a, **kw)
    def header(self):
        self.set_fill_color(*self.brand_rgb); self.rect(0,0,self.w,18,"F")
        if self.brand_logo and os.path.exists(self.brand_logo):
            try: self.image(self.brand_logo, x=self.l_margin, y=3, h=12)
            except Exception: pass
        self.set_text_color(255,255,255); self.set_font("Helvetica","B",14); self.set_y(5)
        self.cell(0,8,self.brand_title,align="C"); self.ln(12); self.set_text_color(0,0,0)
    def section_title(self, title: str):
        self.set_font("Helvetica","B",12); self.set_text_color(*self.brand_rgb)
        self.cell(0,8,title,new_x="LMARGIN", new_y="NEXT"); self.set_text_color(0,0,0)
    def kv(self, k: str, v: str):
        self.set_font("Helvetica","",11); self.cell(50,6,k+":",align="L"); self.cell(0,6,v,new_x="LMARGIN", new_y="NEXT")
    def bullet(self, text: str):
        self.set_font("Helvetica","",11); self.cell(5,6,u"•"); self.multi_cell(0,6,text)

def _week_range(days:int=7):
    end = datetime.date.today(); start = end - datetime.timedelta(days=days-1); return start, end

def _table(pdf: FPDF, headers, rows, col_w=None):
    pdf.set_font("Helvetica","B",10); col_w = col_w or [pdf.w/len(headers)-20]*len(headers)
    for h,w in zip(headers,col_w): pdf.cell(w,7,h,border=1,align="C")
    pdf.ln(7); pdf.set_font("Helvetica","",9)
    for r in rows:
        for cell,w in zip(r,col_w): pdf.cell(w,6,str(cell),border=1)
        pdf.ln(6)

def build_weekly_pdf(state: AppState, out_file: str, days: int = 7) -> str:
    start, end = _week_range(days); p = state.profile
    brand_rgb, brand_title, brand_logo = _brand(state)
    pdf = ReportPDF(orientation="P", unit="mm", format="A4")
    pdf.brand_rgb, pdf.brand_title, pdf.brand_logo = brand_rgb, brand_title, brand_logo
    pdf.set_auto_page_break(auto=True, margin=12); pdf.add_page()

    pdf.section_title("Summary")
    pdf.kv("Date Range", f"{start.isoformat()} to {end.isoformat()}")
    pdf.kv("Goal", p.goal); pdf.kv("Activity", p.activity)
    pdf.kv("Height/Weight", f"{p.height_cm:.0f} cm / {p.weight_kg:.1f} kg"); pdf.ln(2)

    pdf.section_title("Calories & Macros")
    b = bmr_mifflin_st_jeor(p.sex,p.weight_kg,p.height_cm,p.age); t = tdee(b,p.activity)
    target = t - 400 if p.goal=="cut" else t + 250 if p.goal=="bulk" else t
    prot, carbs, fat = macro_targets(p.goal,p.weight_kg,target)
    pdf.kv("BMR", f"{b:.0f} kcal"); pdf.kv("TDEE", f"{t:.0f} kcal")
    pdf.kv("Target kcal", f"{target:.0f} kcal")
    pdf.kv("Macros", f"Protein {prot} g | Carbs {carbs} g | Fat {fat} g"); pdf.ln(2)

    pdf.section_title("Training Plan")
    if state.plan:
        headers = ["Day","Focus","Exercises (name x sets)"]; rows=[]
        for wk in state.plan.workouts:
            exs = "; ".join([f"{ex['name']} ({ex['sets']})" for ex in wk.Exercises[:6]])
            rows.append([wk.Day, wk.Focus, exs])
        _table(pdf, headers, rows, col_w=[25,30,125])
    else:
        pdf.bullet("No plan yet. Use: plan generate --split=upper-lower --days=4")

    pdf.section_title("Progress (Weight)")
    if state.progress:
        entries = state.progress[-days:]
        headers, rows = ["Date","Weight (kg)"], [[e["date"], f"{e['weight']}"] for e in entries]
        _table(pdf, headers, rows, col_w=[40,30])
        diff = float(entries[-1]["weight"]) - float(entries[0]["weight"])
        pdf.kv("Trend", f"{diff:+.2f} kg in {len(entries)} entries")
    else:
        pdf.bullet("No weight entries yet. Log with: progress log --weight=...")

    pdf.section_title("Habits")
    if state.habits_log:
        logs = state.habits_log[-days:]
        avg_water = sum(float(d.get("water",0)) for d in logs)/len(logs)
        avg_sleep = sum(float(d.get("sleep",0)) for d in logs)/len(logs)
        avg_steps = sum(int(d.get("steps",0)) for d in logs)/len(logs)
        pdf.kv("Avg Water", f"{avg_water:.1f} L/day")
        pdf.kv("Avg Sleep", f"{avg_sleep:.1f} h/day")
        pdf.kv("Avg Steps", f"{avg_steps:.0f} /day")
    else:
        pdf.bullet("No habits logged. Use: habits log --water=3 --sleep=7.5 --steps=9000")

    from ..advice.recommend import daily_tips
    pdf.section_title("Coach Advice")
    for tip in daily_tips(p)[:6]: pdf.bullet(tip)

    pdf.ln(3); pdf.set_font("Helvetica","I",9); pdf.cell(0,6,"Generated by FitCoach CLI",align="R")
    pdf.output(out_file); return out_file
