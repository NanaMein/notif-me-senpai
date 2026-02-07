from crewai import *
from abc import ABC, abstractmethod
from backend.data_store.prompt_loader import PromptLoader, AgentPrompts, TaskPrompts
from backend.agents.groq_llm import GroqLLM

load_agent = AgentPrompts()
load_task = TaskPrompts()
llm = GroqLLM(model="meta-llama/llama-4-scout-17b-16e-instruct")
def agent():
    return Agent(
        role=load_agent.get_prompt("v1.agent.role"),
        backstory=load_agent.get_prompt("v1.agent.backstory"),
        goal=load_agent.get_prompt("v1.agent.goal"),
        llm=llm
    )

def task():
    return Task(
        description=load_task.prompt_loader.get_prompt("v1.task.description"),
        expected_output=load_task.prompt_loader.get_prompt("v1.task.expected_output"),
        agent=agent()
    )

def _task():
    return Task(
        description=load_task.prompt_loader.get_prompt("v1.task.description"),
        expected_output=load_task.prompt_loader.get_prompt("v1.task.expected_output"),
        agent=agent()
    )
def crew():
    return Crew(
        agents=[agent()],
        tasks=[task()],
        process=Process.sequential
    )

c = crew()
ck = c.kickoff(inputs={"input":"Uy kamusta ka na beh? nakaka loka na dito sa boracay, ang hohot ng mga guys here. "})
print(ck)