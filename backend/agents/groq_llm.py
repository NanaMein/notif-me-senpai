from typing import Any, Dict, List, Optional, Union
from groq import Groq
from crewai.llms.base_llm import BaseLLM
from backend.core.env_file import settings
from threading import Lock

_GROQ_CLIENT: Optional[Groq] = None
_GROQ_LOCK = Lock()

def get_groq_client() -> Groq:
    global _GROQ_CLIENT
    if _GROQ_CLIENT is None:
        with _GROQ_LOCK:
            if _GROQ_CLIENT is None:
                _GROQ_CLIENT = Groq(
                    api_key=settings.GROQ_API_KEY.get_secret_value(),
                )

    return _GROQ_CLIENT


class GroqLLM(BaseLLM):
    """
    A minimal Groq LLM adapter for CrewAI using composition internally.
    Supports Qwen and GPT-OSS models with proper reasoning_effort handling.
    """

    def __init__(
            self,
            model: str,
            temperature: Optional[float] = None,
            max_tokens: Optional[int] = None,
            **kwargs,
    ):
        # ✧ inherit BaseLLM contract ✧
        super().__init__(model=model, temperature=temperature)

        # ✧ compose with Groq client ✧

        self._client = get_groq_client()
        self._max_tokens = max_tokens or 8000
        self._model_family = self._detect_model_family(model)
        self._extra_params = kwargs  # for tools/reasoning_effort etc.

    def _detect_model_family(self, model_name: str) -> str:
        """Detect if model is qwen or gpt_oss for parameter mapping."""
        lower = model_name.lower()
        if "qwen" in lower:
            return "qwen"
        elif "gpt-oss" in lower or "gpt" in lower:
            return "gpt_oss"
        return "other"

    def call(
            self,
            messages: Union[str, List[Dict[str, str]]],
            tools: Optional[List[dict]] = None,
            callbacks: Optional[List[Any]] = None,
            available_functions: Optional[Dict[str, Any]] = None,
    ) -> str:
        # ✧ normalize messages ✧
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        # ✧ prepare Groq params ✧
        params: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature if self.temperature is not None else 0.7,
            "max_tokens": self._max_tokens,
            "stream": False,
        }

        # ✧ handle reasoning_effort safely per model ✧
        if "reasoning_effort" in self._extra_params:
            effort = self._extra_params["reasoning_effort"]
            if self._model_family == "qwen":
                if effort in ("none", "default"):
                    params["reasoning_effort"] = effort
            elif self._model_family == "gpt_oss":
                if effort in ("none", "default", "low", "medium", "high"):
                    params["reasoning_effort"] = effort

        # ✧ pass tools if provided ✧
        if tools:
            params["tools"] = tools

        # ✧ make the call ✧ (no error handling per your wish~)
        completion = self._client.chat.completions.create(**params)
        return completion.choices[0].message.content or ""

    def supports_stop_words(self) -> bool:
        return True

    def get_context_window_size(self) -> int:
        # ✧ safe defaults ✧
        sizes = {
            "qwen": 32768,
            "gpt_oss": 128000,
            "other": 8192,
        }
        return sizes.get(self._model_family, 8192)