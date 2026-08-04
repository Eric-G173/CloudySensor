import requests
import time
import threading
import os
from dotenv import load_dotenv

load_dotenv()
# ---------- Geocode cache ----------
GEOCODE_CACHE = {}
GEOCODE_CACHE_TTL = 60 * 60 * 24 * 7  # 1 week — a location's city name doesn't change

# ---------- Nominatim throttle ----------
_nominatim_lock = threading.Lock()
_last_nominatim_call = 0
MIN_INTERVAL = 1.1  # a bit over Nominatim's 1 req/sec cap, for safety margin

NOMINATIM_CONTACT = os.getenv("NOMINATIM_CONTACT", "no-contact-set")
NOMINATIM_HEADERS = {
    "User-Agent": f"CloudySensor/1.0 (contact: {NOMINATIM_CONTACT})"
}


def _call_nominatim(url, params):
    """Serializes every Nominatim call through a shared clock, so no matter how
    many requests arrive at once, they go out no faster than 1 per second."""
    global _last_nominatim_call
    with _nominatim_lock:
        wait = MIN_INTERVAL - (time.time() - _last_nominatim_call)
        if wait > 0:
            time.sleep(wait)
        response = requests.get(url, params=params, headers=NOMINATIM_HEADERS, timeout=5)
        _last_nominatim_call = time.time()
    return response


def reverse_geocode(lat, lon):
    # Defensive cast — Flask's request.values.get() returns strings, and round()
    # requires a number. This makes the function safe regardless of caller.
    lat = float(lat)
    lon = float(lon)

    key = (round(lat, 2), round(lon, 2))  # buckets nearby coords into one cache entry
    now = time.time()

    if key in GEOCODE_CACHE:
        city, timestamp = GEOCODE_CACHE[key]
        if now - timestamp < GEOCODE_CACHE_TTL:
            return city

    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "zoom": 10,
        "format": "json",
        "addressdetails": 1,
    }

    try:
        response = _call_nominatim(url, params)
        response.raise_for_status()
        data = response.json()
        address = data.get("address", {})
        city = (
            address.get("city") or
            address.get("town") or
            address.get("village") or
            address.get("municipality")
        )
        GEOCODE_CACHE[key] = (city, now)
        return city
    except Exception as e:
        print("DEBUG: reverse_geocode failed, continuing without city name:", e)
        return None


# get_weather() has been removed from this file. Weather lookups now
# happen client-side in weather.js, straight from the browser to Open-Meteo,
# so they're no longer exposed to Render's shared outbound IP.