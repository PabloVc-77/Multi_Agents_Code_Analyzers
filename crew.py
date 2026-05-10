# AGENTS

import os
from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model= "openai/gpt-oss-120b",
    base_url=os.getenv("API_BASE"),
    api_key=os.getenv("API_KEY"),
    temperature=0.2,
    max_retries=5,
)

code_analyzer = Agent(
    role="Code Analyzer",
    goal="Detect errors and bad practices in code",
    backstory="Expert software reviewer specialized in clean code.",
    llm=llm
)

optimizer = Agent(
    role="Code Optimizer",
    goal="Suggest performance and readability improvements",
    backstory="Expert in code optimization and software architecture.",
    llm=llm
)

documenter = Agent(
    role="Code Documenter",
    goal="Generate technical documentation",
    backstory="Expert technical writer specialized in software documentation.",
    llm=llm
)

# TASKS

from crewai import Task

analyze_task = Task(
    description="Analyze the following code and detect bugs, bad practices and security issues:\n\n{code}",
    agent=code_analyzer,
    expected_output="List of detected issues."
)

optimize_task = Task(
    description="Suggest performance, readability and maintainability improvements for the following code:\n\n{code}",
    agent=optimizer,
    expected_output="Optimization suggestions."
)

document_task = Task(
    description="Generate clear technical documentation in Markdown for the following code:\n\n{code}",
    agent=documenter,
    expected_output="Markdown technical documentation."
)

# CREW
from crewai import Crew

code_analysis_crew = Crew(
    agents=[
        code_analyzer,
        optimizer,
        documenter
    ],
    tasks=[
        analyze_task,
        optimize_task,
        document_task
    ],
    process="sequential",
    verbose=True
)