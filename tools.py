import os
import tempfile
import shutil
from pathlib import Path
from crewai.tools import tool
from fpdf import FPDF
import re

CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
    '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.yaml',
    '.yml', '.json', '.toml', '.sh', '.bash', '.sql', '.html', '.css',
}
 
# Carpetas a ignorar para no saturar el contexto
IGNORED_DIRS = {
    '.git', 'node_modules', '__pycache__', '.venv', 'venv', 'env',
    'dist', 'build', '.next', '.nuxt', 'coverage', '.pytest_cache',
}
 
 
@tool("Lector de Repositorio GitHub")
def leer_repositorio_github(repo_url: str) -> str:
    """
    Clona un repositorio de GitHub y devuelve el contenido completo
    de todos sus archivos de código fuente, junto con la estructura de directorios.
    Recibe la URL del repositorio (ej: https://github.com/usuario/repo).
    Devuelve un string con la estructura del proyecto y el código de cada archivo.
    """
    import subprocess
 
    tmpdir = tempfile.mkdtemp()
    try:
        result = subprocess.run(
            ["git", "clone", "--depth=1", repo_url, tmpdir],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return f"Error al clonar el repositorio:\n{result.stderr}"
 
        # Árbol de archivos
        tree_lines = []
        archivos_codigo = []
 
        for path in sorted(Path(tmpdir).rglob("*")):
            # Ignorar carpetas no relevantes
            if any(ignored in path.parts for ignored in IGNORED_DIRS):
                continue
            if path.is_file() and path.suffix in CODE_EXTENSIONS:
                rel = path.relative_to(tmpdir)
                tree_lines.append(str(rel))
                try:
                    contenido = path.read_text(encoding="utf-8", errors="ignore")
                    # Limitar archivos muy grandes
                    if len(contenido) > 15000:
                        contenido = contenido[:15000] + "\n... [archivo truncado] ..."
                    archivos_codigo.append(
                        f"\n\n### Archivo: {rel}\n```{path.suffix.lstrip('.')}\n{contenido}\n```"
                    )
                except Exception as e:
                    tree_lines.append(f"  (no se pudo leer: {e})")
 
        estructura = "## Estructura del repositorio\n" + "\n".join(tree_lines)
        codigo = "\n".join(archivos_codigo)
 
        return f"{estructura}\n\n## Código fuente\n{codigo}"
 
    except Exception as e:
        return f"Error inesperado: {e}"
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
 
 
@tool("Metadatos de Repositorio GitHub")
def obtener_metadatos_github(repo_url: str) -> str:
    """
    Obtiene metadatos de un repositorio de GitHub usando la API:
    descripción, lenguajes, stars, forks, issues abiertos y últimos commits.
    Recibe la URL del repositorio (ej: https://github.com/usuario/repo).
    Requiere la variable de entorno GITHUB_TOKEN.
    """
    from github import Github, GithubException
 
    token = os.getenv("GITHUB_TOKEN")
    g = Github(token) if token else Github()
 
    repo_path = repo_url.rstrip("/").replace("https://github.com/", "")
    try:
        repo = g.get_repo(repo_path)
        langs = repo.get_languages()
        open_issues = repo.open_issues_count
        commits = list(repo.get_commits()[:5])
 
        ultimos_commits = "\n".join(
            [f"  - {c.commit.message.splitlines()[0][:80]}" for c in commits]
        )
 
        return f"""## Metadatos del repositorio
 
Nombre:        {repo.full_name}
Descripción:   {repo.description or 'Sin descripción'}
Lenguajes:     {', '.join(langs.keys()) or 'Desconocido'}
Stars:         {repo.stargazers_count}
Forks:         {repo.forks_count}
Issues abiertos: {open_issues}
Rama principal: {repo.default_branch}
Licencia:      {repo.license.name if repo.license else 'Sin licencia'}
Última actualización: {repo.updated_at.strftime('%Y-%m-%d')}
 
Últimos 5 commits:
{ultimos_commits}
"""
    except GithubException as e:
        return f"Error de GitHub API: {e.status} - {e.data.get('message', '')}"
    except Exception as e:
        return f"Error inesperado: {e}"


def _limpiar_markdown(texto: str) -> str:
    """Elimina sintaxis markdown para texto plano en el PDF."""
    texto = re.sub(r'#{1,6}\s*', '', texto)
    texto = re.sub(r'\*\*(.*?)\*\*', r'\1', texto)
    texto = re.sub(r'\*(.*?)\*', r'\1', texto)
    texto = re.sub(r'`{1,3}.*?`{1,3}', '', texto)
    texto = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', texto)
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
        elif linea.strip().startswith("- ") or linea.strip().startswith("* "):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, f"  • {linea_limpia[2:]}")
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(0, 6, linea_limpia)
 
    pdf.output(pdf_path)
    return f"PDF generado correctamente en: {pdf_path}"
