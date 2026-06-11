import asyncio
from datetime import datetime, timezone
import logging
from src.models.gap_matrix import (
    GapMatrix,
    ComplianceGap,
    ComplianceStatus,
    GapSeverity,
)
from src.models.system_profile import SystemProfile
from src.tools.foundry_iq_client import FoundryIQClient
from src.mock.mock_data import MOCK_GAP_MATRIX
from src.config import get_settings

logger = logging.getLogger(__name__)

REQUIREMENTS_TO_CHECK = [
    {
        "id": "ART_09",
        "name": "Risk Management System",
        "article": "Article 9",
        "description": "Provider must establish documented risk management system for entire lifecycle",
        "evidence_needed": [
            "Risk register",
            "Risk management procedure",
            "Residual risk assessment",
        ],
    },
    {
        "id": "ART_10",
        "name": "Data and Data Governance",
        "article": "Article 10",
        "description": "Training/validation data must meet quality criteria, free from bias",
        "evidence_needed": [
            "Data quality assessment",
            "Bias testing results",
            "Data governance policy",
        ],
    },
    {
        "id": "ART_11",
        "name": "Technical Documentation",
        "article": "Article 11 + Annex IV",
        "description": "Technical documentation must be drawn up before placing on market",
        "evidence_needed": [
            "Annex IV documentation",
            "System card",
            "Architecture documentation",
        ],
    },
    {
        "id": "ART_12",
        "name": "Record-keeping and Logging",
        "article": "Article 12",
        "description": "Automatic logging capabilities throughout the lifecycle",
        "evidence_needed": [
            "Audit logs",
            "Event logging system",
            "Log retention policy",
        ],
    },
    {
        "id": "ART_13",
        "name": "Transparency and Information",
        "article": "Article 13",
        "description": "Information to deployers must be clear, complete, and accurate",
        "evidence_needed": [
            "User-facing documentation",
            "Instructions for use",
            "Capability limitations disclosure",
        ],
    },
    {
        "id": "ART_14",
        "name": "Human Oversight",
        "article": "Article 14",
        "description": "Humans must be able to understand, monitor, and override the AI system",
        "evidence_needed": [
            "Human review mechanism",
            "Override procedure",
            "Oversight protocol",
        ],
    },
    {
        "id": "ART_15",
        "name": "Accuracy, Robustness, Cybersecurity",
        "article": "Article 15",
        "description": "Appropriate accuracy, robustness, cybersecurity throughout lifecycle",
        "evidence_needed": [
            "Accuracy benchmarks",
            "Robustness testing",
            "Security assessment",
        ],
    },
    {
        "id": "ART_17",
        "name": "Quality Management System",
        "article": "Article 17",
        "description": "Providers must put quality management system in place",
        "evidence_needed": [
            "QMS documentation",
            "Version control policy",
            "Change management procedure",
        ],
    },
    {
        "id": "ART_20",
        "name": "Post-market Monitoring",
        "article": "Article 20",
        "description": "Providers must actively monitor performance after deployment",
        "evidence_needed": [
            "Monitoring plan",
            "Incident reporting procedure",
            "Performance metrics dashboard",
        ],
    },
    {
        "id": "ANNEX_IV",
        "name": "Technical Documentation (Annex IV)",
        "article": "Annex IV",
        "description": "8 categories of technical documentation required",
        "evidence_needed": [
            "System description",
            "Design specifications",
            "Monitoring metrics",
            "Training methodology",
            "Validation results",
            "Post-deploy monitoring plan",
            "Standards applied",
            "Conformity declaration",
        ],
    },
]


