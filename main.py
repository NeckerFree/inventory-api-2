from contextlib import asynccontextmanager

import httpx

from fastapi import FastAPI

from routers import availability

@asynccontextmanager
async def lifespan(app: FastAPI):
    limits = httpx.Limits(
    max_connections=100,
    max_keepalive_connections=20,
    )

    timeout = httpx.Timeout(
        connect=2.0,
        read=5.0,
        write=3.0,
        pool=1.0,
    )

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        app.state.http_client = client
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(availability.router)