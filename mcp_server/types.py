from typing import Optional
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lat: Optional[float] = None
    lon: Optional[float] = None


class LocationItem(BaseModel):
    name: str
    type: str
    destination_id: int
    country: str
    coordinates: Optional[Coordinates] = None


class HotelItem(BaseModel):
    hotel_name: str
    review_score: Optional[float] = None
    rating: Optional[float] = None
    address: Optional[str] = None
    price: Optional[str] = None
    maps_url: str
    main_image_url: Optional[str] = None
    booking_url: Optional[str] = None
