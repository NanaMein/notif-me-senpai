from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from backend.agents.azure.azure_configs import azure_settings



my_endpoint = azure_settings.existing_aiproject_endpoint

project_client = AIProjectClient(
    endpoint=my_endpoint.get_secret_value(),
    credential=DefaultAzureCredential(),
)

my_agent = "generate-chat-completion"
my_version = "3"


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


# response = azure_query_engine(
#     input_message="Tell me what you can help with.",
#     client=project_client
# )
#
# print(response)