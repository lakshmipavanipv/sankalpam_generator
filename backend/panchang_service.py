"""
panchang_service.py
───────────────────
Calculates Hindu Panchang (almanac) values for a given date/time/location.

Panchang consists of 5 limbs (Pancha = 5, Anga = limb):
  1. Tithi   – Lunar day (1-30)
  2. Vara    – Day of week
  3. Nakshatra – Lunar mansion (1-27)
  4. Yoga    – Luni-solar yoga (1-27)
  5. Karana  – Half of a Tithi (1-11)

Plus additional elements: Masa, Paksha, Ritu, Ayana, Samvatsara
"""

import math
import logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)


# ─── Lookup Tables ─────────────────────────────────────────────────────────────

TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashti", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"
]

VARAS = ["Ravivara", "Somavara", "Mangalavara", "Budhavara", "Guruvara", "Shukravara", "Shanivara"]
VARA_ENGLISH = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti"
]

KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garaja",
    "Vanija", "Vishti", "Shakuni", "Chatushpada", "Nagava", "Kimstughna"
]

# Telugu Masas (months)
TELUGU_MASAS = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha",
    "Shravana", "Bhadrapada", "Ashwayuja", "Kartika",
    "Margashira", "Pushya", "Magha", "Phalguna"
]

# Tamil Masas
TAMIL_MASAS = [
    "Chithirai", "Vaikasi", "Aani", "Aadi",
    "Aavani", "Purattasi", "Aippasi", "Karthigai",
    "Margazhi", "Thai", "Maasi", "Panguni"
]

# Kannada/Marathi use similar Sanskrit names
KANNADA_MASAS = TELUGU_MASAS  # Very similar to Telugu

RITUS = [
    ("Vasanta", "Spring"),        # Chaitra-Vaishakha
    ("Grishma", "Summer"),        # Jyeshtha-Ashadha
    ("Varsha", "Monsoon"),        # Shravana-Bhadrapada
    ("Sharada", "Autumn"),        # Ashwayuja-Kartika
    ("Hemanta", "Pre-Winter"),    # Margashira-Pushya
    ("Shishira", "Winter"),       # Magha-Phalguna
]

# Telugu Samvatsaras (60-year cycle)
SAMVATSARAS = [
    "Prabhava", "Vibhava", "Shukla", "Pramoda", "Prajapati",
    "Angirasa", "Shrimukha", "Bhava", "Yuva", "Dhata",
    "Ishvara", "Bahudhanya", "Pramadi", "Vikrama", "Vrisha",
    "Chitrabhanu", "Svabhanu", "Tarana", "Parthiva", "Vyaya",
    "Sarvajit", "Sarvadhari", "Virodhi", "Vikruti", "Khara",
    "Nandana", "Vijaya", "Jaya", "Manmatha", "Durmukhi",
    "Hevilambi", "Vilambi", "Vikari", "Sharvari", "Plava",
    "Shubhakrut", "Shobhakrut", "Krodhi", "Vishvavasu", "Parabhava",
    "Plavanga", "Kilaka", "Saumya", "Sadharana", "Virodhikrut",
    "Paridhavi", "Pramadi", "Ananda", "Rakshasa", "Nala",
    "Pingala", "Kalayukti", "Siddharthi", "Raudra", "Durmati",
    "Dundubhi", "Rudhirodgari", "Raktakshi", "Krodhana", "Akshaya"
]


