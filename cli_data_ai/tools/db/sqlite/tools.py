from agents import function_tool
import sqlite3
from cli_data_ai.agents.context.context import InputData
from agents import RunContextWrapper

@function_tool  
def sql_query_tool(wrapper: RunContextWrapper[InputData],query: str) -> str:
    
    """Executes a query SQL statement and return the results

    Args:
        query: The SQL query to execute to retrieve the desired results
    """
    cursor = sqlite3.connect(f"{wrapper.context.database_name}.sqlite").cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchmany(10)
        return str(rows)
    except Exception as e:
        return f"Error executing query: {e}"

@function_tool
def describe_database(wrapper: RunContextWrapper[InputData]) -> str:
    """Describe the DataBase schema by listing tables available and their attributes
    """
    cursor = sqlite3.connect(f"{wrapper.context.database_name}.sqlite").cursor()
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
def profile_database(wrapper: RunContextWrapper[InputData]) -> str:    
    """Describe in detail the possible values that the columns of the tables in the DataBase can assume. For example possible transaction types etc
    """
    cursor = sqlite3.connect(f"{wrapper.context.database_name}.sqlite").cursor()
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

@function_tool
def create_table(wrapper: RunContextWrapper[InputData], create_query: str) -> str:
    """
    Create a new table in the database using a CREATE TABLE AS SELECT SQL statement.

    Args:
        create_query: The SQL query to create the table.
    """
    try:
        if wrapper.context.human_confirmation:
            conn = sqlite3.connect(f"{wrapper.context.database_name}.sqlite")
            cursor = conn.cursor()
            cursor.execute(create_query)
            conn.commit()
            return "✅ Table created successfully."
        else:
            return "❌ Human confirmation required. Please confirm the action."
    except Exception as e:
        return f"❌ Error creating table: {e}"
    finally:
        conn.close()

@function_tool
def drop_table(wrapper: RunContextWrapper[InputData], table_name: str) -> str:
    """
    Drop a table from the database.

    Args:
        table_name: Name of the table to be dropped.
    """
    try:
        if wrapper.context.human_confirmation:
            conn = sqlite3.connect(f"{wrapper.context.database_name}.sqlite")
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            conn.commit()
            return f"✅ Table '{table_name}' dropped successfully."
        else:
            return "❌ Human confirmation required. Please confirm the action."
    except Exception as e:
        return f"❌ Error dropping table: {e}"
    finally:
        conn.close()

@function_tool
def update_records(wrapper: RunContextWrapper[InputData], update_query: str) -> str:
    """
    Update records in a table using a valid UPDATE SQL query.

    Args:
        update_query: SQL UPDATE statement with WHERE clause recommended.
    """
    try:
        if wrapper.context.human_confirmation:
            conn = sqlite3.connect(f"{wrapper.context.database_name}.sqlite")
            cursor = conn.cursor()
            cursor.execute(update_query)
            conn.commit()
            return f"✅ Records updated successfully. Rows affected: {cursor.rowcount}"
        else:
            return "❌ Human confirmation required. Please confirm the action."
    except Exception as e:
        return f"❌ Error updating records: {e}"
    finally:
        conn.close()

@function_tool
def insert_record(wrapper: RunContextWrapper[InputData], insert_query: str) -> str:
    """
    Insert new record(s) into a table using a valid INSERT INTO SQL statement.

    Args:
        insert_query: SQL INSERT statement.
    """
    try:
        if wrapper.context.human_confirmation:
            conn = sqlite3.connect(f"{wrapper.context.database_name}.sqlite")
            cursor = conn.cursor()
            cursor.execute(insert_query)
            conn.commit()
            return f"✅ Record inserted successfully. Row ID: {cursor.lastrowid}"
        else:
            return "❌ Human confirmation required. Please confirm the action."
    except Exception as e:
        return f"❌ Error inserting record: {e}"
    finally:
        conn.close()

@function_tool
def delete_records(wrapper: RunContextWrapper[InputData], delete_query: str) -> str:
    """
    Delete record(s) from a table using a valid DELETE SQL statement.

    Args:
        delete_query: SQL DELETE statement with WHERE clause recommended.
    """
    try:
        if wrapper.context.human_confirmation:
            conn = sqlite3.connect(f"{wrapper.context.database_name}.sqlite")
            cursor = conn.cursor()
            cursor.execute(delete_query)
            conn.commit()
            return f"✅ Records deleted successfully. Rows affected: {cursor.rowcount}"
        else:
            return "❌ Human confirmation required. Please confirm the action."
    except Exception as e:
        return f"❌ Error deleting records: {e}"
    finally:
        conn.close()