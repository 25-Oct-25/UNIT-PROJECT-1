# report_generator.py
from fpdf import FPDF
import datetime

class PDF(FPDF):
    def header(self):
        # Set font for header
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Car Importer Toolkit - AI Analysis Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        # Set font for footer
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        page_num = self.page_no()
        self.cell(0, 10, f'Page {page_num}', 0, 0, 'C')

def save_ai_report_to_pdf(car, cost, ai_advice, filename):
    try:
        pdf = PDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        #Main Title
        pdf.set_font('Times', 'B', 18)
        pdf.cell(0, 10, 'AI Deal Analysis Report', 0, 1, 'C')
        pdf.ln(5)
        
        #Report Date
        pdf.set_font('Times', '', 10)
        today = datetime.date.today().strftime("%Y-%m-%d")
        pdf.cell(0, 5, f'Report Date: {today}', 0, 1, 'R')
        pdf.ln(10)

        #Car Details
        pdf.set_font('Times', 'B', 14)
        pdf.cell(0, 10, '1. Subject Vehicle:', 0, 1, 'L')
        pdf.set_font('Times', '', 12)
        pdf.cell(0, 8, f"   - Make & Model: {car.year} {car.make} {car.model}", 0, 1, 'L')
        pdf.cell(0, 8, f"   - Origin Country: {car.origin_country}", 0, 1, 'L')
        pdf.cell(0, 8, f"   - Base Price (USD): ${car.price_usd:,.2f}", 0, 1, 'L')
        pdf.ln(5)

        #Cost Details
        pdf.set_font('Times', 'B', 14)
        pdf.cell(0, 10, '2. Cost Analysis:', 0, 1, 'L')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(0, 8, f"   - Total Estimated Cost (SAR): {cost['total_cost']:,.2f} SAR", 0, 1, 'L')
        pdf.ln(10)

        #AI Analysis
        pdf.set_font('Times', 'B', 14)
        pdf.cell(0, 10, '3. AI Advisor Verdict:', 0, 1, 'L')
        pdf.set_font('Times', '', 12)
        

        pdf.multi_cell(0, 8, ai_advice, 0, 'L')
        pdf.ln(10)
        
        #Save the file
        pdf.output(filename)
        print(f"\n✅ PDF Report saved successfully as: {filename}")
        
    except Exception as e:
        print(f"\n❌ Error creating PDF: {e}")