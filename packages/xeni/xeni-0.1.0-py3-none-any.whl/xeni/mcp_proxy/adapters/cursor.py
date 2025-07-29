import json 
import os

from xeni.mcp_proxy.adapters.base import BaseAdapterClass

class CursorAdapter(BaseAdapterClass):

    def __init__(self, agent_name, scope="global"):
        super().__init__(agent_name)
        self.scope = scope
        
    def configure_mcp(self, mcp_server_path: str = None):
        """Configuration logic for cursor desktop"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        mcp_server_directory = os.path.abspath(os.path.join(current_dir, '..'))
        if self.scope == "global":
            config_path = os.path.join(os.path.expanduser("~"), 
                                   ".cursor", "mcp.json")
        elif self.scope == "local":
            config_path = os.path.join(mcp_server_path, "mcp.json")
        module_path = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))

        if config_path: 
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
                        "env": {
                            "PYTHONPATH": module_path,
                        }
                    }
                }
            }
            
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            return False
        return True
        
    