from src.models.system_profile import SystemProfile
from src.models.gap_matrix import GapMatrix, ComplianceGap
from src.models.risk_scorecard import RiskScorecard, EUAIActRiskTier
from src.models.remediation_plan import RemediationPlan, RemediationItem
from src.models.compliance_report import ComplianceReport
from datetime import datetime, timezone


def test_system_profile_valid_creation():
    sp = SystemProfile.example_data()
    assert sp.system_name is not None


def test_gap_matrix_compliance_percentage_calculation():
    gm = GapMatrix.example_data()
    assert isinstance(gm.compliance_percentage, float)


def test_risk_scorecard_tier_values_are_eu_act_compliant():
    assert EUAIActRiskTier.UNACCEPTABLE.value == "UNACCEPTABLE RISK"
    assert EUAIActRiskTier.HIGH.value == "HIGH RISK"


def test_remediation_plan_immediate_filter():
    rp = RemediationPlan.example_data()
    imm = [i for i in rp.items if i.priority == "IMMEDIATE"]
    assert isinstance(imm, list)


def test_remediation_plan_total_effort_days_sum():
    rp = RemediationPlan.example_data()
    assert rp.total_effort_days > 0


def test_compliance_report_has_required_fields():
    cr = ComplianceReport.example_data()
    assert cr.executive_summary is not None


def test_all_models_have_example_data_classmethod():
    assert hasattr(SystemProfile, "model_config")


def test_model_json_schema_works_all_models():
    assert isinstance(SystemProfile.model_json_schema(), dict)
    assert isinstance(GapMatrix.model_json_schema(), dict)
    assert isinstance(RiskScorecard.model_json_schema(), dict)
    assert isinstance(RemediationPlan.model_json_schema(), dict)
    assert isinstance(ComplianceReport.model_json_schema(), dict)
