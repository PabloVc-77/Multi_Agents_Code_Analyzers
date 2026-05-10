from dotenv import load_dotenv
load_dotenv()

from tools import read_code_file
from crew import code_analysis_crew

# Leer archivo de código
code = read_code_file("data/input/ejemplo.py")

# Ejecutar CrewAI
result = code_analysis_crew.kickoff(
    inputs={"code": code}
)

# Mostrar resultado
print(result)