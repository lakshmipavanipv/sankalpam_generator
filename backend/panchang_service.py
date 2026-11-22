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
import swisseph as swe

# Sidereal (Nirayana) positions with Lahiri ayanamsa, as used by Telugu panchangam.
# FLG_MOSEPH = built-in Moshier ephemeris -> works fully offline, no data files needed.
swe.set_sid_mode(swe.SIDM_LAHIRI)
_SID_FLAGS = swe.FLG_MOSEPH | swe.FLG_SIDEREAL

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
            # Swiss Ephemeris keeps settings per thread; FastAPI runs requests
            # on worker threads, so set Lahiri on every call.
            swe.set_sid_mode(swe.SIDM_LAHIRI)

            # Parse date/time in local timezone
            tz = pytz.timezone(timezone)
            dt_local = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            dt_local = tz.localize(dt_local)

            # Convert to UTC for calculations
            dt_utc = dt_local.astimezone(pytz.utc)

            # Julian Day (UT)
            jd = self._julian_day(dt_utc)

            # Sidereal (Nirayana) Sun and Moon longitudes, Lahiri ayanamsa
            sun_lon = self._sid_lon(jd, swe.SUN)
            moon_lon = self._sid_lon(jd, swe.MOON)

            # ── 5 Panchang Elements ──────────────────────────────────────────

            # 1. Tithi (lunar day)
            tithi_num, tithi_name, paksha = self._calc_tithi(sun_lon, moon_lon)

            # 2. Vara (weekday)
            vara_num = dt_local.weekday()  # 0=Monday in Python
            hindu_vara = (vara_num + 1) % 7  # 0=Sunday
            vara_name = VARAS[hindu_vara]

            # 3. Nakshatra (sidereal Moon / 13°20')
            nak_span = 360 / 27
            nakshatra_num = int(moon_lon / nak_span) % 27
            nakshatra_name = NAKSHATRAS[nakshatra_num]
            nakshatra_pada = int((moon_lon % nak_span) / (nak_span / 4)) + 1

            # 4. Yoga (sidereal Sun + Moon)
            yoga_num = int(((sun_lon + moon_lon) % 360) / nak_span) % 27
            yoga_name = YOGAS[yoga_num]

            # 5. Karana (half-tithi, 60 per lunar month)
            karana_name = self._calc_karana((moon_lon - sun_lon) % 360)

            # ── Additional Elements ──────────────────────────────────────────

            # Masa: amanta lunar month (Telugu/Kannada/Marathi) named from the
            # Sun's rashi at the preceding new moon; Tamil uses the solar month.
            masa_num, is_adhika = self._calc_lunar_masa(jd)
            if calendar_type == "Tamil":
                masa_name = TAMIL_MASAS[int(sun_lon / 30) % 12]
            else:
                masa_name = self._get_masa(masa_num, calendar_type)
                if is_adhika:
                    masa_name = "Adhika " + masa_name

            # Ritu (season) - 2 lunar masas per season, Chaitra = Vasanta
            ritu_name, ritu_english = RITUS[(masa_num // 2) % 6]

            # Ayana (sidereal Sun: Makara -> Mithuna is Uttarayana)
            ayana = self._calc_ayana(sun_lon)

            # Samvatsara changes at Ugadi (Chaitra), not on 1 January
            lunar_year = dt_local.year - 1 if (dt_local.month <= 4 and masa_num >= 8) else dt_local.year
            samvatsara = self._calc_samvatsara(lunar_year)

            # Year in Kali Yuga
            kali_yuga_year = dt_local.year + 3101

            return {
                "tithi": tithi_name,
                "tithi_number": tithi_num,
                "paksha": paksha,
                "vara": vara_name,
                "vara_english": VARA_ENGLISH[hindu_vara],
                "nakshatra": nakshatra_name,
                "nakshatra_pada": nakshatra_pada,
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
                "ayanamsa": round(swe.get_ayanamsa_ut(jd), 4),
                "is_adhika_masa": is_adhika,
                "engine": "Swiss Ephemeris (Moshier, offline) - Lahiri sidereal",
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

    def _sid_lon(self, jd: float, body: int) -> float:
        """Sidereal ecliptic longitude (degrees) of a body, Lahiri ayanamsa."""
        return swe.calc_ut(jd, body, _SID_FLAGS)[0][0] % 360

    def _elongation(self, jd: float) -> float:
        """Moon minus Sun longitude, 0..360."""
        return (self._sid_lon(jd, swe.MOON) - self._sid_lon(jd, swe.SUN)) % 360

    def _new_moon_near(self, jd_guess: float) -> float:
        """Refine to the exact new moon (elongation = 0) near jd_guess."""
        jd = jd_guess
        for _ in range(8):
            e = self._elongation(jd)
            if e > 180:
                e -= 360
            jd -= e / 12.190749  # mean daily elongation
            if abs(e) < 1e-6:
                break
        return jd

    def _calc_lunar_masa(self, jd: float):
        """
        Amanta masa: month is named by the Sun's rashi at the new moon that
        starts it (Sun in Meena -> Chaitra). If no sankranti falls inside the
        month (Sun in same rashi at both new moons) it is Adhika.
        Returns (masa_index with Chaitra=0, is_adhika).
        """
        prev_nm = self._new_moon_near(jd - self._elongation(jd) / 12.190749)
        if prev_nm > jd:  # refinement landed on the next new moon
            prev_nm = self._new_moon_near(prev_nm - 29.53)
        next_nm = self._new_moon_near(prev_nm + 29.53)
        r1 = int(self._sid_lon(prev_nm, swe.SUN) / 30) % 12
        r2 = int(self._sid_lon(next_nm, swe.SUN) / 30) % 12
        return (r1 + 1) % 12, r1 == r2

    def _calc_karana(self, elongation: float) -> str:
        """60 half-tithis: Kimstughna, 8 x 7 movable karanas, Shakuni, Chatushpada, Naga."""
        k = int(elongation / 6) % 60
        if k == 0:
            return "Kimstughna"
        if k >= 57:
            return ["Shakuni", "Chatushpada", "Nagava"][k - 57]
        return KARANAS[(k - 1) % 7]

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
