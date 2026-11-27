#file: services/availability_service.py
import asyncio
import random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx

from exceptions.availability_timeout_error import AvailabilityTimeOutError
from schemas.availability_response import AvailabilityResponse

pricing_semaphore = asyncio.Semaphore(10)
PRICE_ATTEMPTS=3
RETRY_DELAY=0.25

def retry_after_seconds(value: str | None) -> float | None:
    if not value:
        return None

    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None

class AvailabilityService:
        async def get_price(
                 self,
                 client: httpx.AsyncClient,
                 product_id: int,
                 deadline:float, 
        ) -> float:
            loop=asyncio.get_running_loop()

            for attempt in range(1, PRICE_ATTEMPTS+1):
                try:
                    async with pricing_semaphore:
                        response = await client.get(
                            f"https://pricing.example.com/products/{product_id}"
                        )
                        response.raise_for_status()
                        return response.json()["price"]
                    
                except (httpx.HTTPStatusError,
                        httpx.NetworkError,
                        httpx.TimeoutException
                        ) as exc:
                    retry_after=None
                    if isinstance(exc, httpx.HTTPStatusError):
                        if exc.response.status_code not in  {429, 500, 502, 503, 504}:
                            raise
                        
                        retry_after =retry_after_seconds(exc.response.headers.get("Retry-After"))
                    if attempt == PRICE_ATTEMPTS:
                        raise

                    backoff=RETRY_DELAY*(2** (attempt-1))
                    delay=max(backoff+random.uniform(0.0, backoff), retry_after or 0.0)
                    if delay >= deadline - loop.time():
                        raise

                    await asyncio.sleep(delay)

            raise RuntimeError("Pricing retries exhausted unexpectedly")
        
        async def get_stock(self, product_id: int) -> int:
            ...

        async def get_warehouse_availability(self, product_id: int) -> bool:
            ...

        async def get_availability(
        self,
        client: httpx.AsyncClient,
        product_id: int,
    ) -> AvailabilityResponse:
            loop=asyncio.get_running_loop()
            deadline=loop.time()+ 8.0
            timeout_context=asyncio.timeout_at(deadline)
            try:
                async with timeout_context:
                    stock, price, warehouse_available = await asyncio.gather(
                    self.get_stock(product_id),
                    self.get_price(client,product_id, deadline),
                    self.get_warehouse_availability(product_id),
                )
            except Exception as exc:
                if not timeout_context.expired():
                    raise
                raise AvailabilityTimeOutError("Availability aggregation exceeded its 8-second deadline") from exc
             
            return AvailabilityResponse(
                product_id=product_id,
                stock=stock,
                price=price,
                warehouse_available=warehouse_available,
            )