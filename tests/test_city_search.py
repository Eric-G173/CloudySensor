from app import app
from API_Function import reverse_geocode
import API_Function


def test_home_page():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"CloudySensor" in response.data


def test_reverse_geocode_endpoint_missing_params():
    client = app.test_client()
    response = client.get("/reverse-geocode")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing lat/lon"


def test_reverse_geocode_endpoint_invalid_params():
    client = app.test_client()
    response = client.get("/reverse-geocode?lat=notanumber&lon=-112.0")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid lat/lon"


def test_reverse_geocode_endpoint_valid(monkeypatch):
    client = app.test_client()
    # Patch the name as it exists in app.py's own namespace (see explanation above) —
    # patching API_Function.reverse_geocode here would NOT affect the route.
    monkeypatch.setattr("app.reverse_geocode", lambda lat, lon: "Phoenix")

    response = client.get("/reverse-geocode?lat=33.4&lon=-112.0")

    assert response.status_code == 200
    assert response.get_json() == {"city": "Phoenix"}


def test_reverse_geocode_endpoint_city_not_found(monkeypatch):
    client = app.test_client()
    monkeypatch.setattr("app.reverse_geocode", lambda lat, lon: None)

    response = client.get("/reverse-geocode?lat=0&lon=0")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Could not determine city"


def test_reverse_geocode_function(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"address": {"city": "Phoenix"}}

    def fake_get(url, params=None, headers=None, timeout=None):
        return FakeResponse()

    monkeypatch.setattr("API_Function.requests.get", fake_get)
    API_Function.GEOCODE_CACHE.clear()  # avoid a stale hit if another test used these coords

    city = reverse_geocode(33.301, -112.002)
    assert city == "Phoenix"


# NOTE: There's no longer a Python-level test for the actual weather lookup
# (temperature, high/low, condition) — that logic now lives entirely in
# weather.js, running in the browser against Open-Meteo directly. pytest and
# Flask's test client can't exercise that; it'd need a JS-side test tool
# (e.g. Playwright or Jest) if you want automated coverage there. Not required
# for a portfolio project, just flagging the gap rather than leaving it silent.