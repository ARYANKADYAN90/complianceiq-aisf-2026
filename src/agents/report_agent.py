import asyncio
from datetime import datetime, timezone
import logging
from src.models.compliance_report import ComplianceReport, ReportSection
from src.models.system_profile import SystemProfile
from src.models.gap_matrix import GapMatrix, ComplianceStatus, GapSeverity
from src.models.risk_scorecard import RiskScorecard
from src.models.remediation_plan import RemediationPlan
from src.mock.mock_data import MOCK_REPORTS
from src.config import get_settings
from azure.identity.aio import DefaultAzureCredential
from agent_framework.azure import AzureAIAgentClient
from agent_framework import ChatAgent

logger = logging.getLogger(__name__)


class ReportAgent:
    """
    Agent 5: Generates final compliance reports tailored to different stakeholders.
    """

    def __init__(self, mock_mode: bool = None):
        self.settings = get_settings()
        self.mock_mode = mock_mode if mock_mode is not None else self.settings.mock_mode  # noqa: E501

    async def _call_llm(self, prompt: str) -> str:
        """Helper to call LLM for report generation."""
        credential = DefaultAzureCredential()
        try:
            async with (
                AzureAIAgentClient(
                    project_endpoint=self.settings.azure_foundry_project_endpoint,
                    model_deployment_name=self.settings.azure_foundry_model_deployment,
                    async_credential=credential,
                ) as client,
                ChatAgent(chat_client=client) as agent,
            ):
                result = await agent.run(prompt)
                return result.content.strip()
        except Exception as e:
            logger.error(f"Failed to generate report section: {e}")
            return f"Error generating section: {str(e)}"
        finally:
            await credential.close()

    async def _generate_executive_summary(
        self,
        system_profile: SystemProfile,
        gap_matrix: GapMatrix,
        scorecard: RiskScorecard,
        roadmap: RemediationPlan,
    ) -> str:
        """500-word board-level report. No jargon. Clear language."""
        if self.mock_mode:
            return MOCK_REPORTS["executive_summary"]

        critical_gaps_text = "\n".join(
            [
                f"- {g.requirement_name}: {g.description}"
                for g in gap_matrix.gaps
                if g.severity == GapSeverity.CRITICAL
            ]
        )
        if not critical_gaps_text:
            critical_gaps_text = "None identified."

        immediate_actions_text = "\n".join(
            [
                f"- {a.action_title} (Owner: {a.owner_role}, Effort: {a.effort_days} days)"  # noqa: E501
                for a in roadmap.immediate_actions
            ]
        )
        if not immediate_actions_text:
            immediate_actions_text = "None required."

        prompt = f"""
Write a 500-word executive summary for non-technical stakeholders (Board members, Legal, Executives).  # noqa: E501

System: {system_profile.system_name}
Risk Tier: {scorecard.risk_tier.value} (EU AI Act classification)
Compliance Score: {scorecard.compliance_percentage}%
Critical Gaps: {scorecard.critical_count}

Top critical issues:
{critical_gaps_text}

Key remediation actions:
{immediate_actions_text}

RULES FOR THIS REPORT:
- Use plain English, no technical jargon
- Explain what EU AI Act means in business terms
- State the financial risk: fines up to €35M or 7% of global annual revenue for non-compliance  # noqa: E501
- Be factual and professional
- End with a clear recommendation
- Do NOT make up facts — only use the data provided
"""
        return await self._call_llm(prompt)

    async def _generate_technical_report(
        self,
        system_profile: SystemProfile,
        gap_matrix: GapMatrix,
        scorecard: RiskScorecard,
        roadmap: RemediationPlan,
    ) -> str:
        """800-word engineering report with exact article references."""
        if self.mock_mode:
            return MOCK_REPORTS["technical_report"]

        gaps_details = ""
        for g in gap_matrix.gaps:
            if g.status != ComplianceStatus.COMPLIANT:
                gaps_details += f"Requirement: {g.requirement_name} ({g.article_reference})\nSeverity: {g.severity.value}\nIssue: {g.description}\n\n"  # noqa: E501

        prompt = f"""
Write an 800-word technical compliance engineering report based on the EU AI Act assessment.  # noqa: E501

System: {system_profile.system_name}
Technical Gaps Identified:
{gaps_details}

RULES FOR THIS REPORT:
- Target audience: CTOs, ML engineers, software architects
- Include exact Article numbers for every requirement
- Provide specific technical fixes (not vague suggestions)
- Include code, architecture, or CI/CD pipeline requirements needed to fix the gaps
- Cite Foundry IQ sources inline as [Article X, §Y] where applicable
- Structure with headings for: Data Governance, Model Testing, Logging, Monitoring, and Oversight Mechanisms  # noqa: E501
- Do NOT make up gaps not listed above. Only elaborate technically on the provided gaps.  # noqa: E501
"""
        return await self._call_llm(prompt)

    async def _generate_certificate_draft(
        self,
        system_profile: SystemProfile,
        scorecard: RiskScorecard,
        roadmap: RemediationPlan,
    ) -> str:
        """Formal compliance certificate template — ready to present."""
        if self.mock_mode:
            return MOCK_REPORTS["certificate_draft"]

        total_gaps = len(
            [g for g in scorecard.risk_findings if g.met]
        )  # wait, finding is just finding.
        total_gaps = len([g for g in scorecard.applicable_articles])  # we use gaps

        # Proper gap counts
        actionable_gaps = len([g for g in roadmap.items])

        status_text = (
            "Compliant"
            if scorecard.compliance_percentage == 100.0
            else "Remediation Plan Established — Not Yet Compliant"
        )

        applicable_articles_str = ", ".join(scorecard.applicable_articles)

        template = f"""COMPLIANCE ASSESSMENT CERTIFICATE
EU AI Act (Regulation 2024/1689)

System Name: {system_profile.system_name}
Developer/Provider: {system_profile.vendor_or_developer}
Assessment Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
Assessor: ComplianceIQ Multi-Agent System v1.0

RISK CLASSIFICATION: {scorecard.risk_tier.value}
BASIS: {applicable_articles_str}

COMPLIANCE STATUS: {scorecard.compliance_percentage}% compliant

GAPS IDENTIFIED: {actionable_gaps} ({scorecard.critical_count} critical, {scorecard.high_count} high priority)  # noqa: E501

REMEDIATION TIMELINE: {roadmap.total_effort_days} working days

STATUS: {status_text}

This certificate documents the results of an automated compliance assessment. It should be reviewed by qualified legal counsel before submission to any regulatory authority.  # noqa: E501

Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
Pipeline: Scanner → Gap Analyzer (Foundry IQ) → Risk Scorer → Remediation Planner → Report Generator → Verification  # noqa: E501
"""
        return template

    async def generate(
        self,
        system_profile: SystemProfile,
        gap_matrix: GapMatrix,
        scorecard: RiskScorecard,
        roadmap: RemediationPlan,
    ) -> ComplianceReport:
        """Generate all three reports."""
        if self.mock_mode:
            report_dict = MOCK_REPORTS.copy()
            report_dict["generated_at"] = datetime.now(timezone.utc)
            return ComplianceReport(**report_dict)

        # Generate in parallel
        executive, technical, certificate = await asyncio.gather(
            self._generate_executive_summary(
                system_profile, gap_matrix, scorecard, roadmap
            ),
            self._generate_technical_report(
                system_profile, gap_matrix, scorecard, roadmap
            ),
            self._generate_certificate_draft(system_profile, scorecard, roadmap),
        )

        # Count Foundry IQ citations across all gaps
        total_citations = sum(len(g.citations) for g in gap_matrix.gaps)

        # Extract sections if needed, or leave empty as it's not strictly specified
        sections = [
            ReportSection(title="Executive Summary", content=executive, citations=[]),
            ReportSection(title="Technical Findings", content=technical, citations=[]),
        ]

        return ComplianceReport(
            system_name=system_profile.system_name,
            executive_summary=executive,
            technical_findings=technical,
            certificate_draft=certificate,
            sections=sections,
            risk_tier=scorecard.risk_tier.value,
            compliance_percentage=scorecard.compliance_percentage,
            critical_gaps_count=scorecard.critical_count,
            generated_at=datetime.now(timezone.utc),
            foundry_iq_citations_count=total_citations,
            is_verified=False,  # Set to True after verification agent
        )
