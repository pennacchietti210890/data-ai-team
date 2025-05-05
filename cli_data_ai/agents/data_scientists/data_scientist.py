import json
import os
from pydantic import BaseModel
from agents import Agent, FunctionTool, RunContextWrapper
from cli_data_ai.tools.ml.tools import get_input_data, choose_model, run_model, model_card_report
from cli_data_ai.agents.data_analysts.sql_analyst import create_sql_analyst
from cli_data_ai.utils.config import get_settings

def create_data_scientist():
    settings = get_settings()

    # Explicitly set the environment variable from settings
    if settings.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    
    sql_agent = create_sql_analyst()
    
    return Agent(
        name="Data Scientist agent",
        tools=[
            sql_agent.as_tool(
                tool_name="sql_agent",
                tool_description="SQL agent to inspect database and execute SQL queries",
            ),
            get_input_data, 
            choose_model, 
            run_model, 
            model_card_report
        ],  
        model="gpt-4o-mini",
        instructions=(
            "You are an expert data scientist helping users create and evaluate predictive models from tabular data.\n\n"
            "## Your Goal\n"
            "- Given a business question, build models to predict or classify the right target based on meaningful input data.\n\n"
            "## Step-by-step Guide\n"
            "1. Use `sql_agent` to inspect the schema and propose a complete SQL query.\n"
            "2. The SQL query must include **both input features and the target variable** (based on the user’s modeling goal). In the SQL query, take into account the following:\n"
            "   - If the user is asking for a classification model, the target variable must be either a binary or a categorical variable.\n"                
            "3. Pass the full query to `get_input_data` to retrieve the DataFrame.\n"
            "4. Call `choose_model` to determine 3–4 baseline models (e.g. linear regression, random forest, MLP).\n"
            "5. For each selected model, call `run_model`, providing:\n"
            "   - The name of the target column\n"
            "   - The chosen model type\n"
            "6. Gather the results and pass them to `model_card_report` to summarize and interpret model quality and business impact.\n"
            "7. Recommend next steps based on model findings.\n\n"
            "## Reminder\n"
            "- Always include the target variable in your SQL query.\n"
            "- Ensure data passed between tools is complete, well-formed, and JSON-encoded as a full DataFrame (not just values).\n"
            "- If in doubt, ask `sql_agent` to verify what columns are present in a table."
        )
)

# Create the agent instance
data_scientist = create_data_scientist()