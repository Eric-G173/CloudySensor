# About the Project

CloudySensor was built to explore API integration, backend routing, and cloud deployment using modern Python web tools. The app provides real-time weather metrics for any city in the world, including remote regions, by combining accurate geolocation data with precise meteorological information.

The system works by converting a user’s city input (e.g., Phoenix, San Francisco) into latitude and longitude coordinates using the OpenStreetMap geocoding API. Those coordinates are then passed to the Open‑Meteo API, which returns detailed weather data for that exact location. The processed results are delivered to the frontend in clean JSON format and displayed through a responsive UI.

# Motivation

CloudySensor represents my first fully built and deployed software project. As a sophomore/junior in college, I wanted to push myself beyond standard coursework and build something that required real API integration, backend logic, and cloud deployment. Weather data felt like the ideal starting point: simple to begin with yet flexible enough to expand into more complex challenges.

Building CloudySensor taught me how to structure a Flask application, work with external APIs, handle geolocation data, and deploy a production-ready service. More importantly, it marked the point where I transitioned from learning concepts in class to applying them in a real, functioning application. This project is the foundation of my development journey and a milestone in becoming a more capable and confident engineer.

# Installation
All other systems come pre-installed, the following has to be done manually:
| Tool | Purpose | Why this choice | How to Install |
|-------|-----|------------------|------------------|
| Python | Backend Language | Python is lightweight, easy to read, and perfect for building small API-driven applications. As my first full project, Python allowed me to focus on learning backend fundamentals without unnecessary complexity | Install Python from python.org
| Flask | Web Framework | Flask is minimal and flexible, making it ideal for learning backend architecture. It gave me full control over routing, API calls, and JSON responses without the overhead of larger frameworks | After cloning the repo, run: pip install -r requirements.txt
| Gunicorn | Production WSGI server |Required for deploying Flask apps on Render. Provides stable performance and proper handling of concurrent requests |  run: pip install -r requirements.txt. **You do not have to run this command again if you already did pip install -r requirements.txt**

## Live Deployment
https://weather-website-fjzu.onrender.com/ 

## Features
- Accurate weather data
- Able to locate any city in the world
- Fast temperature conversions
- Continuous Deployment to Render via Deploy Hook
- Continuous Integration via GitHub Actions to test new changes

## Tech Stack
- Python
- Flask
- JavaScript
- HTML
- CSS
- Gunicorn (Production Server)
- Render (Deployment)

Special thank you to open-meteo for providing their free API. Link for them: https://open-meteo.com/

