"""
geolocation_service.py
─────────────────────
Converts city + country → latitude, longitude, timezone.
Uses the free Nominatim (OpenStreetMap) geocoding API.
No API key required!
"""

import requests
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Timezone fallback table for major Indian cities
INDIA_TIMEZONE_MAP = {
    "india": "Asia/Kolkata",
    "sri lanka": "Asia/Colombo",
    "nepal": "Asia/Kathmandu",
    "bangladesh": "Asia/Dhaka",
    "pakistan": "Asia/Karachi",
    "usa": "America/New_York",
    "united states": "America/New_York",
    "uk": "Europe/London",
    "united kingdom": "Europe/London",
    "australia": "Australia/Sydney",
    "canada": "America/Toronto",
    "germany": "Europe/Berlin",
    "singapore": "Asia/Singapore",
    "malaysia": "Asia/Kuala_Lumpur",
    "uae": "Asia/Dubai",
    "united arab emirates": "Asia/Dubai",
}


class GeolocationService:
    """
    Converts a city + country name into coordinates and timezone.
    Uses OpenStreetMap Nominatim (free, no key needed).
    """

    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.timezone_url = "https://timezonefinder.micg.net/api/v1"  # fallback
        self.headers = {
            "User-Agent": "SankalpamGenerator/1.0 (hindu-sankalpam-app)"
        }

    @lru_cache(maxsize=256)
    def get_location(self, city: str, country: str) -> dict | None:
        """
        Returns dict with: latitude, longitude, timezone, display_name
        Returns None if location not found.
        """
        try:
            # Query Nominatim
            params = {
                "q": f"{city}, {country}",
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            response = requests.get(
                self.nominatim_url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            results = response.json()

            if not results:
                logger.warning(f"No location found for: {city}, {country}")
                return None

            result = results[0]
            lat = float(result["lat"])
            lon = float(result["lon"])

            # Get timezone for these coordinates
            timezone = self._get_timezone(lat, lon, country)

            return {
                "latitude": lat,
                "longitude": lon,
                "timezone": timezone,
                "display_name": result.get("display_name", f"{city}, {country}"),
                "city": city,
                "country": country
            }

        except requests.RequestException as e:
            logger.error(f"Geocoding request failed: {e}")
            # Return a fallback for India if network fails
            return self._get_fallback(city, country)

    def _get_timezone(self, lat: float, lon: float, country: str) -> str:
        """
        Get timezone from coordinates using timezonefinder library.
        Falls back to country-based mapping if library unavailable.
        """
        try:
            from timezonefinder import TimezoneFinder
            tf = TimezoneFinder()
            tz = tf.timezone_at(lat=lat, lng=lon)
            if tz:
                return tz
        except ImportError:
            logger.info("timezonefinder not installed, using country fallback")
        except Exception as e:
            logger.warning(f"Timezone lookup failed: {e}")

        # Fallback: use country name
        country_lower = country.lower().strip()
        return INDIA_TIMEZONE_MAP.get(country_lower, "Asia/Kolkata")

    def _get_fallback(self, city: str, country: str) -> dict:
        """
        Fallback location data when geocoding API is unavailable.
        Defaults to major Indian cities.
        """
        # Common Indian city coordinates
        city_coords = {
            "hyderabad": (17.3850, 78.4867),
            "chennai": (13.0827, 80.2707),
            "bangalore": (12.9716, 77.5946),
            "bengaluru": (12.9716, 77.5946),
            "mumbai": (19.0760, 72.8777),
            "delhi": (28.6139, 77.2090),
            "kolkata": (22.5726, 88.3639),
            "pune": (18.5204, 73.8567),
            "ahmedabad": (23.0225, 72.5714),
            "tirupati": (13.6288, 79.4192),
        }

        city_lower = city.lower().strip()
        coords = city_coords.get(city_lower, (17.3850, 78.4867))  # Default: Hyderabad

        country_lower = country.lower().strip()
        timezone = INDIA_TIMEZONE_MAP.get(country_lower, "Asia/Kolkata")

        return {
            "latitude": coords[0],
            "longitude": coords[1],
            "timezone": timezone,
            "display_name": f"{city}, {country}",
            "city": city,
            "country": country
        }
