const weatherDescriptions = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",

    45: "Fog",
    48: "Depositing rime fog",

    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",

    56: "Freezing drizzle",
    57: "Freezing drizzle (dense)",

    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",

    66: "Freezing rain",
    67: "Freezing rain (heavy)",

    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",

    77: "Snow grains",

    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",

    85: "Snow showers",
    86: "Heavy snow showers",

    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Severe thunderstorm with hail"
};

let currentScale = "F"; // Default

// These now start at 0 and get filled in after the first successful search —
// there's no server-rendered data to read on page load anymore.
let rawTemp = 0;
let rawHigh = 0;
let rawLow = 0;
let rawFeels = 0;
let conditionCode = 0;

function toF(c) { return c * (9/5) +32; }
function toC(c) { return c }

function convert(c) {
    if (currentScale === "F") return toF(c);
    return toC(c);
}

function updateDisplay() {
    document.getElementById("high").textContent =
        `H: ${Math.round(convert(rawHigh))}°`;

    document.getElementById("low").textContent =
        `L: ${Math.round(convert(rawLow))}°`;

    document.getElementById("feels-like").textContent =
        `Feels like: ${Math.round(convert(rawFeels))}°`;

    document.getElementById("condition").textContent =
    weatherDescriptions[conditionCode] || "Unknown";

    document.getElementById("temp-number").textContent =
    Math.round(convert(rawTemp));

document.querySelector(".temp-scale").textContent =
    `°${currentScale}`;

}

function setScale(scale) {
    currentScale = scale;
    updateDisplay();
}

function showError(msg) {
    document.getElementById("weather-error").textContent = msg;
    document.getElementById("weather-card").style.display = "none";
}

// Mirrors the validation that used to run server-side in error_check()
function validateCity(city) {
    if (!city) return "Please enter a city.";
    if (/\d/.test(city)) return "City cannot contain numbers.";
    if (city.length > 100) return "City name too long.";
    return null;
}

// ---------- Fetch weather for a typed city name ----------
async function fetchWeatherByCity(city) {
    document.getElementById("weather-error").textContent = "";
    try {
        const geoRes = await fetch(
            `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}`
        );
        const geoData = await geoRes.json();

        if (!geoData.results || geoData.results.length === 0) {
            showError(`Couldn't find "${city}".`);
            return;
        }

        const { latitude, longitude, name, country } = geoData.results[0];
        await fetchWeatherByCoords(latitude, longitude, name, country);
    } catch (err) {
        showError("Something went wrong. Please try again.");
        console.error(err);
    }
}

// ---------- Fetch weather for known coordinates ----------
async function fetchWeatherByCoords(lat, lon, displayName, displayCountry) {
    try {
        const weatherRes = await fetch(
            `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}` +
            `&current=temperature,apparent_temperature,weather_code` +
            `&daily=temperature_2m_max,temperature_2m_min`
        );
        const weatherData = await weatherRes.json();

        if (weatherData.error) {
            showError(weatherData.reason);
            return;
        }

        const { current, daily } = weatherData;
        rawTemp = current.temperature;
        rawHigh = daily.temperature_2m_max[0];
        rawLow = daily.temperature_2m_min[0];
        rawFeels = current.apparent_temperature;
        conditionCode = current.weather_code;

        document.getElementById("city-name").textContent =
            displayCountry ? `${displayName}, ${displayCountry}` : (displayName || "");

        document.getElementById("weather-card").style.display = "";
        updateDisplay();
    } catch (err) {
        showError("Something went wrong. Please try again.");
        console.error(err);
    }
}

// ---------- Typed-city form ----------
document.getElementById("weather-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const city = document.getElementById("city-input").value.trim();
    const validationError = validateCity(city);
    if (validationError) {
        showError(validationError);
        return;
    }
    fetchWeatherByCity(city);
});

// ---------- "Use Current Location" ----------
document.getElementById("useLocation").addEventListener("click", function (event) {
    event.preventDefault();

    if (!navigator.geolocation) {
        showError("Geolocation is not supported by your browser.");
        return;
    }

    navigator.geolocation.getCurrentPosition(geoSuccess, geoError);
});

async function geoSuccess(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    try {
        // The only step that still touches Flask: reverse-geocoding via Nominatim
        // (cached + throttled server-side, as built earlier).
        const res = await fetch(`/reverse-geocode?lat=${lat}&lon=${lon}`);
        const data = await res.json();

        if (data.error || !data.city) {
            showError("Couldn't determine your city.");
            return;
        }

        // We already have exact coordinates — no need to re-geocode the city
        // name back into coordinates, just fetch weather directly.
        await fetchWeatherByCoords(lat, lon, data.city, "");
    } catch (err) {
        showError("Something went wrong. Please try again.");
        console.error(err);
    }
}

function geoError() {
    showError("Unable to retrieve your location.");
}