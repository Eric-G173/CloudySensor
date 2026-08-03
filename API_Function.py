import requests
import time
import threading

# ---------- Weather cache ----------
CACHE = {}
CACHE_TTL = 60 * 20  # 20 minutes — weather changes slowly enough for this

# ---------- Geocode cache ----------
GEOCODE_CACHE = {}
GEOCODE_CACHE_TTL = 60 * 60 * 24 * 7  # 1 week — a location's city name doesn't change

# ---------- Nominatim throttle ----------
_nominatim_lock = threading.Lock()
_last_nominatim_call = 0
MIN_INTERVAL = 1.1  # a bit over Nominatim's 1 req/sec cap, for safety margin

NOMINATIM_HEADERS = {
    "User-Agent": "CloudySensor/1.0 (contact: your-email@example.com)"  # put a real contact here
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


def get_weather(city_name):
    city = city_name
    now = time.time()

    if city in CACHE:
        cached_data, timestamp = CACHE[city]
        if now - timestamp < CACHE_TTL:
            print("DEBUG: Returning cached weather for", city)
            return cached_data

    geo_location = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"

    try:
        response = requests.get(geo_location, timeout=5).json()
    except Exception as e:
        print("DEBUG: geocoding request failed:", e)
        return None

    # Check for empty results BEFORE indexing into them.
    # (Previously this indexed results[0] first and checked emptiness after,
    # which would raise on any city with no matches.)
    if not response.get("results"):
        return {"matched_city": None}

    matched_city = response["results"][0]["name"]
    matched_country = response["results"][0]["country"]
    lat = response["results"][0]["latitude"]
    lon = response["results"][0]["longitude"]

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature,apparent_temperature,weather_code"
        f"&daily=temperature_2m_max,temperature_2m_min"
    )

    try:
        weather_response = requests.get(weather_url, timeout=5).json()
    except Exception as e:
        print("DEBUG: weather request failed:", e)
        return None

    if weather_response.get("error"):
        print("DEBUG: API returned error:", weather_response.get("reason"))
        return None

    current = weather_response.get("current")
    daily = weather_response.get("daily")
    if not current or not daily:
        print("DEBUG: Missing current or daily weather data")
        return None

    data = {  # All in Celsius (minus condition)
        "city": matched_city,
        "country": matched_country,
        "tempNow": current["temperature"],
        "temp_max": daily["temperature_2m_max"][0],
        "temp_min": daily["temperature_2m_min"][0],
        "feels_like": current["apparent_temperature"],
        "condition": current["weather_code"],
    }
    CACHE[city] = (data, now)
    print("DEBUG: Cached new weather for", city)

    return data