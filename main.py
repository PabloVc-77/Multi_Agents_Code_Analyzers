import os
from dotenv import load_dotenv
from crew import CodeAnalysisCrew

import sys
import re

def clean_text(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# Cargar variables de entorno (API Keys, etc.)
load_dotenv()

def main():
    # PRE-PROCESAR INFORMACIÓN
    if len(sys.argv) < 2:
        print("No se han aportado archivos para analizar")
        print("Uso: python main.py <path_to_file>")
        sys.exit(1)

    filepath = sys.argv[1]

    if not os.path.exists(filepath):
        print(f"No se ha encontrado el archivo: {filepath}")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
 
    filename = os.path.basename(filepath)

    # Iniciar la CREW
    CodeAnalysisCrew().run().kickoff(
        inputs={
            "code": code,
            "filename": filename,
        }
    )

    print(f"\n Full report saved to: outputs/reports/review_{filename}.md")

if __name__ == "__main__":
    main()
