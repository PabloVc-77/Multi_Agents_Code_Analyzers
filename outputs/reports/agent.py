from crewai import Agent
from langchain_openai import ChatOpenAI
import yaml

class CodeAgents:
    def __init__(self):
        with open('config/agents.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        self.llm = ChatOpenAI(model_name="gpt-4o")

    def analizador(self) -> Agent:
        return Agent(config=self.config['analizador'], llm=self.llm, verbose=True)

    def optimizador(self) -> Agent:
        return Agent(config=self.config['optimizador'], llm=self.llm, verbose=True)

    def documentador(self) -> Agent:
        return Agent(config=self.config['documentador'], llm=self.llm, verbose=True)
