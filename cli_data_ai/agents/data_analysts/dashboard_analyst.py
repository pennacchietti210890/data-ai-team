import json
import os
from pydantic import BaseModel
from agents import Agent, FunctionTool, RunContextWrapper
from cli_data_ai.tools.dashboard.metabase.tools import login_visualisation_tool, create_metabase_chart, create_metabase_dashboard, append_chart_to_metabase_dashboard
from cli_data_ai.utils.config import get_settings

class ChartOutput(BaseModel):
    chart_link: str

def create_dashboard_analyst():
    settings = get_settings()

    # Explicitly set the environment variable from settings
    if settings.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        
    return Agent(
        name="Visualisation Analyst",
        tools=[login_visualisation_tool, create_metabase_chart, create_metabase_dashboard, append_chart_to_metabase_dashboard],  
        model="gpt-4o-mini",
        instructions=(
            "You are an expert data analyst helping users to visualise information stored in a database."
            "Given an analytics question, and a related SQL query, you need to choose an appropriate visualisation format such as 'bar' for bar chart or 'table' for a table chart or 'line' for a line chart and create a chart on Metabase.\n\n"
            "If the user asks for a dashbaord, create a dashboard with such chart(s).\n"
            "Reasoning rules:\n"
            "- Before creating a chart, you always need to log in into the platform (Metabase).\n"
            "- The login should return a session token, that you need for the chart creation.\n"
        ),
        output_type=ChartOutput,
    )

# Create the agent instance
dashboard_analyst = create_dashboard_analyst()