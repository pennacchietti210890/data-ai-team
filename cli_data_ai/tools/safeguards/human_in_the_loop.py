from agents import function_tool
from agents import RunContextWrapper
from cli_data_ai.agents.context.context import InputData
@function_tool  
def ask_for_confirmation(wrapper: RunContextWrapper[InputData], text: str) -> str:
    """
    Ask the user for confirmation before taking an action

    Args:
        text (str): The clarification question to ask the user.

    Returns:
        str: The clarification response from the user.
    """
    print(f"\n📝 The agent is asking for clarification:\n{text}\n")
    clarification = input("Your clarification: (yes/no)")
    if clarification.lower() in ["yes"]:
        wrapper.context.human_confirmation = True
    else:
        wrapper.context.human_confirmation = False
    return clarification