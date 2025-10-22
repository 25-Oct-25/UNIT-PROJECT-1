from fpdf import FPDF
import datetime
from rich.console import Console
from rich.table import Table
import os

script_dir = os.path.dirname(__file__)
PDF_DIR = os.path.join(script_dir, "pdf-files")

if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

class PDF(FPDF):
    def header(self):
        """
        Sets the header for the PDF file.
        """
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Car Importer Toolkit - AI Analysis Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        """
        Sets the footer for the PDF file.
        """
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        page_num = self.page_no()
        self.cell(0, 10, f'Page {page_num}', 0, 0, 'C')

def save_ai_report_to_pdf(car, cost, ai_advice, base_filename):
    """
    Creates the PDF file and save it into 'pdf-files' folder.
    """
    try:
        pdf = PDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        pdf.set_font('Times', 'B', 18)
        pdf.cell(0, 10, 'AI Deal Analysis Report', 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_font('Times', '', 10)
        today = datetime.date.today().strftime("%Y-%m-%d")
        pdf.cell(0, 5, f'Report Date: {today}', 0, 1, 'R')
        pdf.ln(10)

        pdf.set_font('Times', 'B', 14)
        pdf.cell(0, 10, '1. Subject Vehicle:', 0, 1, 'L')
        pdf.set_font('Times', '', 12)
        pdf.cell(0, 8, f"   - Make & Model: {car.year} {car.make} {car.model}", 0, 1, 'L')
        pdf.cell(0, 8, f"   - Origin Country: {car.origin_country}", 0, 1, 'L')
        pdf.cell(0, 8, f"   - Base Price (USD): ${car.price_usd:,.2f}", 0, 1, 'L')
        pdf.ln(5)

        pdf.set_font('Times', 'B', 14)
        pdf.cell(0, 10, '2. Cost Analysis:', 0, 1, 'L')
        pdf.set_font('Times', 'B', 12)
        pdf.cell(0, 8, f"   - Total Estimated Cost (SAR): {cost['total_cost']:,.2f} SAR", 0, 1, 'L')
        pdf.ln(10)

        pdf.set_font('Times', 'B', 14)
        pdf.cell(0, 10, '3. AI Advisor Verdict:', 0, 1, 'L')
        pdf.set_font('Times', '', 12)
        
        pdf.multi_cell(0, 8, ai_advice, 0, 'L')
        pdf.ln(10)
        
        full_path = os.path.join(PDF_DIR, base_filename)
        pdf.output(full_path)
        
        print(f"\n✅ PDF Report saved successfully in: {full_path}")
        
    except Exception as e:
        print(f"\n❌ Error creating PDF: {e}")

def print_business_dashboard (total_cars_sold, total_revenue, total_stock_value):
    """
    Prints the businesss dashboard in a table (cars sold, revenue and stock value)
    """
    console = Console()
    table = Table(title="Dashboard", style="bold green")

    table.add_column("Attribute", style="bold white")
    table.add_column("Value", style="white")
    
    table.add_row("Cars sold", f"[magenta]{total_cars_sold}[/magenta]")
    table.add_row("Revenue", f"[magenta]${total_revenue}[/magenta]")
    table.add_row("Stock value", f"[magenta]${total_stock_value}[/magenta]")

    console.print(table)