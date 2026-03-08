from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = "16db3df928d1045f51b23199a877d325"

@app.route("/", methods=["GET","POST"])
def index():

    weather = None
    forecast = None

    if request.method == "POST":

        city = request.form["city"]

        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=zh_tw"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=zh_tw"

        weather_data = requests.get(weather_url).json()
        forecast_data = requests.get(forecast_url).json()

        if weather_data["cod"] == 200:

            weather = {
                "city": city,
                "temp": weather_data["main"]["temp"],
                "description": weather_data["weather"][0]["description"],
                "icon": weather_data["weather"][0]["icon"],
                "humidity": weather_data["main"]["humidity"]
            }

            forecast = []

            for item in forecast_data["list"][:7]:
                forecast.append({
                    "temp": item["main"]["temp"],
                    "icon": item["weather"][0]["icon"],
                    "time": item["dt_txt"]
                })

    return render_template("index.html", weather=weather, forecast=forecast)

if __name__ == "__main__":
    app.run(debug=True)