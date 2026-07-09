import os
import sys

# Sanitize environment variables before any other imports.
# This prevents host environments (like AI agent runners, IDEs, or global shells)
# from injecting contaminating PYTHONPATH or PYTHONHOME variables, which can lead 
# to ModuleNotFoundErrors (e.g. with pywintypes/pythonnet).
for key in ['PYTHONPATH', 'PYTHONHOME']:
    os.environ.pop(key, None)

# Automatically resolve and prioritize local virtual environment packages if present.
base_dir = os.path.dirname(os.path.abspath(__file__))
venv_site_packages = os.path.join(base_dir, ".venv", "Lib", "site-packages")
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# ---------------------------------------------------------
# Standard MCP Imports
# ---------------------------------------------------------
from mcp.server.fastmcp import FastMCP
from pbi_connector import get_active_pbi_instances, PowerBIConnector

# Initialize FastMCP Server
mcp = FastMCP("PowerBI Desktop Local")

@mcp.tool()
def list_instances() -> list[dict]:
    """Scans and lists active local Power BI Desktop instances on the machine.

    Returns:
        list[dict]: Active Power BI instances with their local Analysis Services port and workspace path.
    """
    instances = get_active_pbi_instances()
    return instances

@mcp.tool()
def get_schema(port: str) -> list[dict]:
    """Retrieves the data model schema (tables and columns) from the specified Power BI Desktop port.

    Args:
        port (str): Local port of the active Power BI Desktop instance.

    Returns:
        list[dict]: Tables metadata and column details.
    """
    connector = PowerBIConnector(port)
    schema = connector.get_model_schema()
    return schema

@mcp.tool()
def execute_dax(port: str, query: str) -> list[dict]:
    """Executes a custom DAX query against the specified local Power BI Desktop instance.

    Args:
        port (str): Local port of the active Power BI Desktop instance.
        query (str): The DAX query (e.g. "EVALUATE 'TableName'").

    Returns:
        list[dict]: JSON-serializable list of row dictionaries matching the query results.
    """
    connector = PowerBIConnector(port)
    results = connector.execute_query(query)
    
    # Process results to guarantee JSON serializability for MCP
    clean_results = []
    for row in results:
        clean_row = {}
        for k, v in row.items():
            if v is None:
                clean_row[k] = None
            elif type(v).__name__ == 'Decimal':
                clean_row[k] = float(v)
            elif 'time' in type(v).__name__.lower() or 'date' in type(v).__name__.lower():
                clean_row[k] = str(v)
            else:
                clean_row[k] = v
        clean_results.append(clean_row)
        
    return clean_results

if __name__ == "__main__":
    mcp.run()
