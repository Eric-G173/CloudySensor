# CloudySensor

A full-stack weather app: search any city, or use your current location, and get live conditions and forecasts.

Live demo: https://weather-website-fjzu.onrender.com/

<img width="679" height="862" alt="image" src="https://github.com/user-attachments/assets/105851f1-228f-4f65-bb72-1ea22c35403b" />


# Features
- Search weather by city name, or auto-detect location via the browser's Geolocation API
- Current temperature, "feels like," daily high/low, and condition
- Fahrenheit / Celsius toggle
- Weather updates in place. no page reloads

# Tech stack
- **Backend:** Python, Flask
 - **Frontend:** JavaScript, HTML, CSS
 - **APIs:** Open-Meteo (geocoding + forecast), Nominatim / OpenStreetMap (reverse geocoding)
 - **Testing:** pytest
- **CI/CD:** GitHub Actions → Render (push-to-deploy)

# Architecture: why API calls are split between frontend and backend

Earlier versions of this app made every API call from the Flask backend. In production on Render's free tier, that broke because Render shares outbound IP addresses across many unrelated customers in the same region, and Open-Meteo rate-limits by IP. The app got rate-limited by traffic that had nothing to do with it, before a single real visitor had loaded the page.

The fix:

- Weather lookups (Open-Meteo) now happen entirely client-side, in weather.js. Each visitor's browser calls the API directly, using their own IP instead of Render's shared one, so the app is no longer exposed to other tenants' traffic on the same host.
- Reverse geocoding (Nominatim) stays server-side, in geoConversion.py, since Nominatim's usage policy asks for server-side caching and doesn't reliably support direct browser calls. It's hardened instead: results are cached by rounded coordinates (1-week TTL), throttled to stay under Nominatim's 1-request/second limit, and sent with a real identifying User-Agent per their policy.

# Running locally
```
bash
git clone https://github.com/Eric-G173/Weather-Website.git
cd Weather-Website
python -m venv env
source env/bin/activate      # Windows: env\Scripts\Activate.ps1
pip install -r requirements.txt
```
Create a .env file in the project root:
```
SECRET_KEY=your-secret-key
NOMINATIM_CONTACT=your-email@example.com
```
Then run:
```
bash
python app.py
```
The app will be available at http://127.0.0.1:5000

# Running tests
```
bash
pytest
```
