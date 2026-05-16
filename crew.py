from crewai import Crew, Process
from agents import CodeAgents
from tasks import CodeTasks

class CodeAnalysisCrew:
    def __init__(self, code):
        self.code = code

    def run(self):
        agents = CodeAgents()
        tasks = CodeTasks()

        # Instanciar agentes
        analista = agents.analizador()
        optimista = agents.optimizador()
        doc = agents.documentador()

        # Instanciar tareas
        t1 = tasks.tarea_analisis(analista)
        t2 = tasks.tarea_optimizacion(optimista)
        t3 = tasks.tarea_documentacion(doc)

        crew = Crew(
            agents=[analista, optimista, doc],
            tasks=[t1, t2, t3],
            process=Process.sequential, # El orden importa aquí
            verbose=True
        )

        return crew.kickoff(inputs={'code': self.code})

