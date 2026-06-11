from datetime import datetime, timezone

# 1. System Profile
MOCK_SYSTEM_PROFILE = {
    "use_case": "Automated CV screening and candidate ranking for job applications",
    "system_name": "TalentFilter Pro v2.3",
    "vendor_or_developer": "Acme HR Tech Ltd",
    "deployment_environment": "production",
    "decision_type": "automated",
    "affected_users": ["job_applicants", "hr_managers", "hiring_managers"],
    "data_types_processed": [
        "personal_data",
        "biometric_inferred",
        "employment_history",
    ],
    "autonomy_level": "high_autonomy",
    "human_oversight": False,
    "right_to_explanation": False,
    "geographic_scope": ["EU", "UK", "US"],
    "documentation_completeness": 0.35,
    "raw_text": "TalentFilter Pro v2.3 automatically screens job applicant CVs, ranks candidates, and makes hiring shortlists without human review. It processes personal data and employment history...",
    "extraction_confidence": 0.98,
}

# 2. Gap Matrix
MOCK_GAP_MATRIX = {
    "system_profile": MOCK_SYSTEM_PROFILE,
    "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
    "gaps": [
        {
            "requirement_id": "REQ-ART09",
            "requirement_name": "Risk Management System",
            "article_reference": "Article 9",
            "status": "NON_COMPLIANT",
            "severity": "CRITICAL",
            "description": "No documented risk management system for the AI lifecycle.",
            "missing_evidence": [
                "Risk assessment report",
                "Iterative risk mitigation plan",
            ],
            "remediation_hint": "Establish and document a continuous risk management system.",
            "citations": [
                "EU AI Act Art.9(1) - risk management system must be established"
            ],
            "confidence_score": 0.95,
        },
        {
            "requirement_id": "REQ-ART10",
            "requirement_name": "Data Governance",
            "article_reference": "Article 10",
            "status": "PARTIAL",
            "severity": "HIGH",
            "description": "Training datasets exist but lack bias monitoring and documentation.",
            "missing_evidence": ["Data bias assessment", "Data provenance logs"],
            "remediation_hint": "Implement strict data governance protocols and bias testing.",
            "citations": [
                "EU AI Act Art.10(2) - training data quality and bias mitigation"
            ],
            "confidence_score": 0.88,
        },
        {
            "requirement_id": "REQ-ART11",
            "requirement_name": "Technical Documentation",
            "article_reference": "Article 11",
            "status": "NON_COMPLIANT",
            "severity": "CRITICAL",
            "description": "Technical documentation is severely lacking (0.35 completeness).",
            "missing_evidence": [
                "Annex IV compliant documentation",
                "System architecture details",
            ],
            "remediation_hint": "Draft complete technical documentation prior to market placement.",
            "citations": [
                "EU AI Act Art.11(1) - technical documentation must be drawn up"
            ],
            "confidence_score": 0.99,
        },
        {
            "requirement_id": "REQ-ART12",
            "requirement_name": "Record-keeping",
            "article_reference": "Article 12",
            "status": "NON_COMPLIANT",
            "severity": "HIGH",
            "description": "System does not automatically record events over its lifetime.",
            "missing_evidence": ["Automated logging mechanism", "Log retention policy"],
            "remediation_hint": "Implement automated logging for traceability.",
            "citations": ["EU AI Act Art.12(1) - automated record-keeping required"],
            "confidence_score": 0.92,
        },
        {
            "requirement_id": "REQ-ART13",
            "requirement_name": "Transparency",
            "article_reference": "Article 13",
            "status": "NON_COMPLIANT",
            "severity": "HIGH",
            "description": "Users are not provided with clear instructions or right to explanation.",
            "missing_evidence": ["Instructions for use", "Transparency disclosures"],
            "remediation_hint": "Draft comprehensive user instructions and transparency notices.",
            "citations": [
                "EU AI Act Art.13(1) - transparent operation and user instructions"
            ],
            "confidence_score": 0.96,
        },
        {
            "requirement_id": "REQ-ART14",
            "requirement_name": "Human Oversight",
            "article_reference": "Article 14",
            "status": "NON_COMPLIANT",
            "severity": "CRITICAL",
            "description": "No human oversight mechanism. System makes automated hiring decisions.",
            "missing_evidence": ["Human-in-the-loop workflow", "Override interface"],
            "remediation_hint": "Halt automated rejection; require human review before final decisions.",
            "citations": [
                "EU AI Act Art.14(1) - human oversight tools must be built-in"
            ],
            "confidence_score": 0.99,
        },
        {
            "requirement_id": "REQ-ART15",
            "requirement_name": "Accuracy & Robustness",
            "article_reference": "Article 15",
            "status": "PARTIAL",
            "severity": "HIGH",
            "description": "System claims high accuracy but lacks robustness testing against adversarial data.",
            "missing_evidence": [
                "Robustness testing results",
                "Adversarial vulnerability assessment",
            ],
            "remediation_hint": "Conduct adversarial testing and document accuracy metrics.",
            "citations": [
                "EU AI Act Art.15(1) - high level of accuracy, robustness, cybersecurity"
            ],
            "confidence_score": 0.85,
        },
        {
            "requirement_id": "REQ-ART17",
            "requirement_name": "Quality Management",
            "article_reference": "Article 17",
            "status": "NON_COMPLIANT",
            "severity": "MEDIUM",
            "description": "No formal quality management system is established.",
            "missing_evidence": ["QMS manual", "Standard operating procedures"],
            "remediation_hint": "Establish a QMS that ensures compliance with the regulation.",
            "citations": [
                "EU AI Act Art.17(1) - put a quality management system in place"
            ],
            "confidence_score": 0.90,
        },
        {
            "requirement_id": "REQ-ART20",
            "requirement_name": "Post-market Monitoring",
            "article_reference": "Article 20",
            "status": "NON_COMPLIANT",
            "severity": "MEDIUM",
            "description": "No post-market monitoring system exists for continuous evaluation.",
            "missing_evidence": [
                "Post-market monitoring plan",
                "Continuous evaluation logs",
            ],
            "remediation_hint": "Develop a systematic post-market monitoring plan.",
            "citations": [
                "EU AI Act Art.20 - establish a post-market monitoring system"
            ],
            "confidence_score": 0.94,
        },
        {
            "requirement_id": "REQ-ANNEX4",
            "requirement_name": "Annex IV Documentation",
            "article_reference": "Annex IV",
            "status": "NON_COMPLIANT",
            "severity": "CRITICAL",
            "description": "Missing required detailed technical specifications from Annex IV.",
            "missing_evidence": [
                "System architecture diagrams",
                "Algorithmic logic description",
            ],
            "remediation_hint": "Prepare detailed Annex IV compliance documents.",
            "citations": ["EU AI Act Annex IV - technical documentation requirements"],
            "confidence_score": 0.98,
        },
    ],
}

