"""
geolocation_service.py
─────────────────────
Converts city + country → latitude, longitude, timezone.
Uses the free Nominatim (OpenStreetMap) geocoding API.
No API key required!
"""

import math
import re
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


# Offline fallback for reverse geocoding: (city, state, country, lat, lon)
OFFLINE_CITIES = [
    ("Hyderabad", "Telangana", "India", 17.385, 78.487),
    ("Secunderabad", "Telangana", "India", 17.440, 78.498),
    ("Warangal", "Telangana", "India", 17.968, 79.594),
    ("Karimnagar", "Telangana", "India", 18.439, 79.129),
    ("Khammam", "Telangana", "India", 17.247, 80.151),
    ("Nizamabad", "Telangana", "India", 18.672, 78.094),
    ("Vijayawada", "Andhra Pradesh", "India", 16.506, 80.648),
    ("Visakhapatnam", "Andhra Pradesh", "India", 17.686, 83.218),
    ("Guntur", "Andhra Pradesh", "India", 16.307, 80.436),
    ("Tirupati", "Andhra Pradesh", "India", 13.629, 79.419),
    ("Nellore", "Andhra Pradesh", "India", 14.443, 79.987),
    ("Kurnool", "Andhra Pradesh", "India", 15.828, 78.037),
    ("Rajahmundry", "Andhra Pradesh", "India", 17.000, 81.804),
    ("Kakinada", "Andhra Pradesh", "India", 16.989, 82.247),
    ("Anantapur", "Andhra Pradesh", "India", 14.681, 77.600),
    ("Bengaluru", "Karnataka", "India", 12.972, 77.595),
    ("Mysuru", "Karnataka", "India", 12.296, 76.639),
    ("Chennai", "Tamil Nadu", "India", 13.083, 80.271),
    ("Coimbatore", "Tamil Nadu", "India", 11.017, 76.956),
    ("Madurai", "Tamil Nadu", "India", 9.925, 78.120),
    ("Mumbai", "Maharashtra", "India", 19.076, 72.878),
    ("Pune", "Maharashtra", "India", 18.520, 73.857),
    ("Nagpur", "Maharashtra", "India", 21.146, 79.088),
    ("New Delhi", "Delhi", "India", 28.614, 77.209),
    ("Kolkata", "West Bengal", "India", 22.573, 88.364),
    ("Ahmedabad", "Gujarat", "India", 23.023, 72.571),
    ("Bhubaneswar", "Odisha", "India", 20.296, 85.825),
    ("Kochi", "Kerala", "India", 9.931, 76.267),
    ("Thiruvananthapuram", "Kerala", "India", 8.524, 76.937),
    ("Varanasi", "Uttar Pradesh", "India", 25.318, 82.974),
    ("Vancouver", "British Columbia", "Canada", 49.283, -123.121),
    ("Surrey", "British Columbia", "Canada", 49.191, -122.849),
    ("White Rock", "British Columbia", "Canada", 49.025, -122.803),
    ("Calgary", "Alberta", "Canada", 51.045, -114.072),
    ("Edmonton", "Alberta", "Canada", 53.546, -113.494),
    ("Toronto", "Ontario", "Canada", 43.653, -79.383),
    ("Brampton", "Ontario", "Canada", 43.731, -79.762),
    ("Ottawa", "Ontario", "Canada", 45.421, -75.697),
    ("Montreal", "Quebec", "Canada", 45.502, -73.567),
    ("Seattle", "Washington", "United States", 47.606, -122.332),
    ("San Jose", "California", "United States", 37.338, -121.886),
    ("Los Angeles", "California", "United States", 34.052, -118.244),
    ("Dallas", "Texas", "United States", 32.777, -96.797),
    ("Houston", "Texas", "United States", 29.760, -95.370),
    ("Chicago", "Illinois", "United States", 41.878, -87.630),
    ("New York", "New York", "United States", 40.713, -74.006),
    ("Edison", "New Jersey", "United States", 40.519, -74.412),
    ("Atlanta", "Georgia", "United States", 33.749, -84.388),
    ("London", "England", "United Kingdom", 51.507, -0.128),
    ("Singapore", "", "Singapore", 1.352, 103.820),
    ("Dubai", "Dubai", "United Arab Emirates", 25.205, 55.271),
    ("Sydney", "New South Wales", "Australia", -33.869, 151.209),
    ("Melbourne", "Victoria", "Australia", -37.814, 144.963),
]

