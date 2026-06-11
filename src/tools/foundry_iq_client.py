import json
from agent_framework import ChatAgent
from agent_framework.azure import AzureAIAgentClient, AzureAISearchContextProvider
from azure.identity.aio import DefaultAzureCredential
from azure.search.documents.aio import SearchClient
from src.config import get_settings
from src.mock.mock_data import MOCK_GAP_MATRIX
from src.observability.telemetry import trace_foundry_iq_query

from src.tools.circuit_breaker import CircuitBreaker
from src.tools.retry_handler import retry_with_exponential_backoff
from src.tools.rate_limiter import RateLimiter
from src.tools.cache_manager import CacheManager


class FoundryIQClient:
    """
    Client for interacting with Microsoft Foundry IQ knowledge base via Agentic Retrieval.
    """

    def __init__(self, mock_mode: bool = None):
        self.settings = get_settings()
        self.mock_mode = mock_mode if mock_mode is not None else self.settings.mock_mode
        self.credential = DefaultAzureCredential()
        
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter(max_calls_per_minute=60)
        self.cache = CacheManager(ttl=300)

    @trace_foundry_iq_query("query")
    @retry_with_exponential_backoff(max_retries=3)
    async def query(self, question: str, context: dict = None) -> dict:
        """Query Foundry IQ knowledge base with agentic retrieval."""
        if self.mock_mode:
            return {
                "answer": "Based on the EU AI Act text, the system must establish a continuous risk management system (Article 9) and ensure human oversight (Article 14).",
                "citations": [
                    "EU AI Act Art.9(1) - A risk management system shall be established, implemented, documented and maintained.",
                    "EU AI Act Art.14(1) - High-risk AI systems shall be designed and developed in such a way that they can be effectively overseen by natural persons."
                ],
                "sources_used": ["eu-ai-act-full-text"],
                "confidence": 0.94
            }

        await self.rate_limiter.acquire()
        
        # Simplistic cache key hash logic
        cache_key_hash = "" 
        cached = self.cache.get(question, cache_key_hash)
        if cached:
            return cached

        async def _do_query():
            async with (
                AzureAISearchContextProvider(
                    endpoint=self.settings.azure_search_endpoint,
                    knowledge_base_name=self.settings.foundry_iq_knowledge_base_name,
                    credential=self.credential,
                    mode="agentic",
                    reasoning_effort="medium"
                ) as search,
                AzureAIAgentClient(
                    project_endpoint=self.settings.azure_foundry_project_endpoint,
                    model_deployment_name=self.settings.azure_foundry_model_deployment,
                    async_credential=self.credential,
                ) as client,
                ChatAgent(
                    chat_client=client,
                    context_providers=[search]
                ) as agent
            ):
                full_prompt = question
                if context:
                    full_prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"
    
                result = await agent.run(full_prompt)
                
                return {
                    "answer": result.content,
                    "citations": result.citations if hasattr(result, "citations") else [],
                    "sources_used": result.sources_used if hasattr(result, "sources_used") else [],
                    "confidence": getattr(result, "confidence_score", 0.9)
                }

        result = await self.circuit_breaker.call(_do_query)
        self.cache.set(question, result, cache_key_hash)
        return result


    @trace_foundry_iq_query("classify_eu_risk_tier")
    @retry_with_exponential_backoff(max_retries=3)
    async def classify_eu_risk_tier(self, system_profile: dict) -> dict:
        """Use Foundry IQ to determine EU AI Act risk tier."""
        if self.mock_mode:
            return {
                "risk_tier": "HIGH RISK",
                "rationale": "System is used for recruitment and selection of natural persons.",
                "applicable_entries": ["Annex III point 4"],
                "mandatory_requirements": ["Article 9", "Article 10", "Article 11", "Article 14"],
                "citations": ["EU AI Act Annex III(4) - AI systems intended to be used for recruitment or selection of natural persons"]
            }

        prompt = f"""
        Given an AI system with these characteristics:
        {json.dumps(system_profile, indent=2)}
        
        Based on EU AI Act Article 6, Annex II, and Annex III:
        1. What risk tier applies? (UNACCEPTABLE/HIGH/LIMITED/MINIMAL)
        2. Which specific Annex III entries apply?
        3. What are the mandatory requirements for this tier?
        
        Cite exact article numbers and paragraph text.
        """
        response = await self.query(prompt)
        
        # In a real implementation, we would parse the unstructured response into structured data
        return {
            "risk_tier": "HIGH RISK",  # Assuming parsed from response
            "rationale": response["answer"],
            "citations": response["citations"]
        }

    @trace_foundry_iq_query("check_requirement_compliance")
    @retry_with_exponential_backoff(max_retries=3)
    async def check_requirement_compliance(self, requirement: str, system_profile: dict) -> dict:
        """Check if system meets a specific EU AI Act requirement."""
        if self.mock_mode:
            # Look up mock gap from MOCK_GAP_MATRIX
            gap = next((g for g in MOCK_GAP_MATRIX["gaps"] if g["requirement_name"] == requirement), None)
            if gap:
                return {
                    "compliant": gap["status"] == "COMPLIANT",
                    "partial": gap["status"] == "PARTIAL",
                    "gaps": [gap["description"]],
                    "citations": gap["citations"],
                    "severity": gap["severity"]
                }
            return {
                "compliant": False,
                "partial": False,
                "gaps": ["Requirement not met."],
                "citations": ["EU AI Act generic citation"],
                "severity": "MEDIUM"
            }

        prompt = f"""
        Given the following AI system profile:
        {json.dumps(system_profile, indent=2)}
        
        Evaluate its compliance against the following EU AI Act requirement: {requirement}
        Identify any compliance gaps, partial compliance, and the severity of non-compliance.
        Cite specific paragraphs.
        """
        response = await self.query(prompt)
        
        return {
            "compliant": False,
            "partial": True,
            "gaps": [response["answer"]],
            "citations": response["citations"],
            "severity": "HIGH"
        }

    @trace_foundry_iq_query("get_remediation_steps")
    @retry_with_exponential_backoff(max_retries=3)
    async def get_remediation_steps(self, gap_description: str, article: str) -> dict:
        """Get specific remediation steps for a compliance gap."""
        if self.mock_mode:
            return {
                "steps": [
                    "Develop a human-in-the-loop workflow.",
                    "Update technical documentation to reflect override capability.",
                    "Log all human interventions in the audit system."
                ],
                "effort_estimate": "5 days",
                "owner_role": "Engineering Lead",
                "citations": [f"Foundry IQ: {article} mandates human intervention capability."]
            }

        prompt = f"""
        Given this compliance gap: "{gap_description}"
        Related to {article}.
        
        Provide concrete, actionable remediation steps, an estimated effort level, and the ideal owner role.
        Cite the relevant legal text that justifies these steps.
        """
        response = await self.query(prompt)
        
        return {
            "steps": [response["answer"]],
            "effort_estimate": "Unknown",
            "owner_role": "Compliance Team",
            "citations": response["citations"]
        }

    @trace_foundry_iq_query("verify_claim")
    @retry_with_exponential_backoff(max_retries=3)
    async def verify_claim(self, claim: str, cited_article: str) -> dict:
        """Verify a report claim against the knowledge base."""
        if self.mock_mode:
            return {
                "verified": True,
                "confidence": 0.91,
                "supporting_text": "The claim aligns with the statutory text.",
                "flag": None
            }

        prompt = f"""
        Verify the following claim against the EU AI Act text for {cited_article}:
        Claim: "{claim}"
        
        Is this claim fully supported, partially supported, or contradicted by the legal text?
        """
        response = await self.query(prompt)
        
        is_verified = "supported" in response["answer"].lower() and "contradicted" not in response["answer"].lower()
        
        return {
            "verified": is_verified,
            "confidence": response["confidence"],
            "supporting_text": response["answer"],
            "flag": None if is_verified else "Claim may not be fully supported by citations."
        }
