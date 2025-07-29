"""Main logic for the MCP Proxy server."""
import httpx
import sys
from mcp.server.fastmcp import FastMCP

from xeni.utils.models import ContextData, ContextQuery, ContextResponse

mcp = FastMCP("Xeni")

HTTP_PROXY_URL = "http://127.0.0.1:3000" 

@mcp.tool()
async def search(query: ContextQuery) -> ContextResponse:
    """Search for a query using the MCP Proxy."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{HTTP_PROXY_URL}/context/search",
                json=query.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return ContextResponse(**response.json())
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        return {"Error": f"HTTP error occurred: {str(e)}"}
    except Exception as e:
        return ContextResponse(
            success=False,
            message=f"An error occurred: {str(e)}",
            data=[]
        )

@mcp.tool()
async def insert(data: ContextData) -> None:
    """Insert data into the MCP Proxy."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{HTTP_PROXY_URL}/context/insert",
                json=data.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return ContextResponse(**response.json())
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}", file=sys.stderr)
        return {"Error": f"HTTP error occurred: {str(e)}"}
    except Exception as e:
        return ContextResponse(
            success=False,
            message=f"An error occurred: {str(e)}",
            data=[]
        )
    
if __name__ == "__main__":
    # Start the MCP server
    try:
        print("Starting Xeni MCP server...", file=sys.stderr)
        # Start the MCP server
        mcp.run(transport="stdio")
    except Exception as e:
        print(f"Failed to start MCP server: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
