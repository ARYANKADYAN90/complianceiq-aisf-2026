from enum import Enum
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, computed_field


class RemediationPriority(str, Enum):
    IMMEDIATE = "IMMEDIATE"
    THIRTY_DAYS = "THIRTY_DAYS"
    SIXTY_DAYS = "SIXTY_DAYS"
    NINETY_DAYS = "NINETY_DAYS"


class RemediationItem(BaseModel):
    """An actionable step to remediate a compliance gap."""

    item_id: str = Field(description="Unique identifier for the remediation action")
    gap_reference: str = Field(
        description="Reference to the requirement_id of the gap"
    )  # noqa: E501
    action_title: str = Field(description="Short title of the remediation action")
    action_description: str = Field(
        description="Detailed description of what needs to be done"
    )
    owner_role: str = Field(
        description="Suggested role to own this action (e.g., Engineering, Legal, Product)"  # noqa: E501
    )
    effort_days: int = Field(description="Estimated effort in days")
    priority: RemediationPriority = Field(
        description="Priority timeline for the action"
    )
    article_reference: str = Field(description="Related EU AI Act article")
    citation: str = Field(
        description="Foundry IQ citation supporting this recommendation"
    )
    success_criteria: str = Field(
        description="Criteria to consider this action successfully completed"
    )
    dependencies: List[str] = Field(
        description="List of item_ids this action depends on"
    )

    @classmethod
    def example_data(cls) -> "RemediationItem":
        return cls(
            item_id="REM-001",
            gap_reference="REQ-ART14-01",
            action_title="Implement Human Override Protocol",
            action_description="Develop a UI feature allowing recruiters to override AI rankings before decisions are final.",  # noqa: E501
            owner_role="Engineering",
            effort_days=10,
            priority=RemediationPriority.IMMEDIATE,
            article_reference="Article 14",
            citation="Foundry IQ: Article 14(4)(a) mandates human intervention capability.",  # noqa: E501
            success_criteria="Override button is functional and logs the human decision.",  # noqa: E501
            dependencies=[],
        )


class RemediationPlan(BaseModel):
    """Comprehensive remediation roadmap."""

    items: List[RemediationItem] = Field(
        description="All remediation actions required"
    )  # noqa: E501
    created_at: datetime = Field(description="When the plan was created")

    @computed_field
    @property
    def immediate_actions(self) -> List[RemediationItem]:
        return [
            item
            for item in self.items
            if item.priority == RemediationPriority.IMMEDIATE
        ]

    @computed_field
    @property
    def thirty_day_actions(self) -> List[RemediationItem]:
        return [
            item
            for item in self.items
            if item.priority == RemediationPriority.THIRTY_DAYS
        ]

    @computed_field
    @property
    def sixty_day_actions(self) -> List[RemediationItem]:
        return [
            item
            for item in self.items
            if item.priority == RemediationPriority.SIXTY_DAYS
        ]

    @computed_field
    @property
    def ninety_day_actions(self) -> List[RemediationItem]:
        return [
            item
            for item in self.items
            if item.priority == RemediationPriority.NINETY_DAYS
        ]

    @computed_field
    @property
    def total_effort_days(self) -> int:
        return sum(item.effort_days for item in self.items)

    @classmethod
    def example_data(cls) -> "RemediationPlan":
        return cls(
            items=[RemediationItem.example_data()],
            created_at=datetime.now(timezone.utc),
        )
