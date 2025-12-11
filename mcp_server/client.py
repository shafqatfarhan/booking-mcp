"""
API client for Booking.com.
"""

import logging
import os

import httpx
# from functools import wraps
from typing import Literal

# from tenacity import retry, retry_if_exception_type
# from tenacity.stop import stop_after_attempt
# from tenacity.wait import wait_incrementing

logger = logging.getLogger(__name__)


class RapidAPIClient:
    """Custom RapidAPI client using httpx."""

    def __init__(self, enable_retries: bool = False):
        """
        Initialize the client with API configuration from the environment file.
        """
        self.api_key = os.getenv("RAPIDAPI_KEY")
        self.api_host = os.getenv("RAPIDAPI_HOST")
        self.api_timeout = int(os.getenv("API_TIMEOUT_IN_SECONDS") or 10)
        self.enable_retries = enable_retries
        self.session = httpx.AsyncClient()

    async def __aenter__(self) -> RapidAPIClient:
        return self

    async def __aexit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        await self.close()

    async def close(self):
        if self.session:
            await self.session.aclose()

    # def conditional_retry(method):
    #     """Retry decorator that applies retry logic if retries are enabled."""

    #     @wraps(method)
    #     def _conditional_retry(self, *args, **kwargs):
    #         if self.enable_retries:
    #             return retry(
    #                 stop=stop_after_attempt(3),
    #                 wait=wait_incrementing(start=2, increment=2),
    #                 retry=retry_if_exception_type(
    #                     (Exception)
    #                 ),
    #                 reraise=True,
    #             )(method)(self, *args, **kwargs)
    #         else:
    #             return method(self, *args, **kwargs)  # pylint: disable=not-callable

    #     return _conditional_retry   

    async def _make_request(
        self,
        method: Literal["GET", "POST"],
        endpoint: str,
        params: dict | None = None,
    ) -> dict:
        """
        Make an HTTP request to the Rapid API

        Args:
            method (str): HTTP method (e.g., "GET", "POST").
            endpoint (str): API endpoint.
            params (dict | None): Query parameters.
        Returns:
            dict: JSON response from the API
        """
        url = f"https://{self.api_host}{endpoint}" #try removing https
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.api_host,
            "Content-Type": "application/json"
        }
        
        logger.info(f"Making API request to {endpoint} with params: {params}")
        #async with httpx.AsyncClient() as client:
        async with self.session as client:
            try:
                response = await client.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.api_timeout,
                )

                # Read response body before raising for status
                try:
                    response_data = response.json()
                except (ValueError, AttributeError):
                    response_data = response.text

                response.raise_for_status()
                return response_data
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                message = str(e)
                
                # Try to get error details from response body
                try:
                    error_data = e.response.json()
                    api_message = error_data.get("message", error_data.get("error", error_data.get("detail", str(e))))
                    message = f"{message} | API Error: {api_message}"
                    error_result = {
                        "error": True,
                        "error_message": message,
                        "status_code": status_code,
                        "error_data": error_data
                    }
                except (ValueError, AttributeError):
                    response_text = e.response.text[:500] if hasattr(e.response, 'text') else None
                    message = f"{message} | Response: {response_text}"
                    error_result = {
                        "error": True,
                        "error_message": message,
                        "status_code": status_code,
                    }
                
                logger.error(f"API request to {endpoint} failed with status {status_code}: {error_result}")
                return error_result
            except Exception as e:
                message = str(e)
                error_result = {"error": True, "error_message": message}
                logger.error(f"Exception raised from the API endpoint {endpoint} with params: {params}. Error: {error_result}")
                return error_result
            finally:
                await self.close()

    #@conditional_retry
    async def get_destination_by_name(
        self,
        query: str,
    ) -> dict:
        """Search for destinations by name."""
        logger.info(f"Searching for destinations with query: {query}")

        endpoint = "/v1/hotels/locations"
        params = {"name": query, "locale": "en-gb"}
        return await self._make_request("GET", endpoint, params=params)

    async def get_hotels_by_destination_id(
        self,
        destination_id: str, 
        checkin_date: str, 
        checkout_date: str, 
        adults: int = 2
    ) -> dict:
        """Get hotels for a specific destination."""

        logger.info(f"Getting hotels for destination_id: {destination_id}, checkin: {checkin_date}, checkout: {checkout_date}, adults: {adults}")
        endpoint = "/v1/hotels/search"

        params = {
            "adults_number": adults,
            "units": "metric",
            "page_number": 0,
            "checkin_date": checkin_date,
            "checkout_date": checkout_date,
            "dest_type": "city",
            "dest_id": destination_id,
            "order_by": "popularity",
            "include_adjacency": "true",
            "room_number": 1,
            "filter_by_currency": "USD",
            "locale": "en-gb"
        }
        
        return await self._make_request("GET", endpoint, params=params)
