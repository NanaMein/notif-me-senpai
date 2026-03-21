from crewai import *
from fastapi.concurrency import run_in_threadpool
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



def _internal_kickoff(input_data: dict[str, str]):
    _kickoff = crew().kickoff(inputs=input_data)
    return _kickoff

async def agent_task_runner(message: str):
    try:
        input_message = {"message":message}
        result = await run_in_threadpool(_internal_kickoff, input_message)
        return result
    except Exception as e:
        return None
