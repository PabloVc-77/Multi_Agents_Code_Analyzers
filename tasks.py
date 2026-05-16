from crewai import Task
import yaml

class CodeTasks:
    def __init__(self):
        with open('config/tasks.yaml', 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

    # TAREA 0
    def tarea_exploracion(self, agent) -> Task:
        return Task(
            config=self.config['explorar_repositorio'],
            agent=agent
        )

    # TAREA 1
    def tarea_analisis(self, agent, context) -> Task:
        return Task(
            config=self.config['analisis_de_seguridad'],
            agent=agent,
            context=context
        )

    # TAREA 2
    def tarea_optimizacion(self, agent, context) -> Task:
        return Task(
            config=self.config['tarea_optimizacion'],
            agent=agent,
            context=context
        )
    
    # TAREA 3
    def tarea_buenas_practicas(self, agent, context) -> Task:
        return Task(
            config=self.config['buenas_practicas'],
            agent=agent,
            context=context
        )

    # TAREA 4
    def tarea_documentacion(self, agent, context) -> Task:
        return Task(
            config=self.config['resumir'],
            agent=agent,
            context=context
        )
    
    # TAREA 5
    def generate_pdf_task(self, agent, context) -> Task:
        return Task(
            config=self.config['generate_pdf_task'],
            agent=agent,
            context=context
        )