METROS = {"Hyderabad", "Bengaluru", "Chennai", "Mumbai", "New Delhi", "Kolkata",
          "Pune", "Ahmedabad", "Toronto", "New York", "Los Angeles", "Chicago",
          "Dallas", "Houston", "London", "Singapore", "Dubai", "Sydney", "Melbourne"}

# "Gandipet mandal" -> "Gandipet", "Tenali Mandal" -> "Tenali"
_ADMIN_SUFFIX = re.compile(r"\s+(mandal|tehsil|taluka?|district|division|block)\b.*$", re.I)

# Country guess from timezone when no known city is nearby
TZ_COUNTRY = {
    "Asia/Kolkata": "India", "Asia/Calcutta": "India",
    "America/Vancouver": "Canada", "America/Toronto": "Canada",
    "America/Edmonton": "Canada", "America/Winnipeg": "Canada",
    "America/Halifax": "Canada", "America/Montreal": "Canada",
    "America/New_York": "United States", "America/Chicago": "United States",
    "America/Denver": "United States", "America/Los_Angeles": "United States",
    "America/Phoenix": "United States", "Europe/London": "United Kingdom",
    "Asia/Singapore": "Singapore", "Asia/Dubai": "United Arab Emirates",
    "Australia/Sydney": "Australia", "Australia/Melbourne": "Australia",
    "Asia/Colombo": "Sri Lanka", "Asia/Kathmandu": "Nepal",
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

    def from_coordinates(self, lat: float, lon: float, city: str = "",
                         state: str = "", country: str = "") -> dict:
        """
        Build a location from GPS coordinates. Needs no network: timezone
        comes from the offline timezonefinder database.
        """
        return {
            "latitude": lat,
            "longitude": lon,
            "timezone": self._get_timezone(lat, lon, country or ""),
            "display_name": ", ".join(x for x in (city, state, country) if x) or f"{lat:.4f}, {lon:.4f}",
            "city": city,
            "country": country,
        }

    def reverse_geocode(self, lat: float, lon: float) -> dict:
        """
        Coordinates -> city / state / country.
        Online: OpenStreetMap Nominatim. Offline: nearest known city.
        """
        tz = self._get_timezone(lat, lon, "")
        try:
            r = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={"lat": lat, "lon": lon, "format": "json",
                        "zoom": 10, "addressdetails": 1, "accept-language": "en"},
                headers=self.headers, timeout=6,
            )
            r.raise_for_status()
            a = r.json().get("address", {})
            city = a.get("city") or a.get("town") or ""
            state = a.get("state", "")
            if not city:
                # Outskirts often have no city, only a mandal/taluk (e.g. "Gandipet
                # mandal" in Hyderabad). Prefer the metro it belongs to.
                metro = self._nearby_city(lat, lon)
                if metro:
                    city, state = metro[0], metro[1] or state
                else:
                    raw = (a.get("village") or a.get("municipality")
                           or a.get("county") or a.get("state_district") or "")
                    city = _ADMIN_SUFFIX.sub("", raw).strip()
            return {"city": city, "state": state,
                    "country": a.get("country", ""), "timezone": tz,
                    "latitude": lat, "longitude": lon, "source": "online"}
        except Exception as e:
            logger.info(f"Reverse geocode offline fallback: {e}")
            best = min(OFFLINE_CITIES, key=lambda c: (c[3] - lat) ** 2 + (c[4] - lon) ** 2)
            near = ((best[3] - lat) ** 2 + (best[4] - lon) ** 2) ** 0.5 < 1.0  # ~100 km
            return {"city": best[0] if near else "", "state": best[1] if near else "",
                    "country": best[2] if near else TZ_COUNTRY.get(tz, ""),
                    "timezone": tz, "latitude": lat, "longitude": lon, "source": "offline"}

    @staticmethod
    def _nearby_city(lat: float, lon: float):
        """Known city whose urban area contains the point (metros ~35 km, others ~12 km)."""
        best, best_d = None, 1e9
        for c in OFFLINE_CITIES:
            dlat = math.radians(c[3] - lat)
            dlon = math.radians(c[4] - lon)
            h = (math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat))
                 * math.cos(math.radians(c[3])) * math.sin(dlon / 2) ** 2)
            d = 12742 * math.asin(math.sqrt(h))
            if d <= (35 if c[0] in METROS else 12) and d < best_d:
                best, best_d = c, d
        return best

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
