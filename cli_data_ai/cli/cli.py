import typer
from agents import Runner
from cli_data_ai.agents.data_analysts.sql_analyst import sql_analyst
from cli_data_ai.agents.data_analysts.dashboard_analyst import dashboard_analyst
from cli_data_ai.agents.data_analysts.team import manager
from cli_data_ai.agents.data_scientists.data_scientist import data_scientist
import asyncio
import os
from cli_data_ai.utils.config import settings, get_settings
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
import json
from cli_data_ai.memory.memory import SharedMemoryManager
from cli_data_ai.utils.events_stream import stream_events
from cli_data_ai.agents.context.context import InputData
import pandas as pd

app = typer.Typer(help="Data Analyst CLI", invoke_without_command=True)
console = Console()

# Define available agents
AGENTS = {
    "SQL Analyst": sql_analyst,
    "Data Manager": manager,
    "Data Scientist": data_scientist,
    # Add more agents here as they become available
}

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def select_agent() -> tuple:
    """
    Display agent selection menu and return the selected agent and its name.
    """
    console.print("\n[bold blue]Available Agents:[/bold blue]")
    for idx, agent_name in enumerate(AGENTS.keys(), 1):
        console.print(f"{idx}. {agent_name}")

    while True:
        try:
            agent_idx = typer.prompt("Select an agent by number", type=int)
            agent_names = list(AGENTS.keys())
            if 1 <= agent_idx <= len(agent_names):
                selected_name = agent_names[agent_idx - 1]
                return AGENTS[selected_name], selected_name
            console.print("[red]Invalid selection. Please try again.[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number.[/red]")

def display_help():
    """Display available commands and their descriptions."""
    console.print("\n[bold blue]Available Commands:[/bold blue]")
    console.print("  [green]switch[/green] - Switch to a different agent")
    console.print("  [green]help[/green]   - Show this help message")
    console.print("  [green]clear[/green]  - Clear the terminal screen")
    console.print("  [green]memory[/green] - Load previous conversation memory")
    console.print("  [green]exit[/green]   - Exit the program")
    console.print("  [green]quit[/green]   - Exit the program")
    console.print("  [green]q[/green]      - Exit the program")
    console.print("\n[bold blue]Question Format:[/bold blue]")
    console.print("  Add [green]--s[/green] at the end of your question for streaming response")
    console.print("  Example: [dim]What are the top 5 customers? --s[/dim]")
    console.print("\n[dim]Or just type your question to get started![/dim]")

def load_memory() -> SharedMemoryManager:
    """Load conversation memory if it exists."""
    memory = SharedMemoryManager()
    try:
        memory.load()
        console.print("[green]✓ Conversation memory loaded successfully![/green]")
        return memory
    except Exception as e:
        console.print(f"[red]❌ Error loading memory: {str(e)}[/red]")
        return SharedMemoryManager()

@app.callback()
def main(ctx: typer.Context):
    """
    Data Analyst CLI - Your AI-powered data analysis assistant
    """
    if ctx.invoked_subcommand is None:
        interactive()

@app.command()
def init(
    db: str = typer.Option(..., help="Path to SQLite database"),
    metabase_url: str = typer.Option(..., help="Metabase URL, e.g. http://localhost:3000")
):
    """
    Initialize settings config
    """
    cfg = Config.load_or_create()
    cfg.db_path = db
    cfg.metabase_url = metabase_url
    cfg.save()
    typer.secho("✅ Configuration saved successfully!", fg=typer.colors.GREEN, bold=True)
    initialize(cfg)

