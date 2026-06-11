@description('Location for all resources')
param location string = 'eastus2'

@description('Prefix for all resource names')
@minLength(3)
@maxLength(10)
param resourcePrefix string = 'ciq'

@description('Environment tag')
param environment string = 'hackathon'

var storageAccountName = '${resourcePrefix}docs${uniqueString(resourceGroup().id)}'
var searchServiceName = '${resourcePrefix}-search-${uniqueString(resourceGroup().id)}'
var foundryWorkspaceName = '${resourcePrefix}-foundry'
var openAIAccountName = '${resourcePrefix}-openai'
var containerAppEnvName = '${resourcePrefix}-env'
var containerAppName = '${resourcePrefix}-app'

var commonTags = {
  project: 'complianceiq'
  hackathon: 'agents-league-aisf-2026'
  track: 'reasoning-agents'
  'iq-integration': 'foundry-iq'
}

// 1. Storage Account (for Foundry IQ document storage)
resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountName
  location: location
  tags: commonTags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
  }
}

resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2022-09-01' = {
  parent: storageAccount
  name: 'default'
}

resource regulatoryDocsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-09-01' = {
  parent: blobServices
  name: 'regulatory-docs'
  properties: {
    publicAccess: 'None'
  }
}

// 2. Azure AI Search Service (Foundry IQ backend)
// Basic tier required for agentic retrieval (Foundry IQ)
resource searchService 'Microsoft.Search/searchServices@2023-11-01-preview' = {
  name: searchServiceName
  location: location
  tags: commonTags
  sku: {
    name: 'basic'
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    publicNetworkAccess: 'Enabled'
    semanticSearch: 'free'
  }
}

// 3. Azure AI Foundry Workspace (hub)
resource foundryHub 'Microsoft.MachineLearningServices/workspaces@2023-10-01' = {
  name: foundryWorkspaceName
  location: location
  tags: commonTags
  kind: 'Hub'
  sku: {
    name: 'Basic'
  }
  properties: {
    friendlyName: 'ComplianceIQ Foundry Hub'
    description: 'Microsoft Agents League AISF 2026 — Reasoning Agents Track'
  }
}

// 4. Azure AI Foundry Project (under the hub)
resource foundryProject 'Microsoft.MachineLearningServices/workspaces@2023-10-01' = {
  name: '${foundryWorkspaceName}-project'
  location: location
  tags: commonTags
  kind: 'Project'
  properties: {
    hubResourceId: foundryHub.id
  }
}

// 5. Azure OpenAI Account
resource openAIAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: openAIAccountName
  location: location
  tags: commonTags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openAIAccountName
  }
}

// 6. GPT-4.1-mini Deployment
resource gptDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAIAccount
  name: 'gpt-4-1-mini'
  sku: {
    name: 'Standard'
    capacity: 10
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4.1-mini'
      version: '2025-07-14'
    }
  }
}

// 7. Azure Container Apps Environment
resource containerAppEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerAppEnvName
  location: location
  tags: commonTags
  properties: {
    appLogsConfiguration: {
      destination: 'azure-monitor'
    }
  }
}

// 8. Container App (for Streamlit)
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  tags: commonTags
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8501
      }
    }
    template: {
      containers: [
        {
          name: 'complianceiq-app'
          image: 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
          env: [
            {
              name: 'AZURE_STORAGE_ACCOUNT'
              value: storageAccount.name
            }
            {
              name: 'AZURE_SEARCH_ENDPOINT'
              value: 'https://${searchService.name}.search.windows.net'
            }
            {
              name: 'AZURE_FOUNDRY_PROJECT_ENDPOINT'
              value: foundryProject.properties.discoveryUrl
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: openAIAccount.properties.endpoint
            }
          ]
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
        }
      ]
    }
  }
}

output storageAccountName string = storageAccount.name
output searchServiceEndpoint string = 'https://${searchService.name}.search.windows.net'
output foundryProjectEndpoint string = foundryProject.properties.discoveryUrl
output openAIEndpoint string = openAIAccount.properties.endpoint
output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
