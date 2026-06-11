from datetime import datetime, timezone
import logging
from src.models.system_profile import SystemProfile
from src.models.gap_matrix import (
    GapMatrix,
    ComplianceStatus,
    GapSeverity,
)
from src.models.risk_scorecard import RiskScorecard, EUAIActRiskTier, RiskFinding
from src.mock.mock_data import MOCK_RISK_SCORECARD
from src.config import get_settings

logger = logging.getLogger(__name__)

EU_AI_ACT_ANNEX_III_HIGH_RISK = {
    "employment_hiring": {
        "keywords": [
            "cv",
            "resume",
            "hiring",
            "recruitment",
            "job application",
            "candidate",
            "employment",
            "workforce",
        ],
        "article": "Annex III, point 4",
        "description": "AI used for recruitment or selection of natural persons",
    },
    "education_vocational": {
        "keywords": [
            "student",
            "exam",
            "assessment",
            "grading",
            "education",
            "learning",
            "academic",
            "score",
            "test",
        ],
        "article": "Annex III, point 3",
        "description": "AI used to determine access to educational institutions",
    },
    "biometric_identification": {
        "keywords": [
            "face",
            "facial",
            "fingerprint",
            "biometric",
            "iris",
            "voice recognition",
            "identification",
        ],
        "article": "Annex III, point 1",
        "description": "Real-time remote biometric identification systems",
    },
    "critical_infrastructure": {
        "keywords": [
            "energy",
            "water",
            "gas",
            "electricity",
            "transport",
            "infrastructure",
            "safety component",
        ],
        "article": "Annex III, point 2",
        "description": "AI as safety component of critical infrastructure",
    },
    "law_enforcement": {
        "keywords": [
            "police",
            "criminal",
            "suspect",
            "surveillance",
            "law enforcement",
            "court",
            "judicial",
        ],
        "article": "Annex III, point 6",
        "description": "AI used by law enforcement",
    },
    "healthcare": {
        "keywords": [
            "medical",
            "health",
            "diagnosis",
            "patient",
            "clinical",
            "disease",
            "treatment",
            "hospital",
            "doctor",
        ],
        "article": "Annex III, point 5b",
        "description": "AI as medical device",
    },
    "credit_scoring": {
        "keywords": [
            "credit",
            "loan",
            "insurance",
            "financial",
            "bank",
            "mortgage",
            "creditworthiness",
        ],
        "article": "Annex III, point 5a",
        "description": "AI to evaluate creditworthiness",
    },
    "public_services": {
        "keywords": [
            "welfare",
            "benefits",
            "social security",
            "public service",
            "government",
            "asylum",
            "border",
        ],
        "article": "Annex III, point 5",
        "description": "AI in essential public services",
    },
}

UNACCEPTABLE_RISK_PATTERNS = [
    "social scoring",
    "social credit",
    "subliminal manipulation",
    "exploit vulnerabilities",
    "real-time remote biometric in public spaces",
]


