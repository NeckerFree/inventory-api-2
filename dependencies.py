from typing import Annotated

import httpx
from fastapi import Depends, Request

from services.availability_service import AvailabilityService


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_availability_service() -> AvailabilityService:
    return AvailabilityService()


HttpClientDependency = Annotated[
    httpx.AsyncClient,
    Depends(get_http_client),
]

AvailabilityServiceDependency = Annotated[
    AvailabilityService,
    Depends(get_availability_service),
]
