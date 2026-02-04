from typing import Any, Union, Tuple
from backend.databases.memory import MemoryAsyncDB
from langchain_groq.chat_models import ChatGroq
from backend.core.env_file import settings
from langchain_core.messages import BaseMessage

chat = ChatGroq(
    api_key=settings.GROQ_API_KEY.get_secret_value(),
    temperature=.7,
    model="llama-3.1-8b-instant",
    max_tokens=8000
)
Response_Type = Union[str, list[Union[str,dict]]]
List_Types = list[BaseMessage]
Tuple_type = Tuple[Response_Type, List_Types]

async def ask_query(user_id: Union[str, Any], query: str) -> Tuple_type:
    if not isinstance(user_id, str):
        user_id = str(user_id)

    mem = MemoryAsyncDB(user_id=user_id)

    await mem.add_human_message(content=query)

    messages = await mem.get_messages_with_system()

    resp = await chat.ainvoke(messages)

    response = resp.content

    await mem.add_ai_message(content=response)

    list_message = await mem.get_messages_with_system()

    return response, list_message