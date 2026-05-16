from crewai import Crew, Process
from agents import CodeAgents
from tasks import CodeTasks

class CodeAnalysisCrew:
    def run(self):
        agents = CodeAgents()
        tasks = CodeTasks()

        # Instanciar agentes
        explorador = agents.explorador()
        analista = agents.analizador()
        optimista = agents.optimizador()
        estilista = agents.estilista()
        documentador = agents.documentador()

        # Instanciar tareas
        # Procesamiento
        t0 = tasks.tarea_exploracion(explorador)

        # Analistas
        t1 = tasks.tarea_analisis(analista, context=[t0])
        t2 = tasks.tarea_optimizacion(optimista, context=[t0])
        t3 = tasks.tarea_buenas_practicas(estilista, context=[t0])
 
        # Creación de documentos
        t4 = tasks.tarea_documentacion(documentador, context=[t0, t1, t2, t3])
        t5 = tasks.generate_pdf_task(documentador, context=[t4])

        crew = Crew(
            agents=[explorador, analista, optimista, estilista, documentador],
            tasks=[t0, t1, t2, t3, t4, t5],
            process=Process.sequential,
            verbose=True
        )

        return crew

