from flask import Flask, render_template, request, jsonify

from geoConversion import reverse_geocode
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "test_key")  # Test key used as fallback for CI tests


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/reverse-geocode")
def reverse_geocode_endpoint():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    if lat is None or lon is None:
        return jsonify({"error": "Missing lat/lon"}), 400

    try:
        city = reverse_geocode(float(lat), float(lon))
    except ValueError:
        return jsonify({"error": "Invalid lat/lon"}), 400

    if not city:
        return jsonify({"error": "Could not determine city"}), 404

    return jsonify({"city": city})


if __name__ == "__main__":
    app.run(debug=True)