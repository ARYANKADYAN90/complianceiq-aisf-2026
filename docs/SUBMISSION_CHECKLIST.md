# 🚀 ComplianceIQ Pre-Submission Checklist

## SECTION 1: TECHNICAL REQUIREMENTS (from official rules)
- [ ] GitHub repository is PUBLIC (Settings → Danger Zone → Change visibility)
- [ ] README.md exists at root level with demo video link at top
- [ ] Demo video uploaded to YouTube or Vimeo (unlisted is acceptable)
- [ ] Demo video is under 5 minutes (rules state max 5 min)
- [ ] architecture_diagram.png is in the repository
- [ ] Source code runs from a fresh clone with documented setup steps
- [ ] No .env file committed (verify: `git log --all -- .env` shows nothing)
- [ ] No Azure API keys hardcoded anywhere (run: `grep -r "api_key" src/` should return nothing sensitive)

## SECTION 2: FOUNDRY IQ INTEGRATION (required for IQ tools prize)
- [ ] Foundry IQ knowledge base documented in README
- [ ] At least 2 knowledge sources configured
- [ ] Architecture diagram shows Foundry IQ integration clearly
- [ ] Code shows `AzureAISearchContextProvider` with `mode="agentic"`
- [ ] Mock mode demonstrates what Foundry IQ returns (citations format)

## SECTION 3: SUBMISSION FORM FIELDS (have these ready to copy-paste)
**Project Name:** ComplianceIQ
**Track:** Reasoning Agents
**Short description (100 chars):** "6-agent EU AI Act compliance audit system using Microsoft Foundry + Foundry IQ. Turns 6-week/$50K audits into 3-minute reports."
**Long description (500 chars):** "ComplianceIQ is an enterprise-grade, multi-agent AI pipeline built for the Agents League AISF 2026 Reasoning Agents track. It completely automates EU AI Act (Regulation 2024/1689) compliance auditing. By utilizing 6 specialized agents powered by Microsoft Foundry and the Foundry IQ knowledge base, the system processes proprietary AI system documentation to identify gaps, classify Annex III risk tiers, and generate actionable 30/60/90-day remediation roadmaps backed by grounded legal citations."
**Technologies:** Microsoft Foundry Agent Service, Foundry IQ (Azure AI Search), Azure OpenAI (gpt-4.1-mini), Python 3.11, Streamlit, OpenTelemetry, Pydantic v2, Azure Container Apps
**Microsoft IQ Layer Used:** Foundry IQ
**Problem solved:** EU AI Act compliance automation for organizations
**Impact:** Reduces compliance cost from $50K/6 weeks to free/3 minutes
**GitHub repo URL:** https://github.com/YOUR_USERNAME/complianceiq
**Demo video URL:** https://youtube.com/YOUR_VIDEO

## SECTION 4: SPECIAL PRIZES TO APPLY FOR
- [ ] Best Reasoning Agent ($5,000): Primary track entry
- [ ] Best Use of IQ Tools ($5,000): Explicitly state Foundry IQ usage
- [ ] Accessibility Award ($1,468): Document accessibility features
- [ ] Hack for Good ($1,468): Document democratization aspect
- [ ] *If student:* Top Student Award ($1,468): Provide university enrollment proof

## SECTION 5: COMMUNITY VOTE CAMPAIGN (10% of score)
- [ ] Posted intro in #introductions on Discord
- [ ] Shared progress update (Day 1, Day 2, Day 3)
- [ ] Posted "just submitted!" with demo screenshot
- [ ] Discord username in submission form
- [ ] Voted for 3 other people's projects (good karma)

## SECTION 6: FINAL QUALITY CHECKS
- [ ] Run: `python -m pytest tests/ -v` — all tests pass
- [ ] Run: `streamlit run app/streamlit_app.py` — app starts without errors
- [ ] Mock pipeline completes in under 2 seconds
- [ ] All 3 reports can be downloaded
- [ ] Architecture diagram renders properly in README preview
- [ ] Clicked every link in README (no broken links)
- [ ] Spell-checked README (copy into Google Docs → Tools → Spell Check)