class RiskScorerAgent:
    """
    Agent 3: Applies EU AI Act risk classification rules programmatically.
    Does NOT rely on Foundry IQ — applies deterministic logic based on Annex III.
    """

    def __init__(self, mock_mode: bool = None):
        self.settings = get_settings()
        self.mock_mode = mock_mode if mock_mode is not None else self.settings.mock_mode  # noqa: E501

    def _classify_risk_tier(
        self, system_profile: SystemProfile
    ) -> tuple[EUAIActRiskTier, list[RiskFinding], list[str]]:
        """
        Deterministic risk classification using Annex III rules.
        Returns: (tier, findings, applicable_articles)
        """
        use_case_lower = system_profile.use_case.lower()
        findings = []
        applicable_articles = []

        # 1. Check UNACCEPTABLE risk patterns
        for pattern in UNACCEPTABLE_RISK_PATTERNS:
            if pattern in use_case_lower:
                findings.append(
                    RiskFinding(
                        criterion="Prohibited AI Practices (Article 5)",
                        met=True,
                        evidence=f"Use case contains prohibited pattern: '{pattern}'",
                        article_reference="Article 5",
                    )
                )
                applicable_articles.append("Article 5")
                return EUAIActRiskTier.UNACCEPTABLE, findings, applicable_articles

        # 2. Check Annex III HIGH RISK domains by keyword matching
        is_high_risk = False
        for domain, data in EU_AI_ACT_ANNEX_III_HIGH_RISK.items():
            for keyword in data["keywords"]:
                if keyword in use_case_lower:
                    is_high_risk = True
                    findings.append(
                        RiskFinding(
                            criterion=data["description"],
                            met=True,
                            evidence=f"Use case matches High Risk domain '{domain}' via keyword '{keyword}'.",  # noqa: E501
                            article_reference=data["article"],
                        )
                    )
                    if data["article"] not in applicable_articles:
                        applicable_articles.append(data["article"])
                    break  # Skip other keywords for this domain if matched

        # Also check data_types and autonomy for stronger signals
        data_types_str = " ".join(system_profile.data_types_processed).lower()
        if "biometric" in data_types_str or "health" in data_types_str:
            is_high_risk = True
            findings.append(
                RiskFinding(
                    criterion="Processing of sensitive biometric/health data",
                    met=True,
                    evidence="System processes biometric or health data.",
                    article_reference="Article 6",
                )
            )
            if "Article 6" not in applicable_articles:
                applicable_articles.append("Article 6")

        if not system_profile.human_oversight and system_profile.autonomy_level in [
            "full_autonomy",
            "high_autonomy",
        ]:
            if is_high_risk:
                findings.append(
                    RiskFinding(
                        criterion="High autonomy without human oversight in high-risk domain",  # noqa: E501
                        met=True,
                        evidence="System operates with high autonomy and no human oversight.",  # noqa: E501
                        article_reference="Article 14",
                    )
                )
                if "Article 14" not in applicable_articles:
                    applicable_articles.append("Article 14")

        if is_high_risk:
            # If High Risk, basic requirements apply
            for art in ["Article 9", "Article 11", "Article 13"]:
                if art not in applicable_articles:
                    applicable_articles.append(art)
            return EUAIActRiskTier.HIGH, findings, applicable_articles

        # 3. Check for LIMITED RISK indicators
        if "chatbot" in use_case_lower or "conversational" in use_case_lower:
            findings.append(
                RiskFinding(
                    criterion="AI system intended to interact with natural persons",
                    met=True,
                    evidence="System is a chatbot or conversational AI.",
                    article_reference="Article 52",
                )
            )
            applicable_articles.append("Article 52")
            return EUAIActRiskTier.LIMITED, findings, applicable_articles

        if "deepfake" in use_case_lower or "generate image" in use_case_lower:
            findings.append(
                RiskFinding(
                    criterion="AI system that generates or manipulates image, audio or video content",  # noqa: E501
                    met=True,
                    evidence="System generates content (deepfake/generative).",
                    article_reference="Article 52",
                )
            )
            applicable_articles.append("Article 52")
            return EUAIActRiskTier.LIMITED, findings, applicable_articles

        # Default
        return EUAIActRiskTier.MINIMAL, findings, applicable_articles

    def _calculate_compliance_percentage(self, gap_matrix: GapMatrix) -> float:
        """
        Weighted compliance calculation.
        COMPLIANT = 1.0, PARTIAL = 0.5, NON_COMPLIANT = 0.0, NOT_APPLICABLE = excluded
        Critical gaps have 2x weight.
        Returns 0.0-100.0
        """
        applicable_gaps = [
            g for g in gap_matrix.gaps if g.status != ComplianceStatus.NOT_APPLICABLE
        ]
        if not applicable_gaps:
            return 100.0

        total_weight = 0.0
        earned_score = 0.0

        for gap in applicable_gaps:
            weight = 2.0 if gap.severity == GapSeverity.CRITICAL else 1.0
            total_weight += weight

            if gap.status == ComplianceStatus.COMPLIANT:
                earned_score += 1.0 * weight
            elif gap.status == ComplianceStatus.PARTIAL:
                earned_score += 0.5 * weight
            elif gap.status == ComplianceStatus.NON_COMPLIANT:
                earned_score += 0.0 * weight

        return round((earned_score / total_weight) * 100, 2)

    async def score(self, gap_matrix: GapMatrix) -> RiskScorecard:
        """Main entry point."""
        if self.mock_mode:
            scorecard_dict = MOCK_RISK_SCORECARD.copy()
            scorecard_dict["scored_at"] = datetime.now(timezone.utc)
            return RiskScorecard(**scorecard_dict)

        profile = gap_matrix.system_profile
        tier, findings, articles = self._classify_risk_tier(profile)
        compliance_pct = self._calculate_compliance_percentage(gap_matrix)

        critical_count = sum(
            1
            for g in gap_matrix.gaps
            if g.severity == GapSeverity.CRITICAL
            and g.status == ComplianceStatus.NON_COMPLIANT
        )
        high_count = sum(
            1
            for g in gap_matrix.gaps
            if g.severity == GapSeverity.HIGH
            and g.status == ComplianceStatus.NON_COMPLIANT
        )
        medium_count = sum(
            1
            for g in gap_matrix.gaps
            if g.severity == GapSeverity.MEDIUM
            and g.status == ComplianceStatus.NON_COMPLIANT
        )
        low_count = sum(
            1
            for g in gap_matrix.gaps
            if g.severity == GapSeverity.LOW
            and g.status == ComplianceStatus.NON_COMPLIANT
        )

        total_citations = sum(len(g.citations) for g in gap_matrix.gaps)

        rationale = f"System classified as {tier.value} under EU AI Act. "
        rationale += f"Primary classification trigger: {findings[0].criterion if findings else 'General assessment'}. "  # noqa: E501
        rationale += f"Applicable mandatory requirements: {', '.join(articles)}."

        return RiskScorecard(
            risk_tier=tier,
            compliance_percentage=compliance_pct,
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            total_citations=total_citations,
            risk_findings=findings,
            classification_rationale=rationale,
            applicable_articles=articles,
            scored_at=datetime.now(timezone.utc),
        )
