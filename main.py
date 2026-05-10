from dotenv import load_dotenv
load_dotenv()

from fpdf import FPDF
from tools import read_code_file
from crew import code_analysis_crew

code = read_code_file("data/input/sar.py")

result = code_analysis_crew.kickoff(
    inputs={"code": code}
)

pdf = FPDF()
pdf.add_page()
pdf.add_font("Arial", fname="C:/Windows/Fonts/arial.ttf")
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 6, str(result))
pdf.output("outputs/reports/report.pdf")