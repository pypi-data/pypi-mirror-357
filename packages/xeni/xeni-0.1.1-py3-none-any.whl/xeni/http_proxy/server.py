from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os
import logging
from dotenv import load_dotenv

from xeni.http_proxy.endpoints import insert, search, healthcheck

load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Testing imports
ENVIRONMENT = os.getenv("ENVIRONMENT")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting local Xeni server.")
    yield
    logger.info("Shutting down Xeni server...")

server = FastAPI(title="http-proxy server",
                  description="An http server to relay context to main ArchiveNet",
                  version="0.1.0",
                  docs_url="/docs",
                  redoc_url="/redoc",
                  lifespan=lifespan)

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server.include_router(insert.router)
server.include_router(search.router)
server.include_router(healthcheck.router)

def start_server(port: int = 8000, host: str = "127.0.0.1"):
    uvicorn.run(server, host=host, port=port)

if __name__ == "__main__": 
    start_server()