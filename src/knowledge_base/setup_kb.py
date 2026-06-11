import os
import httpx
from azure.identity import DefaultAzureCredential
from src.config import get_settings


async def setup_knowledge_base() -> str:
    """
    Creates the Foundry IQ knowledge base for ComplianceIQ via Azure AI Search REST API.
    Configures knowledge sources and enables agentic retrieval.
    """
    settings = get_settings()
    if settings.mock_mode:
        print(
            f"✅ Mock Mode: Simulated creation of knowledge base '{settings.foundry_iq_knowledge_base_name}'"
        )
        return settings.foundry_iq_knowledge_base_name

    credential = DefaultAzureCredential()
    token = credential.get_token("https://search.azure.com/.default")

    endpoint = settings.azure_search_endpoint.rstrip("/")
    api_version = "2026-05-01-preview"
    kb_name = settings.foundry_iq_knowledge_base_name

    url = f"{endpoint}/knowledgebases/{kb_name}?api-version={api_version}"

    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json",
    }

    # Optional: if using an API key instead of token
    if settings.azure_search_api_key:
        headers = {
            "api-key": settings.azure_search_api_key,
            "Content-Type": "application/json",
        }

    payload = {
        "name": kb_name,
        "description": "EU AI Act, NIST AI RMF, ISO 42001 regulatory knowledge base for ComplianceIQ",
        "retrievalMode": "agentic",
        "reasoningEffort": "medium",
        "knowledgeSources": [
            {
                "name": "eu-ai-act",
                "type": "azureblob",
                "description": "Complete EU AI Act regulation text (Regulation 2024/1689)",
            },
            {
                "name": "nist-ai-rmf",
                "type": "azureblob",
                "description": "NIST AI Risk Management Framework 1.0",
            },
            {
                "name": "iso-42001",
                "type": "azureblob",
                "description": "ISO/IEC 42001:2023 AI Management System standard",
            },
            {
                "name": "eu-enforcement-live",
                "type": "web",
                "urls": [
                    "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai"
                ],
                "description": "Latest EU AI Act enforcement guidance and updates",
            },
        ],
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                url, headers=headers, json=payload, timeout=30.0
            )
            response.raise_for_status()
            print(
                f"✅ Knowledge base '{kb_name}' created successfully with agentic retrieval enabled."
            )
            return kb_name
        except httpx.HTTPStatusError as e:
            print(
                f"❌ Failed to create knowledge base. Status code: {e.response.status_code}"
            )
            print(f"Response: {e.response.text}")
            raise
