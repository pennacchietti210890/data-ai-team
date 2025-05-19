import json
import os
from pydantic import BaseModel
from agents import Agent, FunctionTool, RunContextWrapper
from cli_data_ai.tools.ml.tools import get_input_data, choose_model, run_model, model_card_report, feature_importance, select_best_model
from cli_data_ai.agents.data_analysts.sql_analyst import create_sql_analyst
from cli_data_ai.utils.config import get_settings
from cli_data_ai.agents.data_scientists.instructions.prompts import DATA_SCIENTIST_INSTRUCTIONS
from cli_data_ai.agents.data_scientists.tripwires.ds_tripwires import ml_report_guardrail_naive, ml_report_guardrail_complete, MLReport

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
            model_card_report,
            select_best_model,
            feature_importance
        ],  
        model="gpt-4.1",
        instructions=DATA_SCIENTIST_INSTRUCTIONS,
        output_guardrails=[ml_report_guardrail_complete],
        output_type=MLReport,
)

# Create the agent instance
data_scientist = create_data_scientist()