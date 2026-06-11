import pytest
import time
from unittest.mock import Mock
from src.agents.orchestrator import ComplianceIQOrchestrator
from src.models.risk_scorecard import EUAIActRiskTier


@pytest.mark.asyncio
async def test_mock_pipeline_completes_successfully(sample_pdf_bytes):
    orchestrator = ComplianceIQOrchestrator(mock_mode=True)
    fake_file = Mock()
    fake_file.name = "test.pdf"
    fake_file.read.return_value = sample_pdf_bytes

    result = await orchestrator.run([fake_file])
    assert result["pipeline_complete"] is True


@pytest.mark.asyncio
async def test_mock_pipeline_returns_all_required_keys():
    orchestrator = ComplianceIQOrchestrator(mock_mode=True)
    result = await orchestrator.run([])

    required_keys = [
        "system_profile",
        "gap_matrix",
        "scorecard",
        "remediation_roadmap",
        "reports",
        "pipeline_complete",
        "mock_mode",
    ]
    for key in required_keys:
        assert key in result


@pytest.mark.asyncio
async def test_mock_pipeline_under_2_seconds():
    start_time = time.time()
    orchestrator = ComplianceIQOrchestrator(mock_mode=True)
    await orchestrator.run([])
    duration = time.time() - start_time

    # Mock mode should be completely local and very fast
    assert duration < 2.0


@pytest.mark.asyncio
async def test_progress_callback_called_6_times():
    orchestrator = ComplianceIQOrchestrator(mock_mode=True)

    callback_calls = []

    def callback(name, status, output=None):
        if "complete" in status:
            callback_calls.append(name)

    await orchestrator.run([], progress_callback=callback)

    # We expect 6 agents to complete
    assert len(callback_calls) == 6


@pytest.mark.asyncio
async def test_pipeline_handles_empty_files_gracefully():
    orchestrator = ComplianceIQOrchestrator(mock_mode=True)
    # In mock mode, it shouldn't crash even with no files
    result = await orchestrator.run([])
    assert result["pipeline_complete"] is True


@pytest.mark.asyncio
async def test_pipeline_output_has_correct_risk_tier_for_cv_screening():
    orchestrator = ComplianceIQOrchestrator(mock_mode=True)
    result = await orchestrator.run([])

    # CV screening is HIGH RISK
    assert result["scorecard"]["risk_tier"] == EUAIActRiskTier.HIGH.value
