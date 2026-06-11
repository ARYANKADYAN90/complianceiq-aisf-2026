from enum import Enum
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class EUAIActRiskTier(str, Enum):
    UNACCEPTABLE = "UNACCEPTABLE RISK"
    HIGH = "HIGH RISK"
    LIMITED = "LIMITED RISK"
    MINIMAL = "MINIMAL RISK"


class RiskFinding(BaseModel):
    """A specific finding related to risk classification criteria."""
    
    criterion: str = Field(description="The risk criterion being evaluated")
    met: bool = Field(description="Whether the criterion is met")
    evidence: str = Field(description="Evidence supporting this finding")
    article_reference: str = Field(description="EU AI Act article reference")

    @classmethod
    def example_data(cls) -> "RiskFinding":
        return cls(
            criterion="Biometric categorization of natural persons",
            met=False,
            evidence="System documentation states it only processes text data.",
            article_reference="Article 5(1)(c)"
        )


class RiskScorecard(BaseModel):
    """Overall risk scorecard for an AI system based on EU AI Act."""
    
    risk_tier: EUAIActRiskTier = Field(description="Overall EU AI Act risk tier")
    compliance_percentage: float = Field(description="Overall compliance percentage")
    critical_count: int = Field(description="Number of critical severity gaps")
    high_count: int = Field(description="Number of high severity gaps")
    medium_count: int = Field(description="Number of medium severity gaps")
    low_count: int = Field(description="Number of low severity gaps")
    total_citations: int = Field(description="Total number of Foundry IQ citations used")
    risk_findings: List[RiskFinding] = Field(description="Findings justifying the risk tier")
    classification_rationale: str = Field(description="Detailed rationale for the risk classification")
    applicable_articles: List[str] = Field(description="List of applicable EU AI Act articles")
    scored_at: datetime = Field(description="When the scoring was performed")

    @classmethod
    def example_data(cls) -> "RiskScorecard":
        return cls(
            risk_tier=EUAIActRiskTier.HIGH,
            compliance_percentage=47.5,
            critical_count=2,
            high_count=5,
            medium_count=3,
            low_count=2,
            total_citations=14,
            risk_findings=[RiskFinding.example_data()],
            classification_rationale="The system is classified as High Risk because it is used for employment and recruitment (Annex III, point 4).",
            applicable_articles=["Article 6", "Article 14", "Annex III(4)"],
            scored_at=datetime.now(timezone.utc),
        )
