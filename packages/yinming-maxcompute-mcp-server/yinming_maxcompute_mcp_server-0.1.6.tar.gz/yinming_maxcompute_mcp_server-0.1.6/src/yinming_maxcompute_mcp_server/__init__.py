from odps import ODPS
from mcp.server.fastmcp import FastMCP
import os

odps = ODPS(
    os.getenv('ALIYUN_ACCESS_KEY_ID'),
    os.getenv('ALIYUN_ACCESS_KEY_SECRET'),
    project=os.getenv('ALIYUN_MAXCOMPUTE_PROJECT_NAME'),
    endpoint=os.getenv('ALIYUN_MAXCOMPUTE_ENDPOINT'),
)


mcp = FastMCP(
    name="MaxcomputeAssistant",
    instructions="maxcompute assistant is a professional MaxCompute data warehouse assistant, helping users run MaxCompute SQL queries.",
)


@mcp.tool(name="run_sql", description="Run a SQL query on the MaxCompute data warehouse.")
def run_sql(sql: str) -> str:
    """Run a SQL query on the MaxCompute data warehouse.
    Args:
        sql: The SQL query to run.
    """

    result = []
    with odps.execute_sql(sql).open_reader(tunnel=False) as reader:
        for record in reader:
            result.append(record)

    return result

@mcp.tool(name="list_tables", description="List all tables in the database.")
def list_tables(prefix: str = "") -> str:
    """List all tables in the database. If a prefix is provided, only tables with that prefix will be listed.
    Args:
        prefix: The prefix of the table name.
    """

    tables = []
    for table in odps.list_tables(prefix=prefix):
        tables.append(table.name)

    return "\n".join(tables)


@mcp.tool(name="show_version", description="Show the version of the mcp server")
def show_version() -> str:
    """Show the version of the mcp server.
    """

    return "0.1.6"


def main():
    mcp.run(transport="stdio")