# 3. Risk Scorecard
MOCK_RISK_SCORECARD = {
    "risk_tier": "HIGH RISK",
    "compliance_percentage": 22.0,
    "critical_count": 4,
    "high_count": 4,
    "medium_count": 2,
    "low_count": 0,
    "total_citations": 28,
    "scored_at": datetime.now(timezone.utc).isoformat(),
    "risk_findings": [
        {
            "criterion": "AI system used for recruitment or selection of natural persons",
            "met": True,
            "evidence": "System automatically screens CVs and makes candidate rankings without human review.",
            "article_reference": "Annex III Article 6(2)",
        }
    ],
    "classification_rationale": (
        "Based on the analysis, TalentFilter Pro v2.3 is classified as HIGH RISK under the EU AI Act. "
        "According to Annex III, Article 6(2), AI systems intended to be used for the recruitment or "
        "selection of natural persons, notably for placing targeted job advertisements, analyzing and "
        "filtering job applications, and evaluating candidates in the course of interviews or tests, "
        "are strictly classified as High Risk. Because this system processes personal employment data "
        "with 'high autonomy' to make shortlisting decisions, it triggers stringent compliance requirements."
    ),
    "applicable_articles": [
        "Article 6(2)",
        "Article 9",
        "Article 10",
        "Article 11",
        "Article 12",
        "Article 13",
        "Article 14",
        "Article 15",
        "Article 17",
        "Article 20",
        "Annex III",
        "Annex IV",
    ],
}

