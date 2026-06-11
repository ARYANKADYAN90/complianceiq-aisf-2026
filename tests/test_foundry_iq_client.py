import pytest
from src.tools.foundry_iq_client import FoundryIQClient


@pytest.mark.asyncio
async def test_mock_query_returns_citations():
    client = FoundryIQClient(mock_mode=True)
    res = await client.query("test")
    assert "citations" in res
    assert len(res["citations"]) > 0


@pytest.mark.asyncio
async def test_mock_classify_risk_returns_high_for_cv_system():
    client = FoundryIQClient(mock_mode=True)
    res = await client.classify_eu_risk_tier({"system_name": "CV"})
    assert res["risk_tier"] == "HIGH RISK"


@pytest.mark.asyncio
async def test_mock_check_requirement_returns_valid_structure():
    client = FoundryIQClient(mock_mode=True)
    res = await client.check_requirement_compliance("Article 9", {})
    assert "compliant" in res


@pytest.mark.asyncio
async def test_mock_verify_claim_returns_bool():
    client = FoundryIQClient(mock_mode=True)
    res = await client.verify_claim("claim", "Article")
    assert isinstance(res["verified"], bool)


@pytest.mark.asyncio
async def test_mock_get_remediation_returns_steps():
    client = FoundryIQClient(mock_mode=True)
    res = await client.get_remediation_steps("gap", "Article")
    assert "steps" in res
