from fastapi import APIRouter

from dependencies import AvailabilityServiceDependency, HttpClientDependency
from schemas.availability_response import AvailabilityResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/{product_id}/availability", response_model=AvailabilityResponse)
async def get_product_availability(
    product_id: int,
    client: HttpClientDependency,
    service: AvailabilityServiceDependency,
) -> AvailabilityResponse:
    return await service.get_availability(client, product_id)