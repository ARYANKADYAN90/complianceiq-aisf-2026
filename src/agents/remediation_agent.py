import asyncio
from datetime import datetime, timezone
import logging
from src.models.gap_matrix import (
    GapMatrix,
    ComplianceGap,
    ComplianceStatus,
    GapSeverity,
)
from src.models.risk_scorecard import RiskScorecard, EUAIActRiskTier
from src.models.remediation_plan import (
    RemediationPlan,
    RemediationItem,
    RemediationPriority,
)
from src.tools.foundry_iq_client import FoundryIQClient
from src.mock.mock_data import MOCK_REMEDIATION_PLAN
from src.config import get_settings

logger = logging.getLogger(__name__)

REMEDIATION_TEMPLATES = {
    "ART_09": {
        "default_actions": [
            "Establish continuous risk management system",
            "Document identified risks and mitigations",
        ],
        "typical_owner_roles": "Compliance Officer",
        "typical_effort_days": 10,
        "article_reference": "Article 9",
    },
    "ART_10": {
        "default_actions": [
            "Implement bias testing protocols",
            "Document data provenance and governance",
        ],
        "typical_owner_roles": "ML Engineer",
        "typical_effort_days": 7,
        "article_reference": "Article 10",
    },
    "ART_11": {
        "default_actions": [
            "Draft complete technical documentation prior to market placement"
        ],
        "typical_owner_roles": "Technical Writer",
        "typical_effort_days": 15,
        "article_reference": "Article 11",
    },
    "ART_12": {
        "default_actions": [
            "Implement automated event logging mechanism",
            "Set up secure log retention",
        ],
        "typical_owner_roles": "DevOps",
        "typical_effort_days": 5,
        "article_reference": "Article 12",
    },
    "ART_13": {
        "default_actions": [
            "Draft comprehensive instructions for users",
            "Add transparency disclosures",
        ],
        "typical_owner_roles": "Product Manager",
        "typical_effort_days": 5,
        "article_reference": "Article 13",
    },
    "ART_14": {
        "default_actions": [
            "Implement human-in-the-loop override interface",
            "Halt fully automated critical decisions",
        ],
        "typical_owner_roles": "Engineering Lead",
        "typical_effort_days": 8,
        "article_reference": "Article 14",
    },
    "ART_15": {
        "default_actions": [
            "Conduct robustness and adversarial testing",
            "Establish accuracy benchmarks",
        ],
        "typical_owner_roles": "QA Engineer",
        "typical_effort_days": 10,
        "article_reference": "Article 15",
    },
    "ART_17": {
        "default_actions": ["Establish formal Quality Management System (QMS)"],
        "typical_owner_roles": "Quality Manager",
        "typical_effort_days": 15,
        "article_reference": "Article 17",
    },
    "ART_20": {
        "default_actions": [
            "Develop post-market monitoring plan",
            "Create incident reporting dashboard",
        ],
        "typical_owner_roles": "Product Manager",
        "typical_effort_days": 12,
        "article_reference": "Article 20",
    },
    "ANNEX_IV": {
        "default_actions": [
            "Provide detailed system architecture diagrams",
            "Document training methodology",
        ],
        "typical_owner_roles": "Technical Writer",
        "typical_effort_days": 15,
        "article_reference": "Annex IV",
    },
}


