import typer
from .config import Config
from .main import initialize, ask_question

app = typer.Typer(help="Data Analyst CLI")

@app.command()
def init(
    db: str = typer.Option(..., help="Path to SQLite database"),
    metabase_url: str = typer.Option(..., help="Metabase URL, e.g. http://localhost:3000")
):
    """
    Initialize config for DB and Metabase.
    """
    cfg = Config.load_or_create()
    cfg.db_path = db
    cfg.metabase_url = metabase_url
    cfg.save()
    typer.secho("Configuration saved.", fg=typer.colors.GREEN)
    initialize(cfg)

@app.command()
def ask(question: str):
    """
    Ask a natural language question.
    """
    cfg = Config.load_or_fail()
    answer = ask_question(cfg, question)
    typer.echo(answer)

if __name__ == "__main__":
    app()
