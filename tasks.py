from crewai import Task
import yaml

class CodeTasks:
    def __init__(self):
        with open('config/tasks.yaml', 'r') as f:
            self.config = yaml.safe_load(f)

    def tarea_analisis(self, agent) -> Task:
        return Task(config=self.config['tarea_analisis'], agent=agent)

    def tarea_optimizacion(self, agent) -> Task:
        return Task(config=self.config['tarea_optimizacion'], agent=agent)

    def tarea_documentacion(self, agent) -> Task:
        return Task(config=self.config['tarea_documentacion'], agent=agent)