class PanchangService:
    """
    Calculates Hindu Panchang elements using astronomical algorithms.
    Based on Jean Meeus 'Astronomical Algorithms' and Vedic calendar system.
    """

    def calculate(
        self,
        date_str: str,
        time_str: str,
        latitude: float,
        longitude: float,
        timezone: str,
        calendar_type: str = "Telugu"
    ) -> dict:
        """
        Main method: returns all Panchang elements.
        """
        try:
            # Parse date/time in local timezone
            tz = pytz.timezone(timezone)
            dt_local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            dt_local = tz.localize(dt_local)

            # Convert to UTC for calculations
            dt_utc = dt_local.astimezone(pytz.utc)

            # Julian Day Number (astronomical time standard)
            jd = self._julian_day(dt_utc)

            # Calculate sun and moon positions
            sun_lon = self._sun_longitude(jd)
            moon_lon = self._moon_longitude(jd)

            # ── 5 Panchang Elements ──────────────────────────────────────────

            # 1. Tithi (lunar day)
            tithi_num, tithi_name, paksha = self._calc_tithi(sun_lon, moon_lon)

            # 2. Vara (weekday)
            vara_num = dt_local.weekday()  # 0=Monday in Python
            # Convert to Hindu weekday (0=Sunday)
            hindu_vara = (vara_num + 1) % 7
            vara_name = VARAS[hindu_vara]

            # 3. Nakshatra (lunar mansion)
            nakshatra_num = int(moon_lon / (360 / 27)) % 27
            nakshatra_name = NAKSHATRAS[nakshatra_num]

            # 4. Yoga (luni-solar)
            yoga_num = int(((sun_lon + moon_lon) % 360) / (360 / 27)) % 27
            yoga_name = YOGAS[yoga_num]

            # 5. Karana (half-tithi)
            karana_num = int(((moon_lon - sun_lon) % 360) / 6) % 11
            karana_name = KARANAS[karana_num]

            # ── Additional Elements ──────────────────────────────────────────

            # Masa (lunar month) - based on sun's position
            masa_num = int(sun_lon / 30) % 12
            masa_name = self._get_masa(masa_num, calendar_type)

            # Ritu (season) - 2 masas per season
            ritu_num = masa_num // 2
            ritu_name, ritu_english = RITUS[ritu_num % 6]

            # Ayana (solar half-year)
            ayana = self._calc_ayana(sun_lon)

            # Samvatsara (year in 60-year cycle)
            samvatsara = self._calc_samvatsara(dt_local.year)

            # Year in Kali Yuga
            kali_yuga_year = dt_local.year + 3101

            return {
                "tithi": tithi_name,
                "tithi_number": tithi_num,
                "paksha": paksha,
                "vara": vara_name,
                "vara_english": VARA_ENGLISH[hindu_vara],
                "nakshatra": nakshatra_name,
                "yoga": yoga_name,
                "karana": karana_name,
                "masa": masa_name,
                "masa_num": masa_num,
                "ritu": ritu_name,
                "ritu_english": ritu_english,
                "ayana": ayana,
                "samvatsara": samvatsara,
                "kali_yuga_year": kali_yuga_year,
                "calendar_type": calendar_type,
                "date": date_str,
                "time": time_str,
                "timezone": timezone,
                "sun_longitude": round(sun_lon, 2),
                "moon_longitude": round(moon_lon, 2),
            }

        except Exception as e:
            logger.error(f"Panchang calculation error: {e}", exc_info=True)
            raise

    # ─── Core Astronomical Calculations ────────────────────────────────────────

    def _julian_day(self, dt_utc: datetime) -> float:
        """Convert UTC datetime to Julian Day Number."""
        y = dt_utc.year
        m = dt_utc.month
        d = dt_utc.day
        h = dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0

        if m <= 2:
            y -= 1
            m += 12

        A = int(y / 100)
        B = 2 - A + int(A / 4)

        jd = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + h / 24.0 + B - 1524.5
        return jd

    def _sun_longitude(self, jd: float) -> float:
        """Calculate approximate Sun ecliptic longitude (degrees)."""
        # Days since J2000.0
        n = jd - 2451545.0

        # Mean longitude
        L = (280.460 + 0.9856474 * n) % 360

        # Mean anomaly
        g = math.radians((357.528 + 0.9856003 * n) % 360)

        # Ecliptic longitude
        lon = L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g)
        return lon % 360

    def _moon_longitude(self, jd: float) -> float:
        """Calculate approximate Moon ecliptic longitude (degrees)."""
        n = jd - 2451545.0

        # Moon's mean longitude
        L = (218.316 + 13.176396 * n) % 360

        # Moon's mean anomaly
        M = math.radians((134.963 + 13.064993 * n) % 360)

        # Moon's mean elongation
        D = math.radians((297.850 + 12.190749 * n) % 360)

        # Moon's argument of latitude
        F = math.radians((93.272 + 13.229350 * n) % 360)

        # Correction terms
        lon = (
            L
            + 6.289 * math.sin(M)
            - 1.274 * math.sin(2 * D - M)
            + 0.658 * math.sin(2 * D)
            - 0.186 * math.sin(math.radians((357.528 + 0.9856003 * n) % 360))
            - 0.114 * math.sin(2 * F)
        )
        return lon % 360

    def _calc_tithi(self, sun_lon: float, moon_lon: float):
        """
        Tithi = lunar elongation / 12 degrees.
        Returns (number, name, paksha).
        """
        elongation = (moon_lon - sun_lon) % 360
        tithi_num = int(elongation / 12) + 1  # 1-30

        if tithi_num <= 15:
            paksha = "Shukla Paksha"  # Waxing (bright fortnight)
            if tithi_num == 15:
                tithi_name = "Purnima"
            else:
                tithi_name = TITHIS[tithi_num - 1]
        else:
            paksha = "Krishna Paksha"  # Waning (dark fortnight)
            kp_num = tithi_num - 15
            if kp_num == 15:
                tithi_name = "Amavasya"
            else:
                tithi_name = TITHIS[kp_num - 1]

        return tithi_num, tithi_name, paksha

    def _get_masa(self, masa_num: int, calendar_type: str) -> str:
        """Get month name based on calendar type."""
        if calendar_type == "Tamil":
            return TAMIL_MASAS[masa_num]
        elif calendar_type in ("Kannada", "Marathi"):
            return KANNADA_MASAS[masa_num]
        else:  # Telugu (default)
            return TELUGU_MASAS[masa_num]

    def _calc_ayana(self, sun_lon: float) -> str:
        """
        Uttarayana: Sun in Capricorn-Gemini (270°-90°)
        Dakshinayana: Sun in Cancer-Sagittarius (90°-270°)
        """
        if sun_lon >= 270 or sun_lon < 90:
            return "Uttarayana"
        else:
            return "Dakshinayana"

    def _calc_samvatsara(self, year: int) -> str:
        """Get the current Samvatsara (one of 60 cyclic Hindu years)."""
        # Samvatsara cycle starts from a reference point
        # Approximate: (year - 1987) mod 60 gives index
        idx = (year - 1987) % 60
        return SAMVATSARAS[idx]
