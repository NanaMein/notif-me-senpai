from typing import *
from abc import ABC, abstractmethod
from pathlib import Path
import yaml
import json
try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources




class LoaderABC(ABC):
    def __init__(self, file_path: Union[str, None] = None) -> None:
        self._file_path = file_path

    @abstractmethod
    def _load_resources(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_prompt(self, key_destination: str) -> str:
        pass


class PromptLoader(LoaderABC):
    def __init__(self, file_path: Union[str, None] = None):
        super().__init__(file_path)
        self._base_dir = Path(__file__).parent
        self.data = self._load_resources()

    @property
    def file_path(self):
        if self._file_path is None:
            return "agents.yaml"
        return self._file_path


    def _load_resources(self) -> Dict[str, Any]:
        try:
            full_path = self._base_dir / self.file_path
            with open(full_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {}

        except (FileNotFoundError, yaml.YAMLError):
            return {}

    def get_prompt(self, key_destination: str) -> str:
        data = self.data
        try:
            for keys in key_destination.split("."):
                data = data[keys]

            if isinstance(data, (dict, list)):
                return json.dumps(data, indent=2, ensure_ascii=False)

            return str(data)

        except KeyError:
            return f"{key_destination} is not a valid key"

class BasePrompt:
    def __init__(self, yaml_file_name: str) -> None:
        self.prompt_loader = PromptLoader(file_path=yaml_file_name)

    def get_prompt(self, key_destination: str) -> str:
        return self.prompt_loader.get_prompt(key_destination=key_destination)

class AgentPrompts(BasePrompt):
    def __init__(self):
        super().__init__("agents.yaml")


class TaskPrompts(BasePrompt):
    def __init__(self):
        super().__init__("tasks.yaml")

