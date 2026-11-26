
import asyncio

import httpx

from schemas.availability_response import AvailabilityResponse

pricing_semaphore = asyncio.Semaphore(10)


class AvailabilityService:
    async def get_availability(
        self,
        client: httpx.AsyncClient,
        product_id: int,
    ) -> AvailabilityResponse:
        async def get_price() -> float:
            async with pricing_semaphore:
                response = await client.get(
                    f"https://pricing.example.com/products/{product_id}"
                )
                response.raise_for_status()
                return response.json()["price"]

        async def get_stock() -> int:
            raise NotImplementedError("Stock lookup is not implemented")

        async def get_warehouse_availability() -> bool:
            raise NotImplementedError(
                "Warehouse availability lookup is not implemented"
            )

        stock, price, warehouse_available = await asyncio.gather(
            get_stock(),
            get_price(),
            get_warehouse_availability(),
        )
        return AvailabilityResponse(
            product_id=product_id,
            stock=stock,
            price=price,
            warehouse_available=warehouse_available,
        )