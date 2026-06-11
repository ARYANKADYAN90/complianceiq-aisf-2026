import pytest
from unittest.mock import AsyncMock
from src.agents.gap_analyzer_agent import GapAnalyzerAgent, REQUIREMENTS_TO_CHECK
from src.models.system_profile import SystemProfile
from src.models.gap_matrix import GapMatrix, GapSeverity, ComplianceStatus
from src.mock.mock_data import MOCK_SYSTEM_PROFILE


@pytest.fixture
def agent():
    return GapAnalyzerAgent(mock_mode=False)


@pytest.fixture
def system_profile():
    return SystemProfile(**MOCK_SYSTEM_PROFILE)


@pytest.mark.asyncio
async def test_analyze_mock_mode(system_profile):
    """Test full scan pipeline in mock mode returns valid GapMatrix."""
    mock_agent = GapAnalyzerAgent(mock_mode=True)
    matrix = await mock_agent.analyze(system_profile)

    assert isinstance(matrix, GapMatrix)
    assert len(matrix.gaps) == 10
    assert matrix.system_profile.system_name == "TalentFilter Pro v2.3"
    # Verify critical/high counts work correctly
    assert matrix.critical_gaps == 4


@pytest.mark.asyncio
async def test_check_article_14_critical(agent, system_profile, mocker):
    """Test that Article 14 gap is always evaluated as CRITICAL severity."""
    # Mock foundry response to return non-compliant
    mocker.patch.object(
        agent.foundry_iq,
        "check_requirement_compliance",
        return_value={
            "compliant": False,
            "partial": False,
            "gaps": ["No human oversight"],
            "citations": ["Art 14"],
            "severity": "HIGH",  # The agent should override this to CRITICAL
        },
    )

    req = next(r for r in REQUIREMENTS_TO_CHECK if r["id"] == "ART_14")
    gap = await agent._check_single_requirement(req, system_profile)

    assert gap.status == ComplianceStatus.NON_COMPLIANT
    assert gap.severity == GapSeverity.CRITICAL
    assert gap.requirement_id == "ART_14"


@pytest.mark.asyncio
async def test_parallel_execution(agent, system_profile, mocker):
    """Verify asyncio.gather is used to run checks in parallel."""
    # Mock the individual check method
    mock_check = AsyncMock()
    from src.models.gap_matrix import ComplianceGap
    mock_check.return_value = ComplianceGap(requirement_id='REQ', requirement_name='Req', article_reference='Art', status=ComplianceStatus.COMPLIANT, severity=GapSeverity.LOW, description='', missing_evidence=[], remediation_hint='', citations=[], confidence_score=1.0)
    mocker.patch.object(agent, "_check_single_requirement", mock_check)

    await agent.analyze(system_profile)

    # Should be called exactly len(REQUIREMENTS_TO_CHECK) times
    assert mock_check.call_count == len(REQUIREMENTS_TO_CHECK)


@pytest.mark.asyncio
async def test_failed_check_graceful(agent, system_profile, mocker):
    """Test that one failed Foundry call doesn't crash the entire pipeline."""
    # Create a side effect that raises an exception on the first call, succeeds on others  # noqa: E501
    call_count = 0

    async def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Azure OpenAI timeout")
        return {
            "compliant": True,
            "partial": False,
            "gaps": [],
            "citations": [],
            "severity": "LOW",
        }

    mocker.patch.object(
        agent.foundry_iq, "check_requirement_compliance", side_effect=side_effect
    )

    matrix = await agent.analyze(system_profile)

    # All 10 gaps should still be present
    assert len(matrix.gaps) == 10

    # One gap should have the "Analysis failed" description
    failed_gaps = [
        g
        for g in matrix.gaps
        if "Analysis failed: Azure OpenAI timeout" in g.description
    ]
    assert len(failed_gaps) == 1
    assert failed_gaps[0].status == ComplianceStatus.NON_COMPLIANT
    assert failed_gaps[0].severity == GapSeverity.HIGH