class RemediationAgent:
    """
    Agent 4: Builds a comprehensive remediation plan.
    """

    def __init__(self, mock_mode: bool = None):
        self.settings = get_settings()
        self.mock_mode = mock_mode if mock_mode is not None else self.settings.mock_mode  # noqa: E501
        self.foundry_iq = FoundryIQClient(mock_mode=self.mock_mode)

    async def _generate_item_for_gap(
        self, gap: ComplianceGap, risk_tier: EUAIActRiskTier
    ) -> list[RemediationItem]:
        """Generate remediation items for one gap using Foundry IQ."""
        template = REMEDIATION_TEMPLATES.get(
            gap.requirement_id,
            {
                "default_actions": ["Address compliance gap"],
                "typical_owner_roles": "Compliance Team",
                "typical_effort_days": 5,
                "article_reference": gap.article_reference,
            },
        )

        actions = template["default_actions"]
        effort = template["typical_effort_days"]
        owner = template["typical_owner_roles"]
        citation = gap.article_reference

        if not self.mock_mode:
            try:
                foundry_result = await self.foundry_iq.get_remediation_steps(
                    gap_description=gap.description, article=gap.article_reference
                )
                if foundry_result.get("steps"):
                    actions = foundry_result["steps"]
                if foundry_result.get("citations"):
                    citation = foundry_result["citations"][0]
            except Exception as e:
                logger.error(f"Failed to enrich remediation from Foundry IQ: {e}")

        # Determine priority
        priority = RemediationPriority.NINETY_DAYS
        if gap.severity == GapSeverity.CRITICAL:
            if risk_tier in [EUAIActRiskTier.HIGH, EUAIActRiskTier.UNACCEPTABLE]:
                priority = RemediationPriority.IMMEDIATE
            else:
                priority = RemediationPriority.THIRTY_DAYS
        elif gap.severity == GapSeverity.HIGH:
            if risk_tier in [EUAIActRiskTier.HIGH, EUAIActRiskTier.UNACCEPTABLE]:
                priority = RemediationPriority.THIRTY_DAYS
            else:
                priority = RemediationPriority.SIXTY_DAYS
        elif gap.severity == GapSeverity.MEDIUM:
            priority = RemediationPriority.SIXTY_DAYS
        elif gap.severity == GapSeverity.LOW:
            priority = RemediationPriority.NINETY_DAYS

        items = []
        for i, action in enumerate(actions):
            items.append(
                RemediationItem(
                    item_id="",  # Assigned later
                    gap_reference=gap.requirement_id,
                    action_title=f"{action[:50]}...",
                    action_description=action,
                    owner_role=owner,
                    effort_days=max(1, effort // len(actions)),
                    priority=priority,
                    article_reference=template["article_reference"],
                    citation=citation,
                    success_criteria=f"Compliance with {template['article_reference']} validated.",  # noqa: E501
                    dependencies=[],
                )
            )

        return items

    async def plan(
        self, gap_matrix: GapMatrix, scorecard: RiskScorecard
    ) -> RemediationPlan:
        """Build full remediation plan from all gaps in the scorecard."""
        if self.mock_mode:
            plan_dict = MOCK_REMEDIATION_PLAN.copy()
            plan_dict["created_at"] = datetime.now(timezone.utc)
            return RemediationPlan(**plan_dict)

        actionable_gaps = [
            g for g in gap_matrix.gaps if g.status != ComplianceStatus.COMPLIANT
        ]

        # Generate items in parallel
        all_items_nested = await asyncio.gather(
            *[
                self._generate_item_for_gap(gap, scorecard.risk_tier)
                for gap in actionable_gaps
            ]
        )

        all_items = [item for sublist in all_items_nested for item in sublist]

        # Sort by priority (IMMEDIATE first)
        priority_order = [
            RemediationPriority.IMMEDIATE,
            RemediationPriority.THIRTY_DAYS,
            RemediationPriority.SIXTY_DAYS,
            RemediationPriority.NINETY_DAYS,
        ]
        all_items.sort(key=lambda x: priority_order.index(x.priority))

        # Assign unique item_ids
        for i, item in enumerate(all_items):
            item.item_id = f"REM-{i+1:03d}"

        return RemediationPlan(items=all_items, created_at=datetime.now(timezone.utc))

    def format_roadmap_summary(self, plan: RemediationPlan) -> str:
        """Returns a formatted text summary of the roadmap."""
        immediate = plan.immediate_actions
        thirty = plan.thirty_day_actions
        sixty = plan.sixty_day_actions
        ninety = plan.ninety_day_actions

        def _format_section(title: str, items: list) -> str:
            if not items:
                return f"{title} (0 items)\n- None required."

            total_days = sum(item.effort_days for item in items)
            lines = [f"{title} ({len(items)} items, {total_days} total days):"]
            for item in items:
                lines.append(
                    f"- [{item.owner_role}] {item.action_title} ({item.effort_days} days)"  # noqa: E501
                )
            return "\n".join(lines)

        parts = [
            _format_section("IMMEDIATE ACTIONS", immediate),
            _format_section("30-DAY ACTIONS", thirty),
            _format_section("60-DAY ACTIONS", sixty),
            _format_section("90-DAY ACTIONS", ninety),
            f"\nTotal estimated effort: {plan.total_effort_days} days",
        ]

        return "\n\n".join(parts)
