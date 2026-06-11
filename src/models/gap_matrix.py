from enum import Enum
from typing import List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, computed_field
from src.models.system_profile import SystemProfile


class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    PARTIAL = "PARTIAL"
    NON_COMPLIANT = "NON_COMPLIANT"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class GapSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ComplianceGap(BaseModel):
    """A specific compliance gap identified against EU AI Act requirements."""

    requirement_id: str = Field(description="Identifier of the requirement")
    requirement_name: str = Field(description="Name of the compliance requirement")
    article_reference: str = Field(
        description="EU AI Act article reference (e.g., Article 14)"
    )
    status: ComplianceStatus = Field(
        description="Compliance status of this requirement"
    )
    severity: GapSeverity = Field(
        description="Severity of the gap if not fully compliant"
    )
    description: str = Field(
        description="Description of the requirement and the finding"
    )
    missing_evidence: List[str] = Field(
        description="List of missing evidence or documentation"
    )
    remediation_hint: str = Field(
        description="High-level hint on how to remediate the gap"
    )
    citations: List[str] = Field(
        description="Specific Foundry IQ citations supporting this finding"
    )
    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Confidence of this finding (0.0 to 1.0)"
    )

    @classmethod
    def example_data(cls) -> "ComplianceGap":
        return cls(
            requirement_id="REQ-ART14-01",
            requirement_name="Human Oversight",
            article_reference="Article 14",
            status=ComplianceStatus.NON_COMPLIANT,
            severity=GapSeverity.CRITICAL,
            description="System lacks sufficient technical measures to ensure human oversight.",
            missing_evidence=[
                "Human-in-the-loop validation logs",
                "Oversight protocol documentation",
            ],
            remediation_hint="Implement an override interface for human reviewers before final decisions.",
            citations=["Regulation 2024/1689 Article 14(4)(a)"],
            confidence_score=0.95,
        )


class GapMatrix(BaseModel):
    """Matrix of all compliance gaps identified for an AI system."""

    gaps: List[ComplianceGap] = Field(description="List of identified compliance gaps")
    system_profile: SystemProfile = Field(
        description="The system profile being analyzed"
    )
    analysis_timestamp: datetime = Field(description="When the analysis was performed")

    @computed_field
    @property
    def total_gaps(self) -> int:
        return len(self.gaps)

    @computed_field
    @property
    def critical_gaps(self) -> int:
        return sum(
            1
            for gap in self.gaps
            if gap.severity == GapSeverity.CRITICAL
            and gap.status != ComplianceStatus.COMPLIANT
        )

    @computed_field
    @property
    def high_gaps(self) -> int:
        return sum(
            1
            for gap in self.gaps
            if gap.severity == GapSeverity.HIGH
            and gap.status != ComplianceStatus.COMPLIANT
        )

    @computed_field
    @property
    def compliance_percentage(self) -> float:
        if not self.gaps:
            return 100.0
        applicable_gaps = [
            g for g in self.gaps if g.status != ComplianceStatus.NOT_APPLICABLE
        ]
        if not applicable_gaps:
            return 100.0
        compliant_gaps = sum(
            1 for g in applicable_gaps if g.status == ComplianceStatus.COMPLIANT
        )
        return round((compliant_gaps / len(applicable_gaps)) * 100, 2)

    @classmethod
    def example_data(cls) -> "GapMatrix":
        return cls(
            gaps=[ComplianceGap.example_data()],
            system_profile=SystemProfile.example_data(),
            analysis_timestamp=datetime.now(timezone.utc),
        )
