from crewai import Agent
from langchain_openai import ChatOpenAI
import yaml

llm = LLM(
    model="openai/gpt-oss-120b",
    base_url=os.getenv("API_BASE"),
    api_key=os.getenv("API_KEY"),
    temperature=0.2,
    max_retries=5,
)

class CodeAgents:

    def analizador(self) -> Agent:
        return Agent(config=self.config['analizador'], llm=self.llm, verbose=True)

    def optimizador(self) -> Agent:
        return Agent(config=self.config['optimizador'], llm=self.llm, verbose=True)

    def documentador(self) -> Agent:
        return Agent(config=self.config['documentador'], llm=self.llm, verbose=True)
