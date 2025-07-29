import json
import os
import platform

from xeni.utils.config import AGENT_CONFIG_FILENAMES
from xeni.mcp_proxy.adapters.base import BaseAdapterClass

class ClineAdapter(BaseAdapterClass):
    """
    Adapter for the Cline client to configure connection to the Python MCP server.
    """

    def __init__(self, agent_name, scope="global"):
        super().__init__(agent_name)
        self.scope = scope

    def configure_mcp(self, mcp_server_path: str = None):
        """
        Sets up configuration for the MCP server (Python backend).
        Writes config JSON with launch details for MCP server.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        mcp_server_directory = os.path.abspath(os.path.join(current_dir, '..'))
        system = platform.system().lower()
    
        absolute_path = ""    
        if system == "darwin":  # macOS
            absolute_path = os.path.expanduser("~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings")
        elif system == "windows":  # Windows
            appdata = os.environ["APPDATA"]
            absolute_path = os.path.join(appdata, "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings")
        elif system == "linux":  # Linux
            absolute_path = os.path.expanduser("~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings")
        
        config_path = os.path.join(absolute_path, AGENT_CONFIG_FILENAMES[self.agent_name]) 

        # Assume the MCP server entrypoint is server.py
        module_path = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        print(f"Module path for MCP server: {module_path}")
        config = {
            "mcpServers": {
                "Xeni": {
                    "command": "uv",
                    "args": [
                        "--directory",
                        mcp_server_directory,
                        "run",
                        "server.py"
                    ],
                    "cwd": mcp_server_directory,
                    "env": {
                        "PYTHONPATH": module_path,
                    }
                }
            }
        }
        print(f"Writing MCP config to: {config_path}")
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print("Error writing MCP config:", e)
            return False

        return True
        