"""Claude config adapter for MCP Proxy."""
import json 
import os

from xeni.utils.file_manager import ConfigFinder
from xeni.mcp_proxy.adapters.base import BaseAdapterClass

class ClaudeAdapter(BaseAdapterClass):

    def __init__(self, agent_name):
        super().__init__(agent_name)

    def configure_mcp(self, mcp_server_path: str = None):
        """Configuration logic for claude desktop"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        mcp_server_path = os.path.abspath(os.path.join(current_dir, '..'))

        cf = ConfigFinder("claude")
        config_path = cf.get_path()
        if not config_path:
            # ask user for permission to search the whole system
            config_path = cf.system_search()
        
        if config_path: 
            config = {
            "mcpServers": {
                "Xeni": {
                    "command": "uv",
                    "args": [
                        "--directory",
                        mcp_server_path,
                        "run",
                        "server.py"
                    ]
                }
            }
        }
            
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            return False
        return True
        
    