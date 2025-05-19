import json
import os
from pydantic import BaseModel
from agents import Agent, FunctionTool, RunContextWrapper
from cli_data_ai.tools.db.sqlite.tools import describe_database, profile_database, sql_query_tool, create_table, drop_table, update_records, insert_record, delete_records
from cli_data_ai.tools.safeguards.human_in_the_loop import ask_for_confirmation
from cli_data_ai.utils.config import get_settings
from cli_data_ai.agents.data_analysts.instructions.prompts import DATA_ANALYST_INSTRUCTIONS

class SQLOutput(BaseModel):
    sql_query: str
    query_results: str

def create_sql_analyst():
    settings = get_settings()

    # Explicitly set the environment variable from settings
    if settings.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        
    return Agent(
        name="SQL agent",
        tools=[describe_database, profile_database, sql_query_tool, create_table, drop_table, update_records, insert_record, delete_records, ask_for_confirmation],
        model="gpt-4.1",
        instructions=DATA_ANALYST_INSTRUCTIONS,
        output_type=SQLOutput,
    )

# Create the agent instance
sql_analyst = create_sql_analyst()