from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import get_settings
from app.core.logging import setup_logging, logger
from app.db.postgres import init_db
from app.db.weaviate import get_weaviate_client
from app.api import ingest, search, qa

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info("startup_event", message="Initializing application")
    
    # Init Postgres
    logger.info("postgres_init")
    await init_db()
    
    # Init Weaviate Schema
    # Note: access weaviate inside docker network
    try:
        w_client = get_weaviate_client()
        w_client.init_schema()
        w_client.close()
    except Exception as e:
        logger.error("weaviate_init_failed", error=str(e))
        # Don't crash, might be temporary connection issue or race condition with docker up
    
    yield
    # Shutdown
    logger.info("shutdown_event", message="Shutting down application")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(ingest.router, prefix=f"{settings.API_V1_STR}/ingest", tags=["Ingest"])
app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["Search"])
app.include_router(qa.router, prefix=f"{settings.API_V1_STR}/qa", tags=["QA"])

@app.get("/")
async def root():
    return {"message": "Kimochi RAG System Ready"}