class GapAnalyzerAgent:
    """
    Agent 2: Checks AI system profile against EU AI Act requirements using Foundry IQ.
    """

    def __init__(self, mock_mode: bool = None):
        self.settings = get_settings()
        self.mock_mode = mock_mode if mock_mode is not None else self.settings.mock_mode
        self.foundry_iq = FoundryIQClient(mock_mode=self.mock_mode)
        self.requirements = REQUIREMENTS_TO_CHECK

    async def _check_single_requirement(
        self, requirement: dict, system_profile: SystemProfile
    ) -> ComplianceGap:
        """Check one requirement against the system profile using Foundry IQ."""
        result = await self.foundry_iq.check_requirement_compliance(
            requirement=requirement["description"],
            system_profile=system_profile.model_dump(),
        )

        if result["compliant"]:
            status = ComplianceStatus.COMPLIANT
        elif result["partial"]:
            status = ComplianceStatus.PARTIAL
        else:
            status = ComplianceStatus.NON_COMPLIANT

        req_id = requirement["id"]

        # Determine severity based on EU AI Act specifics
        if req_id == "ART_14":
            severity = GapSeverity.CRITICAL
        elif req_id in ["ART_09", "ART_11", "ANNEX_IV"]:
            if status == ComplianceStatus.NON_COMPLIANT:
                severity = GapSeverity.CRITICAL
            elif status == ComplianceStatus.PARTIAL:
                severity = GapSeverity.HIGH
            else:
                severity = GapSeverity.LOW
        elif req_id in ["ART_10", "ART_12", "ART_13", "ART_15"]:
            if status == ComplianceStatus.NON_COMPLIANT:
                severity = GapSeverity.HIGH
            elif status == ComplianceStatus.PARTIAL:
                severity = GapSeverity.MEDIUM
            else:
                severity = GapSeverity.LOW
        else:
            if status == ComplianceStatus.NON_COMPLIANT:
                severity = GapSeverity.MEDIUM
            else:
                severity = GapSeverity.LOW

        missing_evidence = []
        if status != ComplianceStatus.COMPLIANT:
            # We would normally extract this from the result,
            # here we use the predefined list as a baseline for gaps
            missing_evidence = requirement["evidence_needed"]

        description_text = (
            " ".join(result["gaps"]) if result["gaps"] else requirement["description"]
        )

        return ComplianceGap(
            requirement_id=req_id,
            requirement_name=requirement["name"],
            article_reference=requirement["article"],
            status=status,
            severity=severity,
            description=description_text,
            missing_evidence=missing_evidence,
            remediation_hint=f"Review {requirement['article']} and ensure documentation.",
            citations=result["citations"],
            confidence_score=result.get("confidence", 0.9),
        )

    async def analyze(self, system_profile: SystemProfile) -> GapMatrix:
        """Run all 10 requirement checks in parallel via Foundry IQ."""
        if self.mock_mode:
            # Reconstruct model from dict
            matrix_dict = MOCK_GAP_MATRIX.copy()
            matrix_dict["analysis_timestamp"] = datetime.now(timezone.utc)
            matrix_dict["system_profile"] = system_profile.model_dump()
            return GapMatrix(**matrix_dict)

        # Run all checks concurrently
        tasks = [
            self._check_single_requirement(req, system_profile)
            for req in self.requirements
        ]
        gaps = await asyncio.gather(*tasks, return_exceptions=True)

        valid_gaps = []
        for i, gap in enumerate(gaps):
            if isinstance(gap, Exception):
                logger.error(
                    f"Failed to check requirement {self.requirements[i]['id']}: {str(gap)}"
                )
                # Create a fallback gap instead of crashing the pipeline
                valid_gaps.append(
                    ComplianceGap(
                        requirement_id=self.requirements[i]["id"],
                        requirement_name=self.requirements[i]["name"],
                        article_reference=self.requirements[i]["article"],
                        status=ComplianceStatus.NON_COMPLIANT,
                        severity=GapSeverity.HIGH,
                        description=f"Analysis failed: {str(gap)}",
                        missing_evidence=[],
                        remediation_hint="Manual review required due to analysis failure.",
                        citations=[],
                        confidence_score=0.0,
                    )
                )
            else:
                valid_gaps.append(gap)

        return GapMatrix(
            gaps=valid_gaps,
            system_profile=system_profile,
            analysis_timestamp=datetime.now(timezone.utc),
        )

    async def get_high_priority_gaps(
        self, gap_matrix: GapMatrix
    ) -> list[ComplianceGap]:
        """Returns only CRITICAL and HIGH severity NON_COMPLIANT gaps, sorted by severity."""
        high_priority = [
            gap
            for gap in gap_matrix.gaps
            if gap.status == ComplianceStatus.NON_COMPLIANT
            and gap.severity in [GapSeverity.CRITICAL, GapSeverity.HIGH]
        ]

        # Sort: CRITICAL first, then HIGH
        def severity_sort_key(gap: ComplianceGap) -> int:
            return 0 if gap.severity == GapSeverity.CRITICAL else 1

        return sorted(high_priority, key=severity_sort_key)
