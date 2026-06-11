from typing import Literal
from pydantic import BaseModel, Field


class SystemProfile(BaseModel):
    """Profile of an AI system extracted from its documentation."""

    use_case: str = Field(
        description="What the AI system does and its primary purpose"
    )  # noqa: E501
    system_name: str = Field(description="Name of the AI system")
    vendor_or_developer: str = Field(
        description="Entity that developed or vends the system"
    )
    deployment_environment: Literal["production", "staging", "testing", "research"] = (
        Field(description="Current deployment environment")
    )
    decision_type: Literal["automated", "human_in_loop", "advisory", "monitoring"] = (
        Field(description="Type of decision making the AI employs")
    )
    affected_users: list[str] = Field(
        description="Categories of affected users (e.g., employees, customers, citizens, patients)"  # noqa: E501
    )
    data_types_processed: list[str] = Field(
        description="Types of data processed (e.g., personal_data, biometric, health, financial)"  # noqa: E501
    )
    autonomy_level: Literal[
        "full_autonomy", "high_autonomy", "partial_autonomy", "human_supervised"
    ] = Field(description="Level of system autonomy")
    human_oversight: bool = Field(
        description="Whether human oversight mechanisms are in place"
    )
    right_to_explanation: bool = Field(
        description="Whether a right to explanation is provided to users"
    )
    geographic_scope: list[str] = Field(
        description="Regions where the system operates (e.g., EU, US, global)"
    )
    documentation_completeness: float = Field(
        ge=0.0,
        le=1.0,
        description="Estimated completeness of provided documentation from 0.0 to 1.0",
    )
    raw_text: str = Field(description="Raw text extracted from uploaded documentation")
    extraction_confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score of the extraction from 0.0 to 1.0",  # noqa: E501
    )

    @classmethod
    def example_data(cls) -> "SystemProfile":
        """Returns realistic test data for the model."""
        return cls(
            use_case="Automated resume screening and candidate ranking",
            system_name="TalentAI Pro",
            vendor_or_developer="HR Tech Solutions Corp",
            deployment_environment="production",
            decision_type="human_in_loop",
            affected_users=["candidates", "employees", "recruiters"],
            data_types_processed=[
                "personal_data",
                "educational",
                "professional_history",
            ],
            autonomy_level="high_autonomy",
            human_oversight=True,
            right_to_explanation=False,
            geographic_scope=["EU", "US"],
            documentation_completeness=0.85,
            raw_text="The system processes candidate resumes to rank them based on job descriptions...",  # noqa: E501
            extraction_confidence=0.92,
        )
