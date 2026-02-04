from typing import Union, Dict, Optional, List
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
import asyncio
import uuid
import time



_MASTER_LOCK = asyncio.Lock()
_USER_MEMORY: Dict[str, "UserMemory"] = {}
_CLEANUP_TASK: Optional[asyncio.Task] = None
MAX_TTL_SECONDS = 3600
CLEANUP_INTERVAL = 600
DEFAULT_SYSTEM = "You are a helpful assistant"


class UserMemory:
    __slots__ = ["lock","messages","last_accessed"]
    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self.messages: list[BaseMessage] = []
        self.last_accessed: float = time.monotonic()

async def _background_cleanup() -> None:
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        time_now = time.monotonic()
        keys_to_remove = []

        async with _MASTER_LOCK:
            for user_id, mem in _USER_MEMORY.items():
                time_before = mem.last_accessed

                time_computed = time_now - time_before

                if time_computed > MAX_TTL_SECONDS:
                    keys_to_remove.append(user_id)

            for key in keys_to_remove:
                del _USER_MEMORY[key]


class MemoryAsyncDB:
    def __init__(self, user_id: Union[str, uuid.UUID, None] = None):
        self._user_id = user_id

        global _CLEANUP_TASK
        if _CLEANUP_TASK is None:
            try:
                loop = asyncio.get_running_loop()
                _CLEANUP_TASK = loop.create_task(_background_cleanup())
            except RuntimeError:
                pass


    @property
    def user_id(self):
        _id = self._user_id

        if _id is None:
            return "user123testing"

        if isinstance(_id, uuid.UUID):
            _id = _id.hex
        return _id

    async def _get_user_memory(self) -> UserMemory:
        user_id = self.user_id

        mem = _USER_MEMORY.get(user_id)
        if mem:
            mem.last_accessed = time.monotonic()
            return mem

        async with _MASTER_LOCK:
            mem = _USER_MEMORY.get(user_id)
            if mem is None:
                mem = UserMemory()
                _USER_MEMORY[user_id] = mem
            mem.last_accessed = time.monotonic()
            return mem

    async def add_human_message(self, content: str):
        mem = await self._get_user_memory()
        async with mem.lock:
            mem.messages.append(HumanMessage(content=content))
            mem.last_accessed = time.monotonic()
        return self

    async def add_ai_message(self, content: str):
        mem = await self._get_user_memory()
        async with mem.lock:
            mem.messages.append(AIMessage(content=content))
            mem.last_accessed = time.monotonic()
        return self

    async def get_messages(self) -> List[BaseMessage]:
        mem = await self._get_user_memory()
        async with mem.lock:
            return list(mem.messages)

    async def get_messages_with_system(self, system_prompt: str = DEFAULT_SYSTEM) -> List[BaseMessage]:
        mem = await self._get_user_memory()
        async with mem.lock:
            return [SystemMessage(content=system_prompt), *mem.messages]