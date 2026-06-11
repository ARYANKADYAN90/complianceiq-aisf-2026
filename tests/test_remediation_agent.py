import pytest
from datetime import datetime, timezone
from src.agents.remediation_agent import RemediationAgent
from src.models.gap_matrix import (
    GapMatrix,
    ComplianceGap,
    ComplianceStatus,
    GapSeverity,
)
from src.models.risk_scorecard import RiskScorecard, EUAIActRiskTier
from src.models.remediation_plan import (
    RemediationPlan,
    RemediationPriority,
    RemediationItem,
)


@pytest.fixture
def agent():
    return RemediationAgent(mock_mode=False)


@pytest.mark.asyncio
async def test_generate_item_priority_logic(agent):
    """Test priority determination based on severity and risk tier."""
    gap_critical = ComplianceGap(
        requirement_id="ART_14",
        requirement_name="Oversight",
        article_reference="Art 14",
        status=ComplianceStatus.NON_COMPLIANT,
        severity=GapSeverity.CRITICAL,
        description="test",
        missing_evidence=[],
        remediation_hint="",
        citations=[],
        confidence_score=0.9,
    )

    # Critical + High Risk = IMMEDIATE
    items = await agent._generate_item_for_gap(gap_critical, EUAIActRiskTier.HIGH)
    assert items[0].priority == RemediationPriority.IMMEDIATE

    # Critical + Limited Risk = THIRTY_DAYS
    items = await agent._generate_item_for_gap(gap_critical, EUAIActRiskTier.LIMITED)
    assert items[0].priority == RemediationPriority.THIRTY_DAYS

    gap_medium = ComplianceGap(
        requirement_id="ART_10",
        requirement_name="Data",
        article_reference="Art 10",
        status=ComplianceStatus.NON_COMPLIANT,
        severity=GapSeverity.MEDIUM,
        description="test",
        missing_evidence=[],
        remediation_hint="",
        citations=[],
        confidence_score=0.9,
    )

    # Medium = SIXTY_DAYS
    items = await agent._generate_item_for_gap(gap_medium, EUAIActRiskTier.HIGH)
    assert items[0].priority == RemediationPriority.SIXTY_DAYS


@pytest.mark.asyncio
async def test_plan_mock_mode():
    """Verify plan uses mock data when in mock mode."""
    mock_agent = RemediationAgent(mock_mode=True)
    plan = await mock_agent.plan(GapMatrix.example_data(), RiskScorecard.example_data())

    assert isinstance(plan, RemediationPlan)
    assert len(plan.items) == 10
    assert (
        plan.immediate_actions[0].action_title == "Implement human oversight mechanism"
    )


def test_format_roadmap_summary(agent):
    """Test string formatting of the roadmap summary."""
    plan = RemediationPlan(
        items=[
            RemediationItem(
                item_id="REM-001",
                gap_reference="1",
                action_title="Urgent fix",
                action_description="x",
                owner_role="CTO",
                effort_days=5,
                priority=RemediationPriority.IMMEDIATE,
                article_reference="Art 1",
                citation="",
                success_criteria="",
                dependencies=[],
            ),
            RemediationItem(
                item_id="REM-002",
                gap_reference="1",
                action_title="Later fix",
                action_description="x",
                owner_role="Dev",
                effort_days=10,
                priority=RemediationPriority.THIRTY_DAYS,
                article_reference="Art 1",
                citation="",
                success_criteria="",
                dependencies=[],
            ),
        ],
        created_at=datetime.now(timezone.utc),
    )

    summary = agent.format_roadmap_summary(plan)
    assert "IMMEDIATE ACTIONS (1 items, 5 total days):" in summary
    assert "- [CTO] Urgent fix (5 days)" in summary
    assert "30-DAY ACTIONS (1 items, 10 total days):" in summary
    assert "Total estimated effort: 15 days" in summary
