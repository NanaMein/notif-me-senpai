from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent



class _AzureSettings(BaseSettings):
    AZURE_EXISTING_AIPROJECT_ENDPOINT: SecretStr
    AGENT_NAME_1: str
    AGENT_VERSION_1: str

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env.azure",
        env_file_encoding="utf-8",
        extra="ignore"
    )


class Settings:
    _azure = _AzureSettings()
    existing_aiproject_endpoint = _azure.AZURE_EXISTING_AIPROJECT_ENDPOINT

    @property
    def agent_reference(self) -> tuple[str, str]:
        _name = self._azure.AGENT_NAME_1
        _version = self._azure.AGENT_VERSION_1
        return _name, _version

    @property
    def agents(self):
        return {
            "name":self._azure.AGENT_NAME_1,
            "version":self._azure.AGENT_VERSION_1,
        }

azure_settings = Settings()

