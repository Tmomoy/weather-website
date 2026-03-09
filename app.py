from flask import Flask, render_template, request
import requests
import os
from datetime import datetime
from taiwan_districts import districts

app = Flask(__name__)

API_KEY = os.environ.get("WEATHER_API_KEY")

if not API_KEY:
    print("⚠️ WARNING: WEATHER_API_KEY not set")


@app.route("/", methods=["GET", "POST"])
def index():

    weather = None
    today = []
    week = []

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    try:

        # 📍 GPS定位
        if lat and lon:

            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=zh_tw"

            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=zh_tw"

        else:

            if request.method == "POST":
                city = request.form.get("city", "").strip()
            else:
                city = "台北"

            # 防止空值
            if not city:
                city = "台北"

            weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city},TW&appid={API_KEY}&units=metric&lang=zh_tw"

            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city},TW&appid={API_KEY}&units=metric&lang=zh_tw"

        # API request
        weather_res = requests.get(weather_url, timeout=10)
        forecast_res = requests.get(forecast_url, timeout=10)

        weather_data = weather_res.json()
        forecast_data = forecast_res.json()

        # API成功
        if str(weather_data.get("cod")) == "200":

            sunrise = datetime.fromtimestamp(
                weather_data["sys"]["sunrise"]
            ).strftime("%H:%M")

            sunset = datetime.fromtimestamp(
                weather_data["sys"]["sunset"]
            ).strftime("%H:%M")

            weather = {
                "city": city,  # 使用使用者輸入，避免英文
                "temp": round(weather_data["main"]["temp"]),
                "feels": round(weather_data["main"]["feels_like"]),
                "description": weather_data["weather"][0]["description"],
                "icon": weather_data["weather"][0]["icon"],
                "humidity": weather_data["main"]["humidity"],
                "pressure": weather_data["main"]["pressure"],
                "wind": weather_data["wind"]["speed"],
                "sunrise": sunrise,
                "sunset": sunset
            }

            # 今日24小時
            for item in forecast_data["list"][:8]:

                today.append({
                    "time": item["dt_txt"][11:16],
                    "temp": round(item["main"]["temp"]),
                    "icon": item["weather"][0]["icon"]
                })

            # 未來7天
            days = {}

            for item in forecast_data["list"]:

                date = item["dt_txt"].split(" ")[0]

                if date not in days:

                    days[date] = {
                        "temp": round(item["main"]["temp"]),
                        "icon": item["weather"][0]["icon"]
                    }

            for d in list(days.keys())[:7]:

                week.append({
                    "date": datetime.strptime(
                        d, "%Y-%m-%d"
                    ).strftime("%m/%d"),
                    "temp": days[d]["temp"],
                    "icon": days[d]["icon"]
                })

        else:
            print("API Error:", weather_data)

    except Exception as e:
        print("Weather API error:", e)

    return render_template(
        "index.html",
        weather=weather,
        today=today,
        week=week,
        districts=districts
    )


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)