# 4. Remediation Plan
MOCK_REMEDIATION_PLAN = {
    "created_at": datetime.now(timezone.utc).isoformat(),
    "items": [
        {
            "item_id": "REM-001",
            "gap_reference": "REQ-ART14",
            "action_title": "Implement human oversight mechanism",
            "action_description": "Develop and deploy a human-in-the-loop workflow. The AI must only provide recommendations; a human must sign off.",
            "owner_role": "CTO",
            "effort_days": 5,
            "priority": "IMMEDIATE",
            "article_reference": "Article 14",
            "citation": "EU AI Act Art.14(1)",
            "success_criteria": "System blocks final hiring decisions until human approval is logged.",
            "dependencies": [],
        },
        {
            "item_id": "REM-002",
            "gap_reference": "REQ-ART14",
            "action_title": "Halt automated rejection — require human review",
            "action_description": "Immediately disable the feature that auto-rejects candidates.",
            "owner_role": "CPO",
            "effort_days": 2,
            "priority": "IMMEDIATE",
            "article_reference": "Article 14(1)(b)",
            "citation": "EU AI Act Art.14(1)(b)",
            "success_criteria": "No automated rejection emails sent.",
            "dependencies": [],
        },
        {
            "item_id": "REM-003",
            "gap_reference": "REQ-ART09",
            "action_title": "Create Risk Management System documentation",
            "action_description": "Draft a continuous, iterative risk management system document.",
            "owner_role": "Compliance Officer",
            "effort_days": 10,
            "priority": "THIRTY_DAYS",
            "article_reference": "Article 9",
            "citation": "EU AI Act Art.9(1)",
            "success_criteria": "Documented RMS approved by legal.",
            "dependencies": [],
        },
        {
            "item_id": "REM-004",
            "gap_reference": "REQ-ART13",
            "action_title": "Implement right to explanation feature",
            "action_description": "Provide a portal for candidates to see why they were ranked a certain way.",
            "owner_role": "Engineering Lead",
            "effort_days": 8,
            "priority": "THIRTY_DAYS",
            "article_reference": "Article 13",
            "citation": "EU AI Act Art.13(1)",
            "success_criteria": "Candidate dashboard deployed.",
            "dependencies": [],
        },
        {
            "item_id": "REM-005",
            "gap_reference": "REQ-ART10",
            "action_title": "Establish bias testing protocol",
            "action_description": "Implement automated testing scripts to identify bias across demographics.",
            "owner_role": "ML Engineer",
            "effort_days": 7,
            "priority": "THIRTY_DAYS",
            "article_reference": "Article 10(2)",
            "citation": "EU AI Act Art.10(2)",
            "success_criteria": "Bias metrics integrated into CI/CD pipeline.",
            "dependencies": [],
        },
        {
            "item_id": "REM-006",
            "gap_reference": "REQ-ANNEX4",
            "action_title": "Complete technical documentation (Annex IV)",
            "action_description": "Write comprehensive technical documentation covering architecture and model weights.",
            "owner_role": "Technical Writer",
            "effort_days": 15,
            "priority": "SIXTY_DAYS",
            "article_reference": "Annex IV",
            "citation": "EU AI Act Annex IV",
            "success_criteria": "Documentation passes internal audit.",
            "dependencies": [],
        },
        {
            "item_id": "REM-007",
            "gap_reference": "REQ-ART12",
            "action_title": "Set up audit log and record-keeping system",
            "action_description": "Implement immutable logs for all AI decisions and dataset versions.",
            "owner_role": "DevOps",
            "effort_days": 5,
            "priority": "SIXTY_DAYS",
            "article_reference": "Article 12",
            "citation": "EU AI Act Art.12(1)",
            "success_criteria": "Audit logs stored in secure object storage.",
            "dependencies": [],
        },
        {
            "item_id": "REM-008",
            "gap_reference": "REQ-ART09",
            "action_title": "Conduct conformity assessment",
            "action_description": "Hire an external auditor to conduct the required conformity assessment.",
            "owner_role": "External Auditor",
            "effort_days": 20,
            "priority": "SIXTY_DAYS",
            "article_reference": "Article 43",
            "citation": "EU AI Act Art.43",
            "success_criteria": "Conformity assessment report received.",
            "dependencies": ["REM-003", "REM-006"],
        },
        {
            "item_id": "REM-009",
            "gap_reference": "REQ-ART20",
            "action_title": "Implement post-market monitoring",
            "action_description": "Establish a framework to monitor AI performance in production continually.",
            "owner_role": "Product Manager",
            "effort_days": 12,
            "priority": "NINETY_DAYS",
            "article_reference": "Article 20",
            "citation": "EU AI Act Art.20",
            "success_criteria": "Monitoring dashboards live.",
            "dependencies": [],
        },
        {
            "item_id": "REM-010",
            "gap_reference": "REQ-ART60",
            "action_title": "Register in EU AI Act database",
            "action_description": "Formally register the High Risk system in the EU database.",
            "owner_role": "Legal Counsel",
            "effort_days": 3,
            "priority": "NINETY_DAYS",
            "article_reference": "Article 60",
            "citation": "EU AI Act Art.60",
            "success_criteria": "Registration confirmation received from EU authorities.",
            "dependencies": ["REM-008"],
        },
    ],
}

# 5. Compliance Reports
MOCK_REPORTS = {
    "report_id": "123e4567-e89b-12d3-a456-426614174000",
    "system_name": "TalentFilter Pro v2.3",
    "risk_tier": "HIGH RISK",
    "compliance_percentage": 22.0,
    "critical_gaps_count": 4,
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "foundry_iq_citations_count": 28,
    "is_verified": True,
    "verification_flags": [],
    "sections": [],
    "executive_summary": (
        "## Executive Summary\n\n"
        "**System Analyzed:** TalentFilter Pro v2.3\n"
        "**Assessment Date:** "
        + datetime.now(timezone.utc).strftime("%Y-%m-%d")
        + "\n\n"
        "This report provides an executive-level summary of the EU AI Act compliance audit for "
        "TalentFilter Pro v2.3. The system has been classified as **HIGH RISK** under the EU AI Act "
        "(Annex III) because it is used for automated recruitment and candidate ranking.\n\n"
        "### Current Status & Business Impact\n"
        "The system currently achieves a compliance score of **22.0%**. Failure to address the "
        "identified critical gaps before the enforcement deadline poses a severe regulatory risk. "
        "Under the EU AI Act, deploying a non-compliant High Risk system can result in fines up to "
        "**€35,000,000 or 7% of total worldwide annual turnover**, whichever is higher.\n\n"
        "### The 3 Most Critical Issues\n"
        "1. **Lack of Human Oversight (Article 14):** The system currently makes automated candidate "
        "rejections without human review. This is a direct violation of Article 14, which mandates "
        "human intervention mechanisms for High Risk systems.\n"
        "2. **Missing Technical Documentation (Article 11 & Annex IV):** The provided documentation "
        "(0.35 completeness score) is severely lacking. Annex IV requires granular details on system "
        "architecture, model weights, and logic.\n"
        "3. **No Risk Management System (Article 9):** There is no documented, iterative risk "
        "management system in place for the AI lifecycle.\n\n"
        "### Recommended Immediate Actions\n"
        "To mitigate immediate regulatory exposure, the following actions must be taken within 48 hours:\n"
        "- **Halt automated rejections.** A human must review and sign off on all candidate shortlists.\n"
        "- **Implement a human override mechanism** in the user interface.\n\n"
        "### 90-Day Roadmap Summary\n"
        "A comprehensive 90-day remediation plan has been established. Key milestones include:\n"
        "- **30 Days:** Establish bias testing protocols and create a Risk Management System.\n"
        "- **60 Days:** Complete Annex IV technical documentation and conduct a formal conformity assessment.\n"
        "- **90 Days:** Register the system in the official EU AI Act database and deploy post-market monitoring."
    ),
    "technical_findings": (
        "## Technical Compliance Report\n\n"
        "**System Analyzed:** TalentFilter Pro v2.3\n\n"
        "This report details the technical deficiencies identified during the EU AI Act compliance "
        "assessment and provides actionable engineering requirements.\n\n"
        "### 1. Human Oversight Engineering (Article 14)\n"
        "**Gap:** The current architecture allows the ML model to issue final 'Reject' or 'Advance' "
        "states in the database without human validation. *Citation: EU AI Act Art.14(1) - High-risk AI "
        "systems shall be designed and developed in such a way that they can be effectively overseen by "
        "natural persons.*\n\n"
        "**Technical Requirement:** \n"
        "- Modify the `PredictionService` to emit a `PendingReview` state instead of a final decision.\n"
        "- Develop an internal UI component for the HR dashboard that presents the AI's confidence score, "
        "key decision factors, and requires an explicit human click (`Approve` or `Override`).\n"
        "- Log the human reviewer's ID and timestamp alongside the decision.\n\n"
        "### 2. Automated Record-Keeping (Article 12)\n"
        "**Gap:** The system lacks immutable audit logs for prediction events over its lifetime. "
        "*Citation: EU AI Act Art.12(1) - High-risk AI systems shall technically allow for the automatic "
        "recording of events ('logs') over the duration of their lifetime.*\n\n"
        "**Technical Requirement:**\n"
        "- Integrate OpenTelemetry or a dedicated audit logging service.\n"
        "- Every prediction must log: Input data hash, Model version ID, Prediction output, Timestamp, "
        "and corresponding Human Oversight event.\n"
        "- Ensure logs are stored in a WORM (Write Once Read Many) compliant storage bucket.\n\n"
        "### 3. Data Governance and Bias Mitigation (Article 10)\n"
        "**Gap:** Training data provenance and bias testing are not integrated into the CI/CD pipeline. "
        "*Citation: EU AI Act Art.10(2) - Training data must be subject to appropriate data governance "
        "and management practices.*\n\n"
        "**Technical Requirement:**\n"
        "- Implement automated bias evaluation scripts (e.g., using Fairlearn) in the model training pipeline.\n"
        "- The pipeline must fail if demographic parity or equalized odds metrics fall below acceptable thresholds.\n"
        "- Document the provenance of the training dataset, including data collection methodologies and consent markers.\n\n"
        "### 4. Robustness and Cybersecurity (Article 15)\n"
        "**Gap:** No adversarial testing has been conducted. *Citation: EU AI Act Art.15(1) - High-risk AI "
        "systems shall achieve an appropriate level of accuracy, robustness, and cybersecurity.*\n\n"
        "**Technical Requirement:**\n"
        "- Introduce adversarial perturbation tests in the staging environment.\n"
        "- Validate that the CV parsing mechanism is resilient to prompt injection or malformed data inputs.\n\n"
        "### Deployment Safeguards\n"
        "Prior to the next production release, a feature flag must be implemented to disable all "
        "automated decision-making capabilities until the human oversight mechanisms are fully deployed "
        "and validated by the QA team."
    ),
    "certificate_draft": (
        "## CERTIFICATE OF COMPLIANCE (DRAFT)\n\n"
        "**EU AI Act (Regulation 2024/1689)**\n\n"
        "**System Name:** TalentFilter Pro v2.3\n"
        "**Developer/Vendor:** Acme HR Tech Ltd\n"
        "**Date of Assessment:** "
        + datetime.now(timezone.utc).strftime("%Y-%m-%d")
        + "\n\n"
        "This document certifies that the AI system identified above has undergone an initial compliance "
        "assessment against the requirements set forth in the European Union Artificial Intelligence Act.\n\n"
        "### Assessment Results\n"
        "- **Risk Classification:** HIGH RISK (Annex III, Article 6(2))\n"
        "- **Current Compliance Score:** 22.0%\n"
        "- **Status:** **PENDING REMEDIATION**\n\n"
        "### Declaration\n"
        "The system currently presents **4 Critical** and **4 High** severity gaps. A formal remediation "
        "plan has been established. This certificate remains in DRAFT status and does NOT grant conformity. "
        "Full conformity and authorization to affix the CE marking will only be granted upon successful "
        "completion of the 90-day remediation roadmap and a subsequent formal conformity assessment as "
        "required by Article 43.\n\n"
        "**Assessed by:** ComplianceIQ Automated Audit Engine\n"
        "**Powered by:** Microsoft Foundry IQ"
    ),
}
