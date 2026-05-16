from crewai import Agent, LLM
import yaml
import os
from tools import generar_pdf, obtener_metadatos_github, leer_repositorio_github
class CodeAgents:

    def __init__(self):

        # Configuración del modelo
        self.llm = LLM(
            model="openai/gpt-oss-120b",
            base_url=os.getenv("API_BASE"),
            api_key=os.getenv("API_KEY"),
            temperature=0.2,
            max_retries=5,
        )

        # Cargar YAML
        with open("config/agents.yaml", "r", encoding="utf-8") as file:
            self.config = yaml.safe_load(file)

    def explorador(self) -> Agent:
        return Agent(
            config=self.config['explorador'],
            llm=self.llm,
            tools=[obtener_metadatos_github, leer_repositorio_github],
            verbose=True
        )


    def analizador(self) -> Agent:
        return Agent(
            config=self.config['analizador'],
            llm=self.llm,
            verbose=True
        )

    def optimizador(self) -> Agent:
        return Agent(
            config=self.config['optimizador'],
            llm=self.llm,
            verbose=True
        )
    
    def estilista(self) -> Agent:
        return Agent(
            config=self.config['estilista'],
            llm=self.llm,
            verbose=True
        )

    def documentador(self) -> Agent:
        return Agent(
            config=self.config['documentador'],
            llm=self.llm,
            verbose=True,
            tools=[generar_pdf]
        )
