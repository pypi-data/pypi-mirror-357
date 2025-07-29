from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import os
import httpx
import json

from xeni.utils.config import ConfigManager, EIZEN_URL
from xeni.utils.models  import ContextData

router = APIRouter()
base_url = EIZEN_URL
headers = {}
config = ConfigManager("", "").load_config_path()
with open(config, 'r') as f:
    config = json.load(f)
    headers["Authorization"] = config.get("Authorization", "")
    headers["x-contract-id"] = config.get("x-contract-id", "")
    headers["Content-Type"] = "application/json"
# Create a new client and connect to the server

@router.post("/context/insert")
async def insert_context(data:ContextData)-> JSONResponse:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{base_url}/insert",
            json= data.model_dump(mode="json"),
            headers = headers
        )
    if response.status_code == 200:
        return JSONResponse(content=response.json())
    else:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )
