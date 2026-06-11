import streamlit as st
import asyncio
import os
import sys

# Ensure src is in the python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.orchestrator import ComplianceIQOrchestrator
from src.config import get_settings

# --- Page Config ---
st.set_page_config(
    page_title="ComplianceIQ — EU AI Act Compliance Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Custom CSS ---
st.markdown(
    """<style>
    /* Increase font size slightly */
    html, body, [class*="css"]  {
        font-size: 15px;
    }
    
    /* Make metric cards have subtle border */
    [data-testid="stMetric"] {
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 10px;
        border-radius: 8px;
        background-color: rgba(128, 128, 128, 0.05);
    }
    
    /* Make download buttons prominent (green) */
    [data-testid="stDownloadButton"] button {
        background-color: #28a745;
        color: white;
        border: none;
        width: 100%;
    }
    [data-testid="stDownloadButton"] button:hover {
        background-color: #218838;
        color: white;
    }
    
    /* Make error messages clearly red */
    [data-testid="stException"] {
        border-left: 5px solid #dc3545;
    }
    
    /* Progress bars: use Microsoft blue (#0078D4) */
    .stProgress > div > div > div > div {
        background-color: #0078D4;
    }
</style>""",
    unsafe_allow_html=True,
)

# --- Initialize Settings ---
settings = get_settings()

# --- HEADER SECTION ---
st.title("🛡️ ComplianceIQ")
st.subheader("Multi-Agent EU AI Act Compliance Intelligence System")

col1, col2 = st.columns([2, 1])
with col1:
    st.write("""
    **6 AI agents powered by Microsoft Foundry + Foundry IQ.**
    Upload your AI system documentation and get a full EU AI Act compliance audit in 3 minutes.
    """)
with col2:
    st.markdown(
        """
    🟢 **Foundry IQ** &nbsp;&nbsp;|&nbsp;&nbsp; 🔵 **6 Agents**<br/>
    🟣 **EU AI Act** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp; ⚡ **3 Minutes**
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Configuration")
    mock_mode = st.toggle("Mock Mode (Local demo)", value=True)

    if mock_mode:
        st.info("Mock Mode ON — no Azure required. Using sample CV screening AI.")
    else:
        st.subheader("Environment Status")
        # Check env vars
        env_vars = [
            ("AZURE_OPENAI_API_KEY", "Azure OpenAI Key"),
            ("AZURE_SEARCH_ENDPOINT", "Azure Search Endpoint"),
            ("AZURE_SEARCH_KEY", "Azure Search Key"),
        ]
        for var, name in env_vars:
            if os.getenv(var):
                st.markdown(f"✅ {name}")
            else:
                st.markdown(f"❌ {name}")

    st.markdown("---")
    st.link_button(
        "⭐ Star on GitHub", "https://github.com/microsoft/agents-league-aisf"
    )
    st.link_button("💬 Vote on Discord", "https://aka.ms/agentsleague/discord")


# --- MAIN CONTENT — 3 TABS ---
tab1, tab2, tab3 = st.tabs(["📤 Upload & Analyze", "📊 Results", "⬇️ Reports"])

# --- TAB 1: Upload & Analyze ---
with tab1:
    st.header("Upload Your AI System Documentation")
    st.caption(
        "Supported formats: PDF, DOCX, TXT, JSON (model cards). Max 10MB per file."
    )

    uploaded_files = st.file_uploader(
        "Drop files here or click to browse",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "json", "md"],
        key="file_uploader",
    )

    if mock_mode:
        st.info(
            "📋 No files needed in mock mode. We'll analyze a sample 'TalentFilter Pro' CV screening AI system."
        )
        with st.expander("View sample system details"):
            st.write("""
            **TalentFilter Pro v2.3**
            - Automated CV screening and candidate ranking for job applications.
            - **Decision Type:** Automated
            - **Affected Users:** Job applicants, HR managers
            - **Data Processed:** Personal data, biometric inferred, employment history
            - **Autonomy:** High
            - **Human Oversight:** False
            """)

    run_button = st.button(
        "🚀 Run Compliance Analysis",
        type="primary",
        use_container_width=True,
        disabled=(not mock_mode and not uploaded_files),
    )

    if run_button:
        st.header("🤖 Agent Pipeline Execution")

        agent_names = [
            "🔍 Scanner Agent",
            "🧠 Gap Analyzer (Foundry IQ)",
            "⚖️ Risk Scorer",
            "🗺️ Remediation Planner (Foundry IQ)",
            "📝 Report Generator",
            "✔️ Verification Agent",
        ]

        # Create placeholders
        agent_containers = {}
        for name in agent_names:
            agent_containers[name] = st.empty()
            agent_containers[name].info(f"⏳ {name}: waiting...")

        progress_bar = st.progress(0)
        status_text = st.empty()

        agent_index = [0]

        def progress_callback(agent_name, status, output):
            # Find closest matching agent name key
            matched_key = None
            for key in agent_names:
                if (
                    agent_name.lower().replace("agent", "").strip() in key.lower()
                    or agent_name in key
                ):
                    matched_key = key
                    break

            if matched_key and "complete" in status:
                agent_containers[matched_key].success(f"{matched_key}: {status}")
                agent_index[0] += 1
                progress_bar.progress(min(agent_index[0] / len(agent_names), 1.0))
            elif matched_key:
                agent_containers[matched_key].info(f"⏳ {matched_key}: {status}")

            status_text.text(f"Status: {agent_name} - {status}")

        with st.spinner("Analysis in progress..."):
            orchestrator = ComplianceIQOrchestrator(mock_mode=mock_mode)
            try:
                results = asyncio.run(
                    orchestrator.run(uploaded_files or [], progress_callback)
                )
                st.session_state["results"] = results
                progress_bar.progress(1.0)
                status_text.success(
                    "✅ Analysis complete! View results in the Results tab."
                )
                st.balloons()
            except Exception as e:
                st.error(f"Pipeline failed: {str(e)}")

# --- TAB 2: Results ---
with tab2:
    if "results" not in st.session_state:
        st.info("Run analysis first in the Upload tab.")
    else:
        results = st.session_state["results"]
        scorecard = results["scorecard"]
        gap_matrix = results["gap_matrix"]

        risk_tier = scorecard["risk_tier"]
        is_high = "HIGH" in risk_tier or "UNACCEPTABLE" in risk_tier

        # METRICS ROW
        col1, col2, col3, col4 = st.columns(4)
        col1.metric(
            "EU AI Act Risk Tier",
            risk_tier,
            delta="⚠️ Strict Requirements Apply" if is_high else "",
            delta_color="inverse" if is_high else "normal",
        )
        col2.metric(
            "Compliance Score",
            f"{scorecard['compliance_percentage']:.1f}%",
            delta=(
                f"-{scorecard['critical_count']} critical gaps"
                if scorecard["critical_count"] > 0
                else "Compliant"
            ),
            delta_color="inverse",
        )

        total_gaps = len(gap_matrix["gaps"])
        found_gaps = (
            scorecard["critical_count"]
            + scorecard["high_count"]
            + scorecard["medium_count"]
            + scorecard["low_count"]
        )
        col3.metric(
            "Gaps Identified",
            found_gaps,
            delta=f"of {total_gaps} rules checked",
            delta_color="off",
        )
        col4.metric("Foundry IQ Citations", scorecard["total_citations"])

        st.markdown("---")

        # GAPS LIST
        st.subheader("📋 Compliance Gap Analysis")
        st.caption("All gaps retrieved from Foundry IQ knowledge base with citations")

        for gap in gap_matrix["gaps"]:
            status = gap["status"]
            severity = gap["severity"]

            if status == "COMPLIANT":
                color_icon = "🟢"
            elif severity == "CRITICAL":
                color_icon = "🔴"
            elif severity == "HIGH":
                color_icon = "🟠"
            else:
                color_icon = "🟡"

            with st.expander(f"{color_icon} {gap['requirement_name']} — {status}"):
                st.write(f"**Severity**: {severity}")
                st.write(f"**Description**: {gap['description']}")
                st.write(
                    f"**Missing Evidence**: {', '.join(gap['missing_evidence']) if gap['missing_evidence'] else 'None'}"
                )
                if gap.get("citations"):
                    st.caption(f"📄 Source: {gap['citations'][0]}")

        st.markdown("---")

        # REMEDIATION ROADMAP
        st.subheader("🗺️ Remediation Roadmap")
        roadmap = results["remediation_roadmap"]

        r_cols = st.columns(4)

        def display_items(col, title, priority_value):
            items = [
                item for item in roadmap["items"] if item["priority"] == priority_value
            ]
            col.markdown(f"**{title}** ({len(items)})")
            for item in items:
                col.info(
                    f"**{item['action_title']}**\n\n"
                    f"👤 {item['owner_role']}\n\n"
                    f"⏱️ {item['effort_days']} days"
                )

        display_items(r_cols[0], "Immediate", "IMMEDIATE")
        display_items(r_cols[1], "30 Days", "THIRTY_DAYS")
        display_items(r_cols[2], "60 Days", "SIXTY_DAYS")
        display_items(r_cols[3], "90 Days", "NINETY_DAYS")


# --- TAB 3: Reports ---
with tab3:
    if "results" not in st.session_state:
        st.info("Run analysis first in the Upload tab.")
    else:
        results = st.session_state["results"]
        reports = results["reports"]

        st.subheader("Download Compliance Reports")

        col1, col2, col3 = st.columns(3)
        col1.download_button(
            "📊 Executive Report",
            reports["executive_summary"].encode("utf-8"),
            "executive_report.md",
            mime="text/markdown",
        )
        col2.download_button(
            "🔧 Technical Report",
            reports["technical_findings"].encode("utf-8"),
            "technical_report.md",
            mime="text/markdown",
        )
        col3.download_button(
            "📋 Compliance Certificate",
            reports["certificate_draft"].encode("utf-8"),
            "compliance_certificate.md",
            mime="text/markdown",
        )

        st.markdown("---")
        st.subheader("Preview: Executive Summary")
        st.markdown(reports["executive_summary"])
