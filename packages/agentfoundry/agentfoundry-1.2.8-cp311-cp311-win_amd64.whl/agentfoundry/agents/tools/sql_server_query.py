import pyodbc
import json

from langchain_core.tools import Tool


def query_sql_server_generic(query: str) -> str:
    """
    Connects to a SQL database using a file path provided in the input JSON, executes the SQL query,
    and returns the fetched rows as a string.

    The input should be a JSON string with the following keys:
      - "file_path": full path to the SQLite database file.
      - "query": a syntactically correct SQL query to execute.

    Example input:
    {
        "file_path": "./quantumdrive/data/chinook.sqlite",
        "query": "SELECT c.Country, SUM(i.Total) AS TotalSpent FROM Customer c JOIN Invoice i ON c.CustomerId = i.CustomerId GROUP BY c.Country ORDER BY TotalSpent DESC LIMIT 3;"
    }
    """
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=yes;"
        )
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return str(rows)
    except Exception as e:
        return f"Error executing query: {e}"


# Wrap the function as a LangChain Tool.
sqlite_tool = Tool(
    name="sql_server_query",
    func=query_sql_server_generic,
    description=(
        "Executes a SQL query on a SQL Server database."
        "Input must be a string containing the SQL query to execute on a SQL Server. The connection for the database "
        "is already up and available including the database name. The function returns the query result as a string."
    )
)

