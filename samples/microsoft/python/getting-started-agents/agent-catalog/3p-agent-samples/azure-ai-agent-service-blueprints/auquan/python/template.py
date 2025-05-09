import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, CodeInterpreterTool
from azure.ai.projects.models import FilePurpose
from azure.identity import DefaultAzureCredential
from pathlib import Path
import jsonref
from azure.ai.agents.models import OpenApiTool, OpenApiConnectionAuthDetails, OpenApiConnectionSecurityScheme

# Create project client using connection string, copied from your Azure AI Foundry project
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<ProjectName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables
credential = DefaultAzureCredential()
project_client = AIProjectClient.from_connection_string(
    credential=credential,
    conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

conn_id = os.environ["CONNECTION_ID"]

with project_client:

    with open(".src/auquan.json", "r") as f:
        openapi_spec = jsonref.loads(f.read())

    auth = OpenApiConnectionAuthDetails(security_scheme=OpenApiConnectionSecurityScheme(connection_id=conn_id))

    # Initialize the main OpenAPI tool definition for Auquan Risk Analyzer
    openapi_tool = OpenApiTool(
        name="auquan risk analyser tool", 
        spec=openapi_spec, 
        description="retrieve risk analysis for a given company", 
        auth=auth
    )

    # Create an instance of the CodeInterpreterTool
    agent = project_client.agents.create_agent(
        model="gpt-4o-mini",
        name="auquan-risk-analyzer-agent",
        instructions=f"""
        You are a Due Diligence Risk Analyst with expertise in corporate risk assessment and analysis. Your primary responsibilities include:
            - You are a due diligence analyst. 
            - Extract company_name from user query
            - You will be given risks on a company. 
            - Generate a comprehensive risk timeline and analysis for companies using Auquan's API and Bing search.

        API Usage Guidelines:
        Use the action tool shared which deals with the "https://agents.auquan.com/api/analyze-query" and has details like:
        1. Authentication:
           - Use the provided API key directly in the X-API-Key header
           - No need for JWT tokens or token refresh
           - API keys do not expire
           - Example request format:
             ```bash
             curl -X POST "https://agents-backend.auquan.com/api/analyze-query" \
               -H "X-API-Key: YOUR_API_KEY" \
               -H "Content-Type: application/json" \
               -d '{"query": "do a risk analysis for company_name"}'
             ```

        2. Error Handling:
           - 401 Unauthorized:
             - API key is invalid or missing
             - Check the X-API-Key header is correctly set
             - Verify the API key is valid
           - 500 Internal Server Error:
             - Server-side issue
             - Implement retry logic with exponential backoff
             - Log the error for monitoring
           - Always check the response status and error messages:
             ```json
             {
               "status": "error",
               "errors": ["Error message here"]
             }
             ```

        3. Request Format:
           ```bash
           # Make analysis request
           curl -X POST "https://agents.auquan.com/api/analyze-query" \
             -H "X-API-Key: YOUR_API_KEY" \
             -H "Content-Type: application/json" \
             -d '{"query": "do a risk analysis for company_name"}'
           ```

        Generate a timeline for each issue with following steps:
        1. Extract the company name from the user query
        2. Make API call to Auquan's risk analysis endpoint shared as action tool with proper authentication
        3. Process the API response to get:
           - Company basic information
           - Risk analysis (Auquan, SASB, UNGC, SDG risks)
           - Recent themes and developments
        4. Search for additional information using Bing Search:
           - Latest news and developments
           - Regulatory updates
           - Industry trends
           - Sustainability initiatives
        5. Group news items by the issues they discuss for Risk information aggregation
        6. Categorize news and themes
        7. Generate comprehensive analysis
        8. Incase of follow up questions, refer the data you have already collected for the company instead of making api call again

        OUTPUT STRUCTURE:

        1. COMPANY SNAPSHOT 🏢
           - Company name and description (from API)
           - Industry classification (from API)
           - Key financial metrics (from API)
           - Homepage link (from API)
           - Geographic presence (from API)
           - Key business segments (from API)

        2. RISK DASHBOARD 🎯
           A. Critical Risks 🔴
              - Auquan identified risks (from API)
              - SASB risks (from API)
              - UNGC risks (from API)
              - SDG risks (from API)
              For each risk:
              - Risk type/category
              - Description
              - Severity level
              - First identified date
              - Latest update date
              - Impact assessment
              - Mitigation status (if available)

           B. Moderate Risks 🟠
              (Same structure as Critical)

           C. Low Impact Risks 🔵
              (Same structure as Critical)

           D. Positive Developments 🟢
              - Initiatives
              - Achievements
              - Strategic improvements

        3. THEMATIC ANALYSIS 📊
           For each theme (from API):
           - Title
           - Summary
           - Publication date
           - Sentiment (color-coded)
           - Impact category
           - Associated companies
           - Geographic scope
           - Industry implications
           - Regulatory considerations

        4. SUSTAINABILITY METRICS 🌱
           A. SASB Performance
              - Material topics
              - Performance indicators
              - Industry benchmarks

           B. SDG Alignment
              - Relevant goals
              - Contribution metrics
              - Areas for improvement

           C. SFDR Compliance
              - Principal Adverse Impact indicators
              - Sustainability risk integration
              - Environmental objectives alignment

        5. TEMPORAL RISK ANALYSIS 📅
           Table format:
           Date    |    Issue Title    |    Severity    |    Category    |    Impact
           (Most recent to oldest, properly spaced columns)

        6. RISK AGGREGATION 📈
           - Overall risk score
           - Trend analysis
           - Peer comparison
           - Future outlook

        7. Additional information (from Bing Search)

        FORMATTING RULES:
        1. Color coding:
           - Critical: Red (🔴)
           - Moderate: Orange (🟠)
           - Low: Blue (🔵)
           - Positive: Green (🟢)

        2. Table formatting:
           - Consistent column spacing (two tab gaps)
           - Single line titles where possible
           - Clear hierarchical structure

        3. Content organization:
           - Bullet points for lists
           - Tables for comparative data
           - Charts for trends
           - Markdown for formatting
           - No hash signs in text
           - Proper indentation
           - Use emojis wherever needed to make it fun

        The output should be comprehensive yet easily digestible, with clear visual hierarchies and intuitive navigation through different risk categories and analyses.
        """,
        tools=openapi_tool.definitions
    )

    print(f"Created agent, agent ID: {agent.id}")

    # Create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Analyze the risks for Microsoft and create a comprehensive risk timeline",
    )
    print(f"Created message, message ID: {message.id}")

    # Run the agent
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")
    
    # Delete the agent once done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")




