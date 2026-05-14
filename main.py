import os
from dotenv import load_dotenv
from fpdf import FPDF
from tools import read_code_file
from crew import CodeAnalysisCrew  # Importamos la clase, no la instancia

# 1. Cargar variables de entorno (API Keys, etc.)
load_dotenv()

def run_analysis():
    # 2. Leer el código fuente que queremos analizar
    try:
        code_to_analyze = read_code_file("data/input/sar.py")
    except FileNotFoundError:
        print("Error: No se encontró el archivo de entrada en data/input/sar.py")
        return

    # 3. Inicializar el Crew con el código y ejecutarlo
    print("Iniciando análisis multi-agente...")
    analysis_flow = CodeAnalysisCrew(code_to_analyze)
    result = analysis_flow.run()

    # 4. Crear la carpeta de salida si no existe
    output_path = "outputs/reports"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # 5. Generar el reporte PDF
    print("Generando reporte PDF...")
    pdf = FPDF()
    pdf.add_page()
    
    try:
        pdf.set_font("Arial", size=11)
    except:
        pdf.add_font("Arial", fname="C:/Windows/Fonts/arial.ttf")
        pdf.set_font("Arial", size=11)

    # El objeto 'result' de CrewAI tiene un atributo .raw con el string final
    contenido_final = str(result.raw) if hasattr(result, 'raw') else str(result)

    pdf.multi_cell(0, 6, contenido_final)
    
    report_name = f"{output_path}/report.pdf"
    pdf.output(report_name)
    
    print(f"¡Hecho! El reporte se ha guardado en: {report_name}")

if __name__ == "__main__":
    run_analysis()
