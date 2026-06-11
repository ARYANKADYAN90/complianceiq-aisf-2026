from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Azure AI Foundry
    azure_foundry_project_endpoint: str = ""
    azure_foundry_model_deployment: str = "gpt-4.1-mini"

    # Azure AI Search (Foundry IQ backend)
    azure_search_endpoint: str = ""
    azure_search_api_key: str = ""  # Optional, supports keyless via DefaultAzureCredential
    foundry_iq_knowledge_base_name: str = "compliance-iq-kb"

    # Azure Document Intelligence
    azure_document_intelligence_endpoint: str = ""
    azure_document_intelligence_key: str = ""

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str = ""
    otel_service_name: str = "complianceiq"

    # App Config
    mock_mode: bool = True
    log_level: str = "INFO"
    max_file_size_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def validate_azure_credentials(self) -> None:
        """Validate that real Azure credentials are present if mock_mode is False."""
        if not self.mock_mode:
            missing = []
            if not self.azure_foundry_project_endpoint:
                missing.append("AZURE_FOUNDRY_PROJECT_ENDPOINT")
            if not self.azure_search_endpoint:
                missing.append("AZURE_SEARCH_ENDPOINT")
            
            if missing:
                raise ValueError(
                    f"mock_mode is False, but the following required environment variables "
                    f"are missing for live Azure connection: {', '.join(missing)}"
                )


@lru_cache()
def get_settings() -> Config:
    """Get cached application settings."""
    settings = Config()
    settings.validate_azure_credentials()
    return settings
