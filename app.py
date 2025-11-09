from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env if present

app = Flask(__name__)
 # needed for flash messages

API_KEY = os.environ.get("OPENWEATHER_API_KEY")  # read from environment or .env
if not API_KEY:
    print("Warning: OPENWEATHER_API_KEY not set. Set it in .env or environment variables.")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/weather", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if city == "":
            flash("Please enter a city name.", "warning")
            return redirect(url_for("home"))

        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"  # Celsius
        }

        try:
            r = requests.get(BASE_URL, params=params, timeout=6)
            data = r.json()
        except requests.RequestException:
            flash("Network error. Please try again.", "danger")
            return redirect(url_for("home"))

        if r.status_code != 200:
            # handle errors: city not found, bad request, etc.
            message = data.get("message", "Unable to get weather.")
            flash(f"Error: {message}", "danger")
            return redirect(url_for("home"))

        # parse useful fields
        weather_info = {
            "city": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "temperature": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "humidity": data.get("main", {}).get("humidity"),
            "description": data.get("weather", [{}])[0].get("description", "").title(),
            "icon": data.get("weather", [{}])[0].get("icon")  # icon code to show image
        }

        return render_template("weather.html", weather=weather_info)

    # If GET (user navigates directly), redirect to home
    return redirect(url_for("home"))

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
