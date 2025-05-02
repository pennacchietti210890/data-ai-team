import typer
from agents import Runner
from cli_data_ai.agents.data_analysts.sql_analyst import sql_analyst
from cli_data_ai.agents.data_analysts.dashboard_analyst import dashboard_analyst
from cli_data_ai.agents.data_analysts.team import manager
import asyncio
import os
from cli_data_ai.utils.config import settings, get_settings
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
import json
from cli_data_ai.memory.memory import SharedMemoryManager

app = typer.Typer(help="Data Analyst CLI", invoke_without_command=True)
console = Console()

# Define available agents
AGENTS = {
    "SQL Analyst": sql_analyst,
    "Data Manager": manager,
    # Add more agents here as they become available
}

# Initialize memory manager
memory = SharedMemoryManager()

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
    console.print("  [green]exit[/green]   - Exit the program")
    console.print("  [green]quit[/green]   - Exit the program")
    console.print("  [green]q[/green]      - Exit the program")
    console.print("\n[dim]Or just type your question to get started![/dim]")

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

    while True:
        try:
            question = typer.prompt("\n>>")
            question = question.strip().lower()
            memory.append_user(question)
            chat_input = memory.get_chat_input()
            # Handle special commands
            if question in {"exit", "quit", "q"}:
                console.print("\n[bold green]Thank you for using Data Analyst CLI! Goodbye! 👋[/bold green]")
                break
            elif question == "switch":
                console.print("\n[bold blue]Switching agent...[/bold blue]")
                selected_agent, agent_name = select_agent()
                console.print(f"\nSwitched to agent: [bold blue]{agent_name}[/bold blue]")
                display_help()
                continue
            elif question == "help":
                display_help()
                continue
            elif question == "clear":
                clear_screen()
                # Redisplay the current agent and help
                console.print(Panel(
                    f"[bold green]Current Agent: {agent_name}[/bold green]",
                    border_style="green"
                ))
                display_help()
                continue

            # Display the question in a nice panel
            console.print(Panel(
                f"[bold blue]Question:[/bold blue] {question}",
                title=f"[bold green]{agent_name} Request[/bold green]",
                border_style="green"
            ))
            
            # Show a spinner while processing
            with console.status(f"[bold green]{agent_name} is analyzing your data...[/bold green]"):
                answer = asyncio.run(Runner.run(selected_agent, input=chat_input))
            
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

            memory.append_assistant(answer.final_output)
            
            # Add a success message
            console.print("\n[bold green]✓ Analysis complete![/bold green]")

        except Exception as e:
            console.print(f"\n[red]❌ Error: {str(e)}[/red]")
            console.print("[yellow]You can try asking your question differently or type 'help' for available commands.[/yellow]")

if __name__ == "__main__":
    app()
