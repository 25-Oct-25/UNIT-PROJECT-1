from fpdf import FPDF
import datetime

class GeneratePDF:
    def __init__(self):
        pass

    def create_pdf(self, content, filename="qa_output.pdf", title="Generated Report"):
        """
        Creates a formatted PDF file from the given content.
        The title can be customized (e.g., 'Video Summary', 'Arabic Translation', etc.)
        """
        pdf = FPDF()
        pdf.add_page()

        # Title Section
        pdf.set_font("Arial", style='B', size=16)
        pdf.cell(0, 10, title, ln=True, align="C")

        # Date
        pdf.set_font("Arial", size=12)
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pdf.ln(5)

        # Content
        for line in content.split("\n"):
            pdf.multi_cell(0, 10, line)

        pdf.output(filename)
        return filename
