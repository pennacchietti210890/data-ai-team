# Data AI CLI

LLM-powered command-line interface tool that lets you interact with your data using natural language, using the OpenAI Agent SDK. 

## A CLI Data Analyst to chat with your data 

<h1>
  <img src="assets/data_analyst_example_cli.png"/>
</h1>

## A CLI Dashboard analyst to visualize your data

<h1>
  <img src="assets/data_visualisation_analyst_cli.png"/>
</h1>

<h1>
  <img src="assets/example_dashboard.png"/>
</h1>

## A CLI Data Scientist to model your data

<h1>
  <img src="assets/data_scientist_example_cli.png"/>
</h1>

## Features

- **SQL Generation**: Automatically generates and executes SQL queries based on your questions
- **Charts and dashboard generation**: Automatically generates Charts and Dashboards using Metabase API
- **Data Science analysis**: Automatically generates data science model reports
- **Clear CLI Interface**: Rich, colorful output with syntax highlighting and formatted results

## Prerequisites

- Python 3.12 or higher
- Poetry (Python package manager)
- An OpenAI API key
- SQLite database (or other supported database)
- For visualisations, a Metabase interface connected to your DB

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd data-ai-team
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Create a `.env` file in the project root with your configuration:
```env
# Database
DATABASE_URL=path/to/your/database.sqlite

# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key

# Application settings
DEBUG=true
```

## Usage

### Run the Tool

Run the tool with the following command;

```bash
poetry run data-analyst-cli
```

The tool will:

1. Display the available agents
2. Once selected the agent, the options available
3. Once the question has been asked, results are displayed in a nicely formatted way

### Example Questions

Here are some example questions you can ask:

- "What's the total revenue for Q1 2024?"
- "Show me the top 5 customers by transaction volume"
- "What's the average transaction amount per day?"
- "Compare monthly transaction volumes between 2023 and 2024"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Powered by [OpenAI](https://openai.com/) and [OpenAI Agent SDK](https://github.com/openai/openai-python)
- Styled with [Rich](https://github.com/Textualize/rich)
