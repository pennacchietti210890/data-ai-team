from agents import function_tool
import requests 
from agents import Agent, RunContextWrapper, Runner, function_tool
from pydantic import BaseModel
from cli_data_ai.agents.context.context import InputData

@function_tool  
def login_visualisation_tool(wrapper: RunContextWrapper[InputData]) -> str:
    
    """Logins into the Visualisation Tool: Metabase
    Returns the session token needed to create object usch as chart cards inside Metabase
    """
    url = f"{wrapper.context.metabase_url}/api/session"
    payload = {"username": wrapper.context.metabase_user_name, "password": wrapper.context.metabase_password}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    session_token = response.json()["id"]
    return session_token

@function_tool
def create_metabase_chart(wrapper: RunContextWrapper[InputData],session_token: str, sql_query: str, name: str, display: str) -> str:
    """Create a Metabase chart via creating a SQL Card question and returns the corresponding url

    Args:
        session_token: Token ID for the session returned after login
        sql_query: SQL Query to build the chart
        name: Name of the chart
        display: Visualisation type for the chart, can be one of the following: 'table', 'bar', 'line', 'pie', 'scatter', 'area'
    """
    url = f"{wrapper.context.metabase_url}/api/card"
    headers = {"X-Metabase-Session": session_token}

    payload = {
        "name": name,
        "dataset_query": {
            "type": "native",
            "native": {"query": sql_query},
            "database": 2
        },
        "display": display,  
        "visualization_settings": {}
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    card = response.json()
    
    card_url = f"localhost:3000/card/{card['id']}"
    return card_url

@function_tool
def create_metabase_dashboard(wrapper: RunContextWrapper[InputData],session_token: str, name: str, description: str) -> int:
    """Create a Metabase Dashboard and return the corresponding ID

    Args:
        session_token: Token ID for the session returned after login
        name: Name for the dashboard
        description: Description of the dashboard
    """
    url = f"{wrapper.context.metabase_url}/api/dashboard"
    headers = {"X-Metabase-Session": session_token}
    payload = {"name": name, "description": description}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["id"]

@function_tool
def add_chart_to_metabase_dashboard(wrapper: RunContextWrapper[InputData],session_token: str, dashboard_id: int, card_id: int) -> str:
    """Add a Metabase chart (its SQL Card) to the Dashboard and return the corresponding dashboard url

    Args:
        session_token: Token ID for the session returned after login
        dashboard_id: ID for the dashboard
        card_id: ID of the Metabase Card
    """
    url = f"{wrapper.context.metabase_url}/api/dashboard/{dashboard_id}/cards"
    headers = {"X-Metabase-Session": session_token}
    payload = {
      "cards": [
        {
          "col": 0,
          "row": 0,
          "id": card_id,
          "card_id": card_id,
          "size_x": 10,
          "size_y": 10,
          "series": [
          ],
        }
      ],
    }
    response = requests.put(url, headers=headers, json=payload)
    response.raise_for_status()
    dashboard_url = f"{wrapper.context.metabase_url}/dashboard/{dashboard_id}"
    return dashboard_url

@function_tool
def append_chart_to_metabase_dashboard(wrapper: RunContextWrapper[InputData],session_token: str, dashboard_id: int, card_id: int) -> str:
    """Add a Metabase chart (its SQL Card) to the Dashboard and return the corresponding dashboard url
    
    Args:
        session_token: Token ID for the session returned after login
        dashboard_id: ID for the dashboard
        card_id: ID of the Metabase Card
    """   
    # Step 1: Fetch current dashboard layout
    url = f"{wrapper.context.metabase_url}/api/dashboard/{dashboard_id}"
    headers = {"X-Metabase-Session": session_token}
    response = requests.get(url, headers=headers)
    
    response.raise_for_status()
    dashboard_data = response.json()
    existing_cards = dashboard_data.get("dashcards", [])
    
    # Step 2: Compute next available position
    occupied = set()
    for card in existing_cards:
        c0 = card.get("col", 0)
        r0 = card.get("row", 0)
        w = card.get("size_x", 12)
        h = card.get("size_y", 10)
        for dx in range(w):
            for dy in range(h):
                occupied.add((c0 + dx, r0 + dy))

    # Scan row by row
    for row in range(100):  # allow up to 100 rows
        for col in range(0, 24, 12):
            # Check if space is free
            space_free = all((col + dx, row + dy) not in occupied
                             for dx in range(12) for dy in range(10))
            if space_free:
                break
        break
    
    # Step 3: Create the new dashboard layout card
    new_layout_card = {
        "id": card_id,         # dashboard card id (can reuse or generate unique)
        "card_id": card_id,    # saved question ID
        "col": col,
        "row": row,
        "size_x": 12,
        "size_y": 10,
        "parameter_mappings": [],
        "visualization_settings": {},
    }
    
    # Step 5: PUT full layout
    put_url = f"{wrapper.context.metabase_url}/api/dashboard/{dashboard_id}/cards"
    payload = {
        "cards": existing_cards + [new_layout_card],
    }
    
    put_response = requests.put(put_url, headers=headers, json=payload)
    put_response.raise_for_status()
    dashboard_url = f"{wrapper.context.metabase_url}/dashboard/{dashboard_id}"
    return dashboard_url