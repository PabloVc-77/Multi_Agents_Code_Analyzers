from crewai import Crew, Process
from agents import CodeAgents
from tasks import CodeTasks

class CodeAnalysisCrew:
    def run(self):
        agents = CodeAgents()
        tasks = CodeTasks()

        # Instanciar agentes
        analista = agents.analizador()
        optimista = agents.optimizador()
        estilista = agents.estilista()
        documentador = agents.documentador()

        # Instanciar tareas
        t1 = tasks.tarea_analisis(analista)
        t2 = tasks.tarea_optimizacion(optimista, context=[t1])
        t3 = tasks.tarea_buenas_practicas(estilista, context=[t1, t2])
        t4 = tasks.tarea_documentacion(documentador, context=[t1, t2, t3])
        t5 = tasks.generate_pdf_task(documentador, context=[t4])

        crew = Crew(
            agents=[analista, optimista, estilista, documentador],
            tasks=[t1, t2, t3, t4, t5],
            process=Process.sequential,
            verbose=True
        )

        return crew

