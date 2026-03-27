from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent



class _AzureSettings(BaseSettings):
    AZURE_EXISTING_AGENT_ID: str
    AZURE_ENV_NAME: SecretStr
    AZURE_LOCATION: SecretStr
    AZURE_SUBSCRIPTION_ID: SecretStr
    AZURE_EXISTING_AIPROJECT_ENDPOINT: SecretStr
    AZURE_EXISTING_AIPROJECT_RESOURCE_ID: SecretStr
    AZURE_EXISTING_RESOURCE_ID: str
    AZURE_OPENAI_ENDPOINT: SecretStr
    AZURE_API_KEY: SecretStr

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env.azure",
        env_file_encoding="utf-8",
        extra="ignore"
    )


class Settings:
    _azure = _AzureSettings()
    existing_agent_id = _azure.AZURE_EXISTING_AGENT_ID
    env_name=_azure.AZURE_ENV_NAME
    location = _azure.AZURE_LOCATION
    subscription_id = _azure.AZURE_SUBSCRIPTION_ID
    existing_aiproject_endpoint = _azure.AZURE_EXISTING_AIPROJECT_ENDPOINT
    existing_aiproject_resource_id=_azure.AZURE_EXISTING_AIPROJECT_RESOURCE_ID
    existing_resource_id = _azure.AZURE_EXISTING_RESOURCE_ID
    openai_endpoint = _azure.AZURE_OPENAI_ENDPOINT
    api_key = _azure.AZURE_API_KEY

azure_settings = Settings()


