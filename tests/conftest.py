import pytest
import os
import io
from datetime import datetime, timezone
from src.config import Config
from src.models.system_profile import SystemProfile
from src.models.gap_matrix import GapMatrix
from src.models.risk_scorecard import RiskScorecard
from src.models.remediation_plan import RemediationPlan
from src.models.compliance_report import ComplianceReport
from src.mock.mock_data import (
    MOCK_SYSTEM_PROFILE, MOCK_GAP_MATRIX, 
    MOCK_RISK_SCORECARD, MOCK_REMEDIATION_PLAN, MOCK_REPORTS
)

@pytest.fixture
def mock_settings():
    return Config(
        mock_mode=True,
        azure_foundry_project_endpoint="https://fake.api.azureml.ms",
        azure_search_endpoint="https://fake.search.windows.net",
        azure_search_api_key="fake-key",
        azure_foundry_model_deployment="gpt-4-mini"
    )

@pytest.fixture
def sample_system_profile():
    return SystemProfile(**MOCK_SYSTEM_PROFILE)

@pytest.fixture
def sample_gap_matrix():
    matrix_data = MOCK_GAP_MATRIX.copy()
    matrix_data["analysis_timestamp"] = datetime.now(timezone.utc)
    return GapMatrix(**matrix_data)

@pytest.fixture
def sample_scorecard():
    scorecard_data = MOCK_RISK_SCORECARD.copy()
    scorecard_data["scored_at"] = datetime.now(timezone.utc)
    return RiskScorecard(**scorecard_data)

@pytest.fixture
def sample_remediation_plan():
    plan_data = MOCK_REMEDIATION_PLAN.copy()
    plan_data["created_at"] = datetime.now(timezone.utc)
    return RemediationPlan(**plan_data)

@pytest.fixture
def sample_reports():
    reports_data = MOCK_REPORTS.copy()
    reports_data["generated_at"] = datetime.now(timezone.utc)
    return ComplianceReport(**reports_data)

@pytest.fixture
def sample_pdf_bytes():
    from PyPDF2 import PdfWriter
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()

@pytest.fixture
def sample_docx_bytes():
    from docx import Document
    doc = Document()
    doc.add_paragraph('Test content')
    output = io.BytesIO()
    doc.save(output)
    return output.getvalue()
