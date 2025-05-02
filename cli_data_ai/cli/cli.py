import typer
from agents import Runner
from cli_data_ai.agents.data_analysts.sql_analyst import sql_analyst
from cli_data_ai.agents.data_analysts.dashboard_analyst import dashboard_analyst
from cli_data_ai.agents.data_analysts.team import manager
import asyncio
from cli_data_ai.utils.config import settings, get_settings
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
import json

app = typer.Typer(help="Data Analyst CLI")
console = Console()

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

@app.command(name="ask_dashboard_analyst")
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
            answer = asyncio.run(Runner.run(dashboard_analyst, input=question))
        
        # Format and display the SQL query if present
        if hasattr(answer.final_output, 'chart_link') and answer.final_output.chart_link:
            console.print("\n[bold blue]Generated Visualisation Link:[/bold blue]")
            console.print(Markdown(answer.final_output.chart_link))        
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

if __name__ == "__main__":
    app()
