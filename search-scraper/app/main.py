from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.core.browser import start_browser, stop_browser


@asynccontextmanager
async def lifespan(app: FastAPI):

    await start_browser()

    yield

    await stop_browser()


app = FastAPI(
    title="Search Scraper",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)