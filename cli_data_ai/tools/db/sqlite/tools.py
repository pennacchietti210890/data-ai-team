from agents import function_tool
import sqlite3

@function_tool  
def sql_query_tool(query: str) -> str:
    
    """Executes a query SQL statement and return the results

    Args:
        query: The SQL query to execute to retrieve the desired results
    """
    cursor = sqlite3.connect("mock_fin_app_v2.sqlite").cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return str(rows)
    except Exception as e:
        return f"Error executing query: {e}"

@function_tool
def describe_database() -> str:
    """Describe the DataBase schema by listing tables available and their attributes
    """
    cursor = sqlite3.connect("mock_fin_app.sqlite").cursor()
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    db_description = {}

    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()
        db_description[table] = [{"column_name": col[1], "type": col[2]} for col in columns]

    return db_description

@function_tool
def profile_database()-> str:    
    """Describe in detail the possible values that the columns of the tables in the DataBase can assume. For example possible transaction types etc
    """
    cursor = sqlite3.connect("mock_fin_app.sqlite").cursor()
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    max_unique_values = 20
    db_profile = {}

    for table in tables:
        table_info = []
        cursor.execute(f"PRAGMA table_info({table});")
        columns = cursor.fetchall()

        for col in columns:
            column_name = col[1]
            col_type = col[2]

            # Try to detect distinct values if it's TEXT or looks categorical
            cursor.execute(f"SELECT COUNT(DISTINCT {column_name}) FROM {table};")
            distinct_count = cursor.fetchone()[0]

            # If not too many distinct values, fetch them
            sample_values = []
            if distinct_count <= max_unique_values:
                cursor.execute(f"SELECT DISTINCT {column_name} FROM {table} LIMIT {max_unique_values};")
                sample_values = [row[0] for row in cursor.fetchall()]

            table_info.append({
                "column_name": column_name,
                "type": col_type,
                "distinct_count": distinct_count,
                "sample_values": sample_values
            })

        db_profile[table] = table_info

    return db_profile