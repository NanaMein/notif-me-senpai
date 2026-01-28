from typing import Union
from cachetools import LRUCache
from threading import Lock
import asyncio

MEMORY_CACHE = LRUCache(10)

LOCK = Lock()

class MemoryDB:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.lock = LOCK


    def add_user(self, content):
        _user = {"role":"user","content":content}
        with self.lock:
            cache = self._internal_cache()
            cache.append(_user)
            return self

    def add_assistant(self, content):
        _assistant = {"role":"assistant","content":content}
        with self.lock:
            cache = self._internal_cache()
            cache.append(_assistant)
            return self

    def _internal_cache(self) -> list:
        _cache = MEMORY_CACHE.get(self.user_id)

        if isinstance(_cache, list):
            return _cache

        new_cache = []
        MEMORY_CACHE[self.user_id] = new_cache
        return new_cache

    def get_messages(self):
        with self.lock:
            cache = self._internal_cache()
            return cache




_CACHE_FOR_LOCKS = LRUCache(10)
_MASTER_LOCK = asyncio.Lock()


class MemoryAsyncDB:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.cache_for_locks = _CACHE_FOR_LOCKS
        self.master_lock = _MASTER_LOCK


    async def add_user(self, content):
        _lock = await self._internal_lock()
        async with _lock:
            _user = {"role":"user","content":content}
            cache = self._internal_cache()
            cache.append(_user)
            return self

    async def add_assistant(self, content):
        _lock = await self._internal_lock()
        async with _lock:
            _assistant = {"role":"assistant","content":content}
            cache = self._internal_cache()
            cache.append(_assistant)
            return self

    async def _internal_lock(self):
        cached_lock = self.cache_for_locks.get(self.user_id)

        if isinstance(cached_lock, asyncio.Lock):
            return cached_lock

        async with self.master_lock:

            new_lock = asyncio.Lock()
            self.cache_for_locks[self.user_id] = new_lock
            return new_lock


    def _internal_cache(self) -> list:
        _cache = MEMORY_CACHE.get(self.user_id)

        if isinstance(_cache, list):
            return _cache

        new_cache = []
        MEMORY_CACHE[self.user_id] = new_cache
        return new_cache

    async def get_messages(self):
        _lock = await self._internal_lock()
        async with _lock:
            cache = self._internal_cache()
            return cache

