from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.utils.logger import setup_logger
from app.context.context_helpers.get_canonmap_helper import get_canonmap

logger = setup_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.canonmap = get_canonmap()
    logger.info("CanonMap initialized (from API context)")
    yield