import asyncio
from src.mock.mock_data import (
    MOCK_SYSTEM_PROFILE,
    MOCK_GAP_MATRIX,
    MOCK_RISK_SCORECARD,
    MOCK_REMEDIATION_PLAN,
    MOCK_REPORTS
)

class MockPipeline:
    """
    Mock Data Engine for ComplianceIQ.
    Ensures 100% reliable demo execution without relying on live Azure credentials.
    Simulates the agent pipeline with delays for a realistic UI experience.
    """

    async def run(self, uploaded_files: list, progress_callback=None) -> dict:
        """
        Run the mock pipeline with simulated agent execution delays.
        """
        # Agent 1
        if progress_callback:
            progress_callback("Scanner Agent", "running", None)
        await asyncio.sleep(0.3)
        if progress_callback:
            progress_callback("Scanner Agent", "complete", MOCK_SYSTEM_PROFILE)

        # Agent 2
        if progress_callback:
            progress_callback("Gap Analyzer (Foundry IQ)", "running", None)
        await asyncio.sleep(0.3)
        if progress_callback:
            progress_callback("Gap Analyzer (Foundry IQ)", "complete", MOCK_GAP_MATRIX)

        # Agent 3
        if progress_callback:
            progress_callback("Risk Scorer", "running", None)
        await asyncio.sleep(0.3)
        if progress_callback:
            progress_callback("Risk Scorer", "complete", MOCK_RISK_SCORECARD)

        # Agent 4
        if progress_callback:
            progress_callback("Remediation Planner (Foundry IQ)", "running", None)
        await asyncio.sleep(0.3)
        if progress_callback:
            progress_callback("Remediation Planner (Foundry IQ)", "complete", MOCK_REMEDIATION_PLAN)

        # Agent 5
        if progress_callback:
            progress_callback("Report Generator", "running", None)
        await asyncio.sleep(0.3)
        if progress_callback:
            progress_callback("Report Generator", "complete", MOCK_REPORTS)

        # Agent 6
        if progress_callback:
            progress_callback("Verification Agent", "running", None)
        await asyncio.sleep(0.3)
        if progress_callback:
            progress_callback("Verification Agent", "complete", MOCK_REPORTS)

        return {
            "system_profile": MOCK_SYSTEM_PROFILE,
            "gap_matrix": MOCK_GAP_MATRIX,
            "scorecard": MOCK_RISK_SCORECARD,
            "remediation_roadmap": MOCK_REMEDIATION_PLAN,
            "reports": MOCK_REPORTS,
            "pipeline_complete": True
        }

    def run_instant(self) -> dict:
        """
        Run the mock pipeline instantly without any delays for rapid testing.
        """
        return {
            "system_profile": MOCK_SYSTEM_PROFILE,
            "gap_matrix": MOCK_GAP_MATRIX,
            "scorecard": MOCK_RISK_SCORECARD,
            "remediation_roadmap": MOCK_REMEDIATION_PLAN,
            "reports": MOCK_REPORTS,
            "pipeline_complete": True
        }
