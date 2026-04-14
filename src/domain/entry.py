"""
Entry domain models for travel records and location aggregation.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class EntryBase(BaseModel):
    """Shared entry fields."""

    destination: str
    entry_date: date
    entry_type: str
    category: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    title: Optional[str] = None
    content: str


class EntryCreate(EntryBase):
    """Payload for creating an entry."""


class EntryUpdate(BaseModel):
    """Payload for updating an entry."""

    destination: Optional[str] = None
    entry_date: Optional[date] = None
    entry_type: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    title: Optional[str] = None
    content: Optional[str] = None


class EntryResponse(EntryBase):
    """Entry returned by API."""

    id: int
    created_at: datetime
    updated_at: datetime


class LocationResponse(BaseModel):
    """Aggregated location data for the globe UI."""

    destination: str
    country: Optional[str] = None
    city: str
    lat: float
    lng: float
    count: int
    latest_entry_date: date
