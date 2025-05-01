import json
import os
from pydantic import BaseModel
from agents import Agent, FunctionTool, RunContextWrapper
from cli_data_ai.tools.db.sqlite.tools import describe_database, profile_database, sql_query_tool
from cli_data_ai.utils.config import get_settings

class SQLOutput(BaseModel):
    sql_query: str
    query_results: str

def create_sql_analyst():
    settings = get_settings()

    # Explicitly set the environment variable from settings
    if settings.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
        
    return Agent(
        name="SQL Analyst",
        tools=[describe_database, profile_database, sql_query_tool],
        model="gpt-4o-mini",  # Using GPT-4 as it's better for SQL analysis
        instructions=(
            "You are an expert data analyst helping users retrieve information from a database. "
            "You can execute SQL queries directly or inspect the database schema if needed.\n\n"
            "Reasoning rules:\n"
            "- After executing a SQL query, always check whether the result contains useful data.\n"
            "- If the query executes successfully but the result is empty or very small (like 0 rows), "
            "you should assume the query might be wrong, incomplete, or based on wrong assumptions.\n"
            "- In that case, consider calling `describe_database` or `profile_database` to better understand the tables and columns before trying again.\n"
            "- Avoid giving final answers based on empty or 0-result queries without verifying schema understanding.\n"
        ),
        output_type=SQLOutput,
    )

# Create the agent instance
sql_analyst = create_sql_analyst()