"""
This file initializes the FastMCP server, sets up authentication, logging,
and registers the custom Booking.com MCP tools for searching destinations
and hotels via the Booking.com API.
"""

import logging

from dotenv import load_dotenv
from fastmcp import Context, FastMCP, settings
from typing import Any, Dict, List, Union
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from uvicorn.config import Config
    

from mcp_server.client import RapidAPIClient
from mcp_server.middleware import AuthMiddleware
from mcp_server.types import HotelItem, LocationItem
from mcp_server.utils import setup_logging

# Load environment variables from .env file
load_dotenv()

setup_logging()

logger = logging.getLogger(__name__)

settings.json_response = True
mcp = FastMCP(
    "Booking.com",
    on_duplicate_tools="error",
    instructions="This server provides booking.com tools.",
    auth=None
)
mcp.add_middleware(AuthMiddleware())

logger.info(f"MCP server started!")


@mcp.tool(
    annotations={
        "title": "Search Destinations",
        "readOnlyHint": True,
        "openWorldHint": False,
        "openWorldHint": False
    }
)
async def search_destinations(query: str, ctx: Context) -> Union[List[LocationItem], Dict[str, Any]]:
    """Search for hotel destinations by valid city, country, area, or region name."""
    logger.info(f"func:search_destinations - Request ID: {ctx.request_context.request_id}\n")
    logger.info(f"func:search_destinations - Request's client host and port: {ctx.request_context.request.client.host}:{ctx.request_context.request.client.port}")
    logger.info(f"func:search_destinations - Request headers: {ctx.request_context.request.headers}")
    configg = Config(app)
    logger.info(f"MCP server started!: {configg.timeout_graceful_shutdown} - {configg.limit_concurrency}")  
    async with RapidAPIClient() as api_client:
        result = await api_client.get_destination_by_name(query)
    
    if "error" in result:
        logger.error(f"Error in search_destinations: {result.get("error_message", "Error fetching destinations.")}")
        return result
    
    formatted_results = []
    if isinstance(result, list):
        destinations_count = len(result)
        logger.info(f"Found {destinations_count} destinations for query: {query}")
        for destination in result:
            data = {
                "name": destination.get('name'),
                "type": destination.get('dest_type'),
                "destination_id": destination.get('dest_id'),
                "country": destination.get('country'),
                "coordinates": {"lat": destination.get('latitude'), "lon": destination.get('longitude')}
            }
            location_item = LocationItem(**data)
            formatted_results.append(location_item)
        
        return formatted_results if formatted_results else {"error": True, "status_code":404, "message": "No destinations found matching your query."}
    else:
        logger.warning(f"Unexpected response format from API for query: {query}")
        return {"error": True, "status_code":500, "message": "Unexpected response format from the API."}


@mcp.tool(
    annotations={
        "title": "Fetch Hotels",
        "readOnlyHint": True,
        "openWorldHint": False,
        "openWorldHint": False
    }
)
async def get_hotels(destination_id: str, checkin_date: str, checkout_date: str, ctx: Context, adults: int = 2) -> Union[List[HotelItem], Dict[str, Any]]:
    """Get hotels for a specific destination. checkin_date and checkout_date are required fields and should be future dates. 
    If required arguments are not provided, respond back to provide them. 
    If no hotels appear in search results, try searching for future dates.
    """
    logger.info(f"func:get_hotels - Request ID: {ctx.request_context.request_id}")
    logger.info(f"func:get_hotels - Request's client host and port: {ctx.request_context.request.client.host}:{ctx.request_context.request.client.port}")
    
    async with RapidAPIClient() as api_client:
        result = await api_client.get_hotels_by_destination_id(destination_id, checkin_date, checkout_date, adults)
    
    if "error" in result:
        logger.error(f"Error in get_hotels: {result.get("error_message", "Error fetching hotels.")}")
        return result
    
    formatted_results = []
    # Booking.com response is an object with "result" list
    hotels = result.get("result", [])

    if isinstance(hotels, list):
        hotels_count = len(hotels)
        logger.info(f"Found {hotels_count} hotels for destination: {destination_id}")

        for hotel in hotels[:10]:
            # use min_total_price since gross_price is always null
            price_value = hotel.get("min_total_price")
            currency = hotel.get("currency_code") or hotel.get("currencycode") or ""
            if price_value is None:
                price_display = None
            else:
                price_display = f"{price_value} {currency}".strip()

            # URL with filters applied
            base_url = hotel.get("url", "")
            if base_url:
                final_url = (
                    f"{base_url}"
                    f"?checkin={checkin_date}"
                    f"&checkout={checkout_date}"
                    f"&group_adults={adults}"
                    f"&no_rooms=1"
                    f"&group_children=0"
                )
            else:
                final_url = None

            # pick best available
            main_image = (
                hotel.get("max_1440_photo_url")
                or hotel.get("max_photo_url")
                or hotel.get("main_photo_url")
                or None
            )

            data = {
                "hotel_name": hotel.get("hotel_name"),
                "review_score": hotel.get("review_score"),
                "rating": hotel.get("class"),
                "address": hotel.get("address"),
                "price": price_display,
                "maps_url": f"https://www.google.com/maps?q={hotel.get('latitude','')},{hotel.get('longitude','')}",
                "main_image_url": main_image,
                "booking_url": final_url,
            }

            hotel_item = HotelItem(**data)
            formatted_results.append(hotel_item)
        return formatted_results if formatted_results else {"error": True, "status_code": 404, "message": "No hotels found for these dates."}
    else:
        logger.warning(f"Unexpected response format from API for destination: {destination_id}")
        return {"error": True, "status_code": 500, "message": "Unexpected response format from the API."}


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """
    Check the health of the server.
    """
    return JSONResponse(status_code=200, content={"status": "healthy", "service": "Booking.com-mcp-server"})


def run_server():
    logger.info("Starting MCP development server.")
    mcp.run(transport="http", port=9000)


# Create ASGI application
app = mcp.http_app(transport="http")
