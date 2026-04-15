"""Geocoding service for resolving city/country to coordinates."""

import json
from urllib.parse import quote_plus
from urllib.request import Request, urlopen


class GeocodeError(Exception):
    """Raised when geocoding fails."""


class GeocodeService:
    """Resolve human-readable places into latitude and longitude."""

    def __init__(self, settings, entry_repository):
        self.settings = settings
        self.entry_repository = entry_repository

    def resolve(self, city, country=None):
        """Resolve a city/country pair into coordinates."""

        if not city:
            raise GeocodeError("City is required for automatic geocoding")

        cached = self.entry_repository.find_existing_coordinates(city=city, country=country)
        if cached is not None:
            return cached

        provider = (self.settings.geocode_provider or "opencage").lower()
        if provider != "opencage":
            raise GeocodeError("Unsupported geocode provider: {0}".format(provider))

        if not self.settings.geocode_api_key:
            raise GeocodeError("GEOCODE_API_KEY is required when lat/lng are not provided")

        query_parts = [city]
        if country:
            query_parts.append(country)
        query_text = ", ".join(query_parts)
        url = (
            "https://api.opencagedata.com/geocode/v1/json?q={query}&key={key}&limit=1&no_annotations=1"
            .format(
                query=quote_plus(query_text),
                key=quote_plus(self.settings.geocode_api_key),
            )
        )

        request = Request(
            url,
            headers={
                "User-Agent": "OpenGiraffe-Travelbook/1.0"
            },
        )
        response = urlopen(request, timeout=self.settings.geocode_timeout)
        body = response.read().decode("utf-8")
        payload = json.loads(body)
        results = payload.get("results") or []
        if not results:
            raise GeocodeError("Could not resolve coordinates for {0}".format(query_text))

        geometry = results[0].get("geometry") or {}
        lat = geometry.get("lat")
        lng = geometry.get("lng")
        if lat is None or lng is None:
            raise GeocodeError("Geocoding provider returned no coordinates for {0}".format(query_text))

        return {
            "lat": float(lat),
            "lng": float(lng),
        }
