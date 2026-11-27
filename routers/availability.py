#file: routers/availability.py
from fastapi import APIRouter, HTTPException

from dependencies import AvailabilityServiceDependency, HttpClientDependency
from schemas.availability_response import AvailabilityResponse
from exceptions.availability_timeout_error import AvailabilityTimeOutError

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/{product_id}/availability", response_model=AvailabilityResponse)
async def get_product_availability(
    product_id: int,
    client: HttpClientDependency,
    service: AvailabilityServiceDependency,
) -> AvailabilityResponse:
    try:
        return await service.get_availability(client, product_id)
    except AvailabilityTimeOutError as exc:
        raise HTTPException(
            status_code=504,
            detail= "Availability aggregation timed out",
        ) from exc