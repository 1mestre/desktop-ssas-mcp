"""
Sanitizing launcher for the Power BI Desktop Local MCP Server.

This wrapper:
1. Clears PYTHONPATH/PYTHONHOME to prevent host-environment conflicts
2. Prioritizes the local .venv site-packages directory
3. Launches the MCP server via server.py

Usage:
    .venv\\Scripts\\python.exe launch.py
"""

import os
import sys

for key in ["PYTHONPATH", "PYTHONHOME"]:
    os.environ.pop(key, None)

base_dir = os.path.dirname(os.path.abspath(__file__))
venv_site_packages = os.path.join(base_dir, ".venv", "Lib", "site-packages")
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

if __name__ == "__main__":
    from server import mcp
    mcp.run()
