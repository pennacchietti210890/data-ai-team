import json
import os
from pydantic import BaseModel
from agents import Agent, FunctionTool, RunContextWrapper
from cli_data_ai.tools.dashboard.metabase.tools import login_visualisation_tool, create_metabase_chart, create_metabase_dashboard, append_chart_to_metabase_dashboard
from cli_data_ai.utils.config import get_settings
from cli_data_ai.agents.data_analysts.instructions.prompts import DASHBOARD_ANALYST_INSTRUCTIONS

def create_dashboard_analyst():
    settings = get_settings()

    # Explicitly set the environment variable from settings
    if settings.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        
    return Agent(
        name="Visualisation agent",
        tools=[login_visualisation_tool, create_metabase_chart, create_metabase_dashboard, append_chart_to_metabase_dashboard],  
        model="gpt-4o",
        instructions=DASHBOARD_ANALYST_INSTRUCTIONS
    )

# Create the agent instance
dashboard_analyst = create_dashboard_analyst()