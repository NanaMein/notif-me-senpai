import asyncio
from typing import Any
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from backend.agents.azure.azure_configs import azure_settings
from personality_agent import AzureAgentService



# ---------------------------
# 1. Create Project Client
# ---------------------------
async def create_project_client():
    credential = DefaultAzureCredential()

    project_client = AIProjectClient(
        endpoint=azure_settings.existing_aiproject_endpoint.get_secret_value(),
        credential=credential,
    )

    return project_client, credential

async def chat_with_model(project_client, message: str | list[dict[str, str]]):
    async with project_client.get_openai_client() as openai_client:
        if isinstance(message, str):
            messages = [{"role": "user", "content": message}]
        else:
            messages = message

        my_agent = "kokomi-trial-agent"
        my_version = "2"
        # _test_openai_client = OpenAI()
        # _test_openai_client.completions.create(
        #     prompt=message, model=my_agent
        # )
        # response = await openai_client.completions.create(
        #     prompt=message, model=my_agent,
        #     extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
        # )

        # response = await openai_client.responses.create(
        #     input=[{"role": "user", "content": message}],
        #     extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
        # )

        response = await openai_client.responses.create(
            input=messages,
            extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
        )
        return response.output_text



# ---------------------------
# 3. Optional: Agent Run
# ---------------------------
async def run_agent(project_client, agent_id: str, message: str):
    # create thread
    thread = await project_client.agents.create_thread()

    # send message
    await project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=message,
    )

    # run agent
    run = await project_client.agents.create_run(
        thread_id=thread.id,
        agent_id=agent_id,
    )

    # wait until done
    while run.status in ["queued", "in_progress"]:
        await asyncio.sleep(1)
        run = await project_client.agents.get_run(
            thread_id=thread.id,
            run_id=run.id,
        )

    # get messages
    messages = await project_client.agents.list_messages(thread.id)

    return messages


# ---------------------------
# 4. Test Entry Point
# ---------------------------
async def main(testing_class: bool = False):
    project_client, credential = await create_project_client()
    azure_object = AzureAgentService()
    await azure_object.start()

    try:
        print("=== Testing Chat ===")
        is_list = False
        if is_list:
            message = [
                {"role": "user", "content": "Hello my name is alpapi nice to meet you *Hugs sweetly but friendly*"},
                {"role": "assistant",
                 "content": "Greetings, Alpapi. It is a pleasure to make your acquaintance. *This one appreciates your kindness and warmth.* Please, feel free to share anything on your mind or let me know how I may be of assistance today."},
                {"role": "user", "content": "How can i be friends with someone like you *expecting gaze*"}
            ]
        else:
            message = "Hello my name is alpapi nice to meet you *Hugs sweetly but friendly*"

        if not testing_class:
            response = await chat_with_model(project_client, message=message)

        else:

            response = await azure_object.agent_run(message)
        print(response)

        # OPTIONAL: Agent test
        # agent_id = "your-agent-id"
        # messages = await run_agent(project_client, agent_id, "Explain async in Python")
        # print(messages)

    finally:
        await project_client.close()
        await credential.close()
        await azure_object.stop()



if __name__ == "__main__":
    asyncio.run(main(testing_class=True))