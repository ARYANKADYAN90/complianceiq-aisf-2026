import pytest
from src.agents.risk_scorer_agent import RiskScorerAgent
from src.models.system_profile import SystemProfile
from src.models.gap_matrix import GapMatrix


@pytest.fixture
def scorer():
    return RiskScorerAgent(mock_mode=True)


@pytest.fixture
def empty_gap_matrix():
    return GapMatrix.example_data()


@pytest.mark.asyncio
async def test_cv_screening_is_high_risk(scorer, empty_gap_matrix):
    sp = SystemProfile.example_data()
    sp.use_case = "CV screening"
    res = await scorer.score(sp, empty_gap_matrix)
    assert res.risk_tier.value == "HIGH RISK"


@pytest.mark.asyncio
async def test_medical_ai_is_high_risk(scorer, empty_gap_matrix):
    sp = SystemProfile.example_data()
    sp.use_case = "medical diagnosis"
    res = await scorer.score(sp, empty_gap_matrix)
    assert res.risk_tier.value == "HIGH RISK"


@pytest.mark.asyncio
async def test_chatbot_is_limited_risk(scorer, empty_gap_matrix):
    sp = SystemProfile.example_data()
    sp.use_case = "customer service chatbot"
    res = await scorer.score(sp, empty_gap_matrix)
    assert res.risk_tier.value == "LIMITED RISK"


@pytest.mark.asyncio
async def test_weather_app_is_minimal_risk(scorer, empty_gap_matrix):
    sp = SystemProfile.example_data()
    sp.use_case = "weather forecasting"
    res = await scorer.score(sp, empty_gap_matrix)
    assert res.risk_tier.value == "MINIMAL RISK"


@pytest.mark.asyncio
async def test_compliance_percentage_all_compliant_is_100(scorer):
    sp = SystemProfile.example_data()
    gm = GapMatrix.example_data()
    for gap in gm.gaps:
        gap.status = "COMPLIANT"
    res = await scorer.score(sp, gm)
    assert res.compliance_percentage == 100.0
