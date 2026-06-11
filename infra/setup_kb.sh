#!/bin/bash
set -e

echo "ComplianceIQ — Setting up Foundry IQ Knowledge Base"
echo "======================================================"

# Download regulatory documents
echo "📥 Downloading EU AI Act PDF..."
curl -L "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689" \
  -o /tmp/eu_ai_act.pdf
echo "✅ EU AI Act downloaded"

echo "📥 Downloading NIST AI RMF..."
curl -L "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf" \
  -o /tmp/nist_ai_rmf.pdf
echo "✅ NIST AI RMF downloaded"

# Upload to Azure Blob Storage
echo "☁️ Uploading to Azure Blob Storage..."
az storage blob upload --file /tmp/eu_ai_act.pdf \
  --container-name regulatory-docs \
  --name eu_ai_act_regulation_2024_1689.pdf \
  --account-name $STORAGE_ACCOUNT_NAME \
  --auth-mode login

az storage blob upload --file /tmp/nist_ai_rmf.pdf \
  --container-name regulatory-docs \
  --name nist_ai_rmf_1_0.pdf \
  --account-name $STORAGE_ACCOUNT_NAME \
  --auth-mode login

echo "✅ Documents uploaded to Azure Blob Storage"
echo ""
echo "📋 Next: Run 'python -m src.knowledge_base.setup_kb' to create Foundry IQ knowledge base"
echo "🎉 Setup complete!"
