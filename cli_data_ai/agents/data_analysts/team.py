import json
import os
from pydantic import BaseModel
from agents import Agent, FunctionTool, RunContextWrapper
from cli_data_ai.agents.data_analysts.sql_analyst import sql_analyst
from cli_data_ai.agents.data_analysts.dashboard_analyst import dashboard_analyst
from cli_data_ai.utils.config import get_settings
from cli_data_ai.agents.data_analysts.instructions.prompts import DATA_MANAGER_INSTRUCTIONS

def create_team():
    settings = get_settings()

    # Explicitly set the environment variable from settings
    if settings.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        
    return Agent(
        name="Manager agent", 
        model="gpt-4o",
        instructions=DATA_MANAGER_INSTRUCTIONS,
        tools=[
            sql_analyst.as_tool(
                tool_name="sql_agent",
                tool_description="SQL agent to inspect database and execute SQL queries",
            ),
            dashboard_analyst.as_tool(
                tool_name="visualisation_agent",
                tool_description="Visualisation agent to create chart via metabase card questions as well as creating dashboards with those charts",
            )
        ]
    )

# Create the agent instance
manager = create_team()