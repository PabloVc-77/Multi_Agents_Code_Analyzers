def read_code_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()
    
def save_report(content, path="outputs/report.md"):
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)

from crewai.tools import tool
from fpdf import FPDF
import re
import os

def _limpiar_markdown(texto: str) -> str:
    """Elimina sintaxis markdown para texto plano en el PDF."""
    texto = re.sub(r'#{1,6}\s*', '', texto)       # headers
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto) # negrita
    texto = re.sub(r'\*(.*?)\*', r'\1', texto)      # cursiva
    texto = re.sub(r'`{1,3}.*?`{1,3}', '', texto)  # código
    texto = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', texto)  # links
    return texto

@tool("Generador de PDF")
def generar_pdf(md_path: str) -> str:
    """
    Convierte un archivo Markdown a PDF.
    Recibe la ruta del archivo .md y genera un .pdf en la misma carpeta.
    Devuelve la ruta del PDF generado.
    """
    if not os.path.exists(md_path):
        return f"Error: no se encontró el archivo {md_path}"

    pdf_path = md_path.replace(".md", ".pdf")

    with open(md_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    for linea in contenido.split("\n"):
        linea_limpia = _limpiar_markdown(linea).strip()
        if not linea_limpia:
            pdf.ln(3)
            continue

        # Títulos
        if linea.startswith("# "):
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(44, 62, 80)
            pdf.multi_cell(0, 10, linea_limpia)
            pdf.ln(2)
        elif linea.startswith("## "):
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(52, 73, 94)
            pdf.multi_cell(0, 8, linea_limpia)
            pdf.ln(1)
        elif linea.startswith("### "):
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 7, linea_limpia)
        # Listas
        elif linea.strip().startswith("- ") or linea.strip().startswith("* "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, f"  • {linea_limpia[2:]}")
        # Texto normal
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, linea_limpia)

    pdf.output(pdf_path)
    return f"PDF generado correctamente en: {pdf_path}"