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
        print("Uso:    python main.py <github_repo_url>")
        print("Ejemplo: python main.py https://github.com/usuario/repo")
        sys.exit(1)
 
    repo_url = sys.argv[1].rstrip("/")
 
    if not repo_url.startswith("https://github.com/"):
        print("Error: la URL debe ser de GitHub (https://github.com/usuario/repo)")
        sys.exit(1)
 
    # Nombre del repo para nombrar los archivos de salida
    filename = repo_url.split("/")[-1]
 
    os.makedirs("reports", exist_ok=True)
 
    print(f"\nAnalizando repositorio: {repo_url}")
    print(f"Informe de salida:      reports/review_{filename}.md\n")
 
    CodeAnalysisCrew().run().kickoff(inputs={
        "repo_url": repo_url,
        "filename": filename,
    })


    print(f"\n Full report saved to: outputs/reports/review_{filename}.md")

if __name__ == "__main__":
    main()
