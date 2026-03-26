from typing import Any
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from backend.agents.azure.azure_configs import azure_settings
from functools import lru_cache
from starlette.concurrency import run_in_threadpool
from datetime import datetime, timezone


@lru_cache(maxsize=1)
def azure_client(place_holder_id: str | None = None):
    endpoint = azure_settings.existing_aiproject_endpoint
    return AIProjectClient(
        endpoint=endpoint.get_secret_value(),
        credential=DefaultAzureCredential(),
    )


class AzureChatCompletionBase:
    def __init__(
            self,
            client: AIProjectClient,
            message: str | list[dict[str, str]],
    ):
        self._client = client
        self._message = message

    @property
    def message(self):
        return self.message_handler(self._message)

    @property
    def client(self):
        return self._client

    @staticmethod
    def message_handler(input_message: Any) -> list[dict[str, str]]:
        if isinstance(input_message, str):
            messages = [{"role": "user", "content": input_message}]
        elif isinstance(input_message, list):
            messages = input_message
        else:
            messages = [{"role": "user", "content": str(input_message)}]
        return messages

    async def execute(self):
        response = await run_in_threadpool(azure_query_engine, self.message, self.client)
        return response




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