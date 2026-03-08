from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("WEATHER_API_KEY")

if not API_KEY:
    print("⚠️ WARNING: WEATHER_API_KEY not set")


@app.route("/", methods=["GET", "POST"])
def index():

    weather = None
    forecast = None

    if request.method == "POST":

        city = request.form.get("city")

        if not city:
            city = "Taipei"

        weather_url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={API_KEY}&units=metric&lang=zh_tw"
        )

        forecast_url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?q={city}&appid={API_KEY}&units=metric&lang=zh_tw"
        )

        try:

            weather_data = requests.get(weather_url, timeout=10).json()
            forecast_data = requests.get(forecast_url, timeout=10).json()

            if str(weather_data.get("cod")) == "200":

                weather = {
                    "city": city,
                    "temp": weather_data["main"]["temp"],
                    "description": weather_data["weather"][0]["description"],
                    "icon": weather_data["weather"][0]["icon"],
                    "humidity": weather_data["main"]["humidity"],
                }

                forecast = []

                for item in forecast_data.get("list", [])[:7]:

                    forecast.append({
                        "temp": item["main"]["temp"],
                        "icon": item["weather"][0]["icon"],
                        "time": item["dt_txt"]
                    })

        except Exception as e:
            print("Weather API error:", e)

    return render_template("index.html", weather=weather, forecast=forecast)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)