# Auquan Due Diligence Risk Analyst Agent

This code sample for the Due Diligence Risk Analyst enables building an expert system designed to provide comprehensive risk analysis and timeline tracking for companies. It specializes in analyzing company risks across multiple dimensions including operational, financial, regulatory, and sustainability metrics. The agent processes structured risk data from Auquan's API, generates detailed timelines, and provides actionable insights through well-formatted reports with visual risk indicators.

---

## 💼 Use Cases
1. Comprehensive Risk Analysis
   - "Do a risk analysis for Total energies"

2. Specific Risk Assessment
   - "What are the critical risks identified for TotalEnergies?"

3. Sustainability Analysis
   - "Generate a sustainability analysis for TotalEnergies"

4. Risk Table Creation
   - "Create a table indicating risks for TotalEnergies showing all categories and severity"

5. Overall Risk Rating Analysis
   - "What is the overall risk range of TotalEnergies?"

6. Recent Theme Analysis
   - "What are the recent themes around TotalEnergies and what are their impacts?"

---

## 🧩 Tools

This agent leverages **Azure AI Agent Service**, using the following tools:
## Tool 1: Auquan API
**Description:** 
Retrieves and processes company risk data from Auquan's API. This tool enables the agent to access comprehensive company information, risk assessments, and thematic analysis data.

**API Endpoint:** `https://agents.auquan.com/api/analyze-query`
**Authentication:** API key in x-api-key header
**Request Format:**
```json
{
  "query": "do a risk analysis for {COMPANY_NAME}"
}
```

**Error Handling:**
- 401: Check API key validity
- 500: Retry with backoff
- Log all errors for monitoring

### Tool 2: Code Interpreter
**Description:**
Performs data analysis and visualization tasks including:
- Risk score calculations
- Timeline generation
- Data formatting and structuring
- Table and chart creation

**Reference Files:**
- No specific reference files required
- No authentication required

### Tool 3: Grounding with Bing Search
**Description:**
Enriches the analysis with:
- Latest news and developments
- Regulatory updates
- Industry trends
- Sustainability initiatives

**Reference Files:**
- No specific reference files required
- No authentication required

The agent is configured via a `template.py` file and deployable with Bicep for enterprise use.


## ⚙️ Setup Instructions

### Prerequisites
1. Azure subscription with the following permissions
   - Contributor or Cognitive Services Contributor role (for resource deployment)
   - Azure AI Developer and Cognitive Services user role (for agent creation)
2. Agent setup: deploy the latest agent setup using this ([custom deployment](https://www.aka.ms/basic-agent-deployment)).
   - The above creates:
      - AI Services resource
      - AI Project
      - Model deployment
3. Python 3.8+
4. Azure CLI
5. An API key for your Auquan Risk Agent

---

### Steps
1. **Clone the Repository**

2. **Set Environment Variables**
```bash
PROJECT_ENDPOINT="<your-project-endpoint>" # (https://<your-ai-services-account-name>.services.ai.azure.com/api/projects/<your-project-name>)
MODEL_DEPLOYMENT_NAME="<your-model-deployment-name>"
OPENAPI_CONNECTION_ID="<your-Auquantool-connection-id>"

3. **Deploy Resources**

4. **Run the Agent Script**
```bash
template.py
```
---
## 💬 Example Agent Interactions

- "Do a risk analysis for Microsoft"

- "What are the critical risks identified for Microsoft?"

- "Generate a sustainability analysis for Microsoft"

- "Create a table indicating risks for Microsoft showing all categories and severity"

- "What is the overall risk range of Microsoft?"

- "What are the recent themes around Microsoft and what are their impacts?"

 
## 🛠 Customization Tips

- **Connect with more datasets**  
  Add datasets like lawsuits/sanctions to the agent's analysis via the Auquan Knowledge tool to identify potential risks.

- **Connect with vector stores**  
  Connect with vector stores that have specific data (eg. Annual Reports, Industry Reports etc.) ingested into them.

- **Connect with local files**  
  Add your local files to include your data in risk-analysis
