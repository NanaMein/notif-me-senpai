from typing import Any
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from backend.agents.azure.azure_configs import azure_settings


class AzureAgentService:
    def __init__(self, agent_reference: dict[str, Any] | None = None):
        self._credential: None | DefaultAzureCredential = None
        self._client: None | AIProjectClient = None
        self._agent_reference = agent_reference


    @property
    def extra_body(self) -> dict[str, Any]:
        if self._agent_reference is None:
            agents = azure_settings.agents
            self._agent_reference = {"agent_reference": {"name": agents["name"] , "version": agents["version"], "type": "agent_reference"}}
        return self._agent_reference

    async def credential(self):
        if self._credential is None:
            self._credential = DefaultAzureCredential()
        return self._credential


    async def client(self):
        if self._client is None:
            credential = await self.credential()
            self._client = AIProjectClient(
                endpoint=azure_settings.existing_aiproject_endpoint.get_secret_value(),
                credential=credential
            )
        return self._client

    async def agent_run(self, inputs: str | list[dict[str, str]]):
        client = await self.client()
        async with client.get_openai_client() as openai_client:
            if isinstance(inputs, str):
                input_list = [{"role": "user", "content": inputs}]
            else:
                input_list = inputs

            response = await openai_client.responses.create(
                input=input_list,
                extra_body=self.extra_body,
            )
            return response.output_text




my_agent = "generate-chat-completion"
my_version = "4"


def azure_query_engine(input_message: str | list[dict[str, str]], client: AIProjectClient):
    if isinstance(input_message, str):
        messages = [{"role": "user", "content": input_message}]
    else:
        messages = input_message

    openai_client = client.get_openai_client()
    response_output = openai_client.responses.create(
        input=messages,
        extra_body={
            "agent_reference": {
                "name": my_agent,
                "version": my_version,
                "type":"agent_reference"
            }
        }
    )
    return response_output.output_text


import time
start = time.perf_counter()
obj = AzureChatCompletionBase(
    client=azure_client(),
    message="Nice to meet you! tell me more about yourself. What is your name?"
)
mid = time.perf_counter()
print("TIME FOR OBJECT INSTANCE:\n", mid - start)
import asyncio
print(asyncio.run(obj.execute()))
end = time.perf_counter()

print("TIME RECORDED\n",end - start )