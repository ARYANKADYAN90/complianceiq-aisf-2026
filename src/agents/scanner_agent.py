import io
import json
import asyncio
import logging
from typing import List, Any
from PyPDF2 import PdfReader
from docx import Document
from src.models.system_profile import SystemProfile
from src.mock.mock_data import MOCK_SYSTEM_PROFILE
from src.config import get_settings
from azure.identity.aio import DefaultAzureCredential
from agent_framework.azure import AzureAIAgentClient
from agent_framework import ChatAgent

logger = logging.getLogger(__name__)


class ScannerAgent:
    """
    Agent 1: Extracts text from uploaded files and uses an LLM to generate
    a structured SystemProfile describing the AI system.
    """

    SUPPORTED_FORMATS = [".pdf", ".docx", ".txt", ".json", ".md"]

    def __init__(self, mock_mode: bool = None):
        self.settings = get_settings()
        self.mock_mode = mock_mode if mock_mode is not None else self.settings.mock_mode  # noqa: E501

    async def extract_text(self, file_bytes: bytes, filename: str) -> str:
        """Extract raw text from any supported file format."""
        ext = filename[filename.rfind(".") :].lower() if "." in filename else ""

        if not file_bytes:
            logger.warning(f"File {filename} is empty.")
            return ""

        try:
            if ext == ".pdf":
                reader = PdfReader(io.BytesIO(file_bytes))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                return text.strip()

            elif ext == ".docx":
                doc = Document(io.BytesIO(file_bytes))
                text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
                return text.strip()

            elif ext in [".txt", ".md"]:
                return file_bytes.decode("utf-8", errors="replace").strip()

            elif ext == ".json":
                try:
                    data = json.loads(file_bytes.decode("utf-8"))
                    return json.dumps(data, indent=2)
                except json.JSONDecodeError:
                    return file_bytes.decode("utf-8", errors="replace").strip()

            else:
                logger.warning(f"Unsupported format {ext} for file {filename}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {str(e)}")
            return ""

    async def extract_system_profile(self, raw_text: str) -> dict:
        """Use LLM to extract structured SystemProfile from raw text."""
        if self.mock_mode:
            return MOCK_SYSTEM_PROFILE

        prompt = f"""
You are an AI system compliance analyst. Extract structured 
information from this AI system documentation.

Documentation:
{raw_text}

Extract EXACTLY these fields as JSON:
- use_case: what the AI system does (1-2 sentences)
- system_name: name of the system
- vendor_or_developer: company or team that built it
- decision_type: one of [automated, human_in_loop, advisory, monitoring]
- affected_users: list of user categories affected
- data_types_processed: list of data types (personal_data, biometric, health, financial, employment, behavioral, location, other)  # noqa: E501
- autonomy_level: one of [full_autonomy, high_autonomy, partial_autonomy, human_supervised]  # noqa: E501
- human_oversight: true/false — is there a human review step?
- right_to_explanation: true/false — can users request explanation?
- geographic_scope: list of regions (EU, US, UK, global, etc.)
- documentation_completeness: 0.0 to 1.0 based on how complete the docs are

Return ONLY valid JSON. No explanation text. No markdown fences.
"""
        credential = DefaultAzureCredential()
        try:
            async with (
                AzureAIAgentClient(
                    project_endpoint=self.settings.azure_foundry_project_endpoint,
                    model_deployment_name=self.settings.azure_foundry_model_deployment,
                    async_credential=credential,
                ) as client,
                ChatAgent(chat_client=client) as agent,
            ):
                result = await agent.run(prompt)
                content = result.content.strip()

                # Cleanup potential markdown fences
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]

                data = json.loads(content.strip())
                return data
        finally:
            await credential.close()

    def _estimate_confidence(self, profile: dict) -> float:
        """Estimate confidence of the extraction."""
        score = 0.0
        if profile.get("system_name") and profile["system_name"] != "Unknown":
            score += 0.1
        if profile.get("use_case") and len(profile["use_case"]) > 50:
            score += 0.2
        if profile.get("data_types_processed"):
            score += 0.1
        if profile.get("documentation_completeness", 0.0) > 0.5:
            score += 0.2
        if "human_oversight" in profile:
            score += 0.2
        if profile.get("geographic_scope") and "EU" in profile["geographic_scope"]:
            score += 0.2

        return min(score, 1.0)

    async def scan(self, files: List[Any]) -> SystemProfile:
        """Main entry point. Scans all uploaded files, returns SystemProfile."""
        if self.mock_mode:
            return SystemProfile(**MOCK_SYSTEM_PROFILE)

        if not files:
            raise ValueError("No files uploaded")

        # Extract text from all files in parallel
        # files is a list of Streamlit UploadedFile-like objects (has .name and .read())  # noqa: E501
        tasks = []
        for file in files:
            # handle both async and sync reads, assuming sync for memory objects like streamlit  # noqa: E501
            file_bytes = file.read()
            if asyncio.iscoroutine(file_bytes):
                file_bytes = await file_bytes
            tasks.append(self.extract_text(file_bytes, file.name))

        extracted_texts = await asyncio.gather(*tasks)

        # Combine text
        combined_text = "\n\n".join(text for text in extracted_texts if text)
        if not combined_text.strip():
            raise ValueError("Could not extract text from any provided files")

        # Truncate to 50,000 characters to avoid context limits
        if len(combined_text) > 50000:
            logger.warning("Combined text exceeded 50,000 characters. Truncating.")
            combined_text = combined_text[:50000]

        # Extract profile dict
        profile_dict = await self.extract_system_profile(combined_text)

        # Set raw text and confidence
        profile_dict["raw_text"] = combined_text
        profile_dict["extraction_confidence"] = self._estimate_confidence(profile_dict)

        # Validate with pydantic
        return SystemProfile(**profile_dict)
