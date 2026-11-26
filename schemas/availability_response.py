from pydantic import BaseModel

class AvailabilityResponse(BaseModel):
    product_id: int
    stock: int
    price: float
    warehouse_available: bool