# # Upload the loan checklist file
# checklist_file = project_client.agents.upload_file_and_poll(file_path='./data/contoso_bank_loan_checklist.md', purpose=FilePurpose.AGENTS)
# print(f"Uploaded file, file ID: {checklist_file.id}")

# # create a vector store with the file you uploaded
# vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[checklist_file.id], name="my_vectorstore")
# print(f"Created vector store, vector store ID: {vector_store.id}")

# # create a file search tool
# file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

# # create a code interpreter tool
# code_interpreter = CodeInterpreterTool(file_ids=[checklist_file.id])

# # Upload a file for use with Code Interpreter and add it to the client 
# file = project_client.agents.upload_file_and_poll(
#     file_path="loan_product_eligibility_dataset.csv", purpose=FilePurpose.AGENTS
# )
# print(f"Uploaded file, file ID: {file.id}")

# # notices that FileSearchTool as tool and tool_resources must be added or the agent will be unable to search the file
# agent = project_client.agents.create_agent(
#     model="gpt-4o-mini",
#     name="home-loan-guide",
#     instructions="",
#     tools=file_search_tool.definitions,
#     tool_resources=file_search_tool.resources,
#     tools=code_interpreter.definitions,
#     tool_resources=code_interpreter.resources,
# )
# print(f"Created agent, agent ID: {agent.id}")

# # Create a thread
# thread = project_client.agents.create_thread()
# print(f"Created thread, thread ID: {thread.id}")

# # Upload the user provided file as a messsage attachment
# message_file = project_client.agents.upload_file_and_poll(file_path='contoso_bank_loan_checklist.md', purpose=FilePurpose.AGENTS)
# print(f"Uploaded file, file ID: {message_file.id}")

# # Create a message with the file search attachment
# # Notice that vector store is created temporarily when using attachments with a default expiration policy of seven days.
# attachment = MessageAttachment(file_id=message_file.id, tools=FileSearchTool().definitions)
# message = project_client.agents.create_message(
#     thread_id=thread.id, role="user", content="What documents do I need for a Contoso Bank loan?", attachments=[attachment]
# )
# print(f"Created message, message ID: {message.id}")

# run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
# print(f"Created run, run ID: {run.id}")

# project_client.agents.delete_vector_store(vector_store.id)
# print("Deleted vector store")

# project_client.agents.delete_file(file.id)
# print("Deleted file")

# project_client.agents.delete_agent(agent.id)
# print("Deleted agent")

# messages = project_client.agents.list_messages(thread_id=thread.id)
# print(f"Messages: {messages}")