@app.command(name="ask_data_analyst")
def ask(question: str):
    """
    Ask a natural language question to analyze your data.
    """
    try:        
        # Display the question in a nice panel
        console.print(Panel(
            f"[bold blue]Question:[/bold blue] {question}",
            title="[bold green]Data Analysis Request[/bold green]",
            border_style="green"
        ))
        
        # Show a spinner while processing
        with console.status("[bold green]Analyzing your data...[/bold green]"):
            answer = asyncio.run(Runner.run(sql_analyst, input=question))
        
        # Format and display the SQL query if present
        if hasattr(answer.final_output, 'sql_query') and answer.final_output.sql_query:
            console.print("\n[bold blue]Generated SQL Query:[/bold blue]")
            console.print(Syntax(answer.final_output.sql_query, "sql", theme="monokai", line_numbers=True))
        
        # Format and display the results
        if hasattr(answer.final_output, 'query_results') and answer.final_output.query_results:
            console.print("\n[bold blue]Results:[/bold blue]")
            # Try to parse as JSON for better formatting
            try:
                results = json.loads(answer.final_output.query_results)
                console.print_json(data=results)
            except:
                # If not JSON, display as markdown
                console.print(Markdown(answer.final_output.query_results))
        
        # Add a success message
        console.print("\n[bold green]✓ Analysis complete![/bold green]")
            
    except Exception as e:
        typer.secho(f"❌ Error: {str(e)}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

@app.command(name="ask_data_manager")
def ask(question: str):
    """
    Ask a natural language question to visualise your data.
    """
    try:        
        # Display the question in a nice panel
        console.print(Panel(
            f"[bold blue]Question:[/bold blue] {question}",
            title="[bold green]Dashboard/Visualisation Request[/bold green]",
            border_style="green"
        ))
        
        # Show a spinner while processing
        with console.status("[bold green]Creating visualisations for your data...[/bold green]"):
            answer = asyncio.run(Runner.run(manager, input=question))
        
        # Format and display the SQL query if present
        if answer.final_output:
            console.print("\n[bold blue]Generated Analysis:[/bold blue]")
            console.print(Markdown(answer.final_output))        
        # Add a success message
        console.print("\n[bold green]✓ Analysis complete![/bold green]")
            
    except Exception as e:
        typer.secho(f"❌ Error: {str(e)}", fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

@app.command()
def interactive():
    """
    Start an interactive session with a data analyst agent.
    """
    console.print(Panel(
        "[bold green]Welcome to Data Analyst CLI Interactive Mode![/bold green]\n"
        "You can ask questions about your data and get AI-powered analysis.",
        border_style="green"
    ))
    
    # Initial agent selection
    selected_agent, agent_name = select_agent()
    console.print(f"\nSelected agent: [bold blue]{agent_name}[/bold blue]")
    display_help()

    # Initialize empty memory
    memory = SharedMemoryManager()

    while True:
        try:
            question = typer.prompt("\n>>")
            question = question.strip()
            
            # Check for streaming marker
            is_streaming = question.endswith("--s")
            if is_streaming:
                question = question[:-3].strip()
            
            # Handle special commands
            if question.lower() in {"exit", "quit", "q"}:
                # Save memory before exiting
                if memory.memory.messages:
                    memory.memory.save()
                    console.print("[green]✓ Conversation memory saved![/green]")
                console.print("\n[bold green]Thank you for using Data Analyst CLI! Goodbye! 👋[/bold green]")
                break
            elif question.lower() == "switch":
                console.print("\n[bold blue]Switching agent...[/bold blue]")
                selected_agent, agent_name = select_agent()
                console.print(f"\nSwitched to agent: [bold blue]{agent_name}[/bold blue]")
                display_help()
                continue
            elif question.lower() == "help":
                display_help()
                continue
            elif question.lower() == "clear":
                clear_screen()
                # Redisplay the current agent and help
                console.print(Panel(
                    f"[bold green]Current Agent: {agent_name}[/bold green]",
                    border_style="green"
                ))
                display_help()
                continue
            elif question.lower() == "memory":
                memory = load_memory()
                continue

            # Display the question in a nice panel
            console.print(Panel(
                f"[bold blue]Question:[/bold blue] {question}",
                title=f"[bold green]{agent_name} Request[/bold green]",
                border_style="green"
            ))
            
            memory.append_user(question)
            question = memory.get_chat_input()

            data_context = InputData(
                database_name=settings.DATABASE_NAME, 
                metabase_url=settings.METABASE_URL, 
                metabase_user_name=settings.METABASE_USER_NAME, 
                metabase_password=settings.METABASE_PASSWORD, 
                df=pd.DataFrame(), 
                trained_models={},
                trained_model=None, model_results=[]
            )
            max_turns = 20

            if is_streaming:
                asyncio.run(stream_events(selected_agent, question, context=data_context, max_turns=max_turns))
                continue
            
            # Show a spinner while processing
            with console.status(f"[bold green]{agent_name} is analyzing your data...[/bold green]"):
                answer = asyncio.run(Runner.run(selected_agent, input=question, context=data_context, max_turns=max_turns))
            
            # Format and display the SQL query if present
            if hasattr(answer.final_output, 'sql_query') and answer.final_output.sql_query and agent_name == "SQL Analyst":
                console.print("\n[bold blue]Generated SQL Query:[/bold blue]")
                console.print(Syntax(answer.final_output.sql_query, "sql", theme="monokai", line_numbers=True))
            
            # Format and display the results
            if hasattr(answer.final_output, 'query_results') and answer.final_output.query_results and agent_name == "SQL Analyst":
                console.print("\n[bold blue]Results:[/bold blue]")
                # Try to parse as JSON for better formatting
                try:
                    results = json.loads(answer.final_output.query_results)
                    console.print_json(data=results)
                except:
                    # If not JSON, display as markdown
                    console.print(Markdown(answer.final_output.query_results))

            if answer.final_output and agent_name == "Data Manager":
                console.print("\n[bold blue]Generated Analysis:[/bold blue]")
                console.print(Markdown(answer.final_output))

            if answer.final_output and agent_name == "Data Scientist":
                console.print("\n[bold blue]ML Analysis Report:[/bold blue]")
                ml_report = answer.final_output
                
                # Display Overview
                if hasattr(ml_report, 'baseline_model_results'):
                    console.print("\n[bold cyan]Overview:[/bold cyan]")
                    console.print(Markdown(ml_report.baseline_model_results))
                
                # Display Best Model
                if hasattr(ml_report, 'best_model'):
                    console.print("\n[bold cyan]Best Model:[/bold cyan]")
                    console.print(Markdown(ml_report.best_model))
                
                # Display Feature Importance
                if hasattr(ml_report, 'feature_importance'):
                    console.print("\n[bold cyan]Feature Importance:[/bold cyan]")
                    console.print(Markdown(ml_report.feature_importance))
                
                # Display Next Steps
                if hasattr(ml_report, 'next_steps'):
                    console.print("\n[bold cyan]Next Steps:[/bold cyan]")
                    console.print(Markdown(ml_report.next_steps))
            
            # Add a success message
            console.print("\n[bold green]✓ Analysis complete![/bold green]")

            # Store the conversation in memory
            if hasattr(answer.final_output, 'sql_query') and answer.final_output.sql_query:
                memory.append_assistant(answer.final_output.sql_query)
            if hasattr(answer.final_output, 'query_results') and answer.final_output.query_results:
                memory.append_assistant(answer.final_output.query_results)
            elif answer.final_output:
                # For Data Scientist, store a formatted version of the report
                if agent_name == "Data Scientist":
                    report_parts = []
                    for attr in ['overview', 'data_analysis', 'model_details', 'results', 'recommendations']:
                        if hasattr(answer.final_output, attr):
                            report_parts.append(f"{attr.title()}: {getattr(answer.final_output, attr)}")
                    memory.append_assistant("\n\n".join(report_parts))
                else:
                    memory.append_assistant(str(answer.final_output))

        except Exception as e:
            console.print(f"\n[red]❌ Error: {str(e)}[/red]")
            console.print("[yellow]You can try asking your question differently or type 'help' for available commands.[/yellow]")

if __name__ == "__main__":
    app()
