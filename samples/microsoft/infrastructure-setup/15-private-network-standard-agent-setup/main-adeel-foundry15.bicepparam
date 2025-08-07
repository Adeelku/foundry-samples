using './main.bicep'

param location = 'canadaeast'
param aiServices = 'aiservices'
param modelName = 'gpt-4o'
param modelFormat = 'OpenAI'
param modelVersion = '2024-11-20'
param modelSkuName = 'GlobalStandard'
param modelCapacity = 30
param firstProjectName = 'project'
param projectDescription = 'A project for the AI Foundry account with network secured deployed Agent'
param displayName = 'project'
param peSubnetName = 'privateendpoints'

// Resource IDs for existing resources
// If you provide these, the deployment will use the existing resources instead of creating new ones
param existingVnetResourceId = ''
param vnetName = 'sob15-vnet'
param agentSubnetName = 'foundryclient'
param aiSearchResourceId =  ''
param azureStorageAccountResourceId = ''
param azureCosmosDBAccountResourceId = ''
param existingAoaiResourceId = ''

// Pass the DNS zone map here
// Leave empty to create new DNS zone, add the resource group of existing DNS zone to use it
param existingDnsZones = {}

//DNSZones names for validating if they exist
param dnsZoneNames = [
  'privatelink.services.ai.azure.com'
  'privatelink.openai.azure.com'
  'privatelink.cognitiveservices.azure.com'
  'privatelink.search.windows.net'
  'privatelink.blob.core.windows.net'
  'privatelink.documents.azure.com'
]


// Network configuration: only used when existingVnetResourceId is not provided
// These addresses are only used when creating a new VNet and subnets
// If you provide existingVnetResourceId, these values will be ignored
param vnetAddressPrefix = '10.0.0.0/16'
param agentSubnetPrefix = '10.0.1.0/24'
param peSubnetPrefix = '10.0.0.0/27'

