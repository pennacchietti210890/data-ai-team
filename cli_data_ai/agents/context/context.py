from pydantic import BaseModel, ConfigDict
import pandas as pd
from agents import RunContextWrapper

class InputData(BaseModel):
    """
    Input data for the agent
    """
    database_name: str
    metabase_url: str
    metabase_user_name: str
    metabase_password: str
    df: pd.DataFrame = None
    trained_models: dict = {}  # Store all models by name
    trained_model: object = None  # Store the best model
    model_results: list = []  # Optional: store all results
    human_confirmation: bool = False

    class Config:
        arbitrary_types_allowed = True