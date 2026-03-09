from flask import Flask, render_template, request
import requests
import os
from datetime import datetime
from taiwan_districts import districts, district_city_map

app = Flask(__name__)

API_KEY = os.environ.get("WEATHER_API_KEY")


@app.route("/", methods=["GET","POST"])
def index():

    weather=None
    today=[]
    week=[]

    lat=request.args.get("lat")
    lon=request.args.get("lon")

    try:

        # GPS定位
        if lat and lon:

            weather_url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=zh_tw"
            forecast_url=f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=zh_tw"

            city_name="目前位置"

        else:

            if request.method=="POST":
                city=request.form.get("city","").strip()
            else:
                city="台北"

            # 如果輸入的是區 / 鄉 / 鎮
            if city in district_city_map:
                city_query=district_city_map[city]
            else:
                city_query=city

            weather_url=f"https://api.openweathermap.org/data/2.5/weather?q={city_query},TW&appid={API_KEY}&units=metric&lang=zh_tw"
            forecast_url=f"https://api.openweathermap.org/data/2.5/forecast?q={city_query},TW&appid={API_KEY}&units=metric&lang=zh_tw"

            city_name=city

        weather_data=requests.get(weather_url).json()
        forecast_data=requests.get(forecast_url).json()

        if str(weather_data.get("cod"))=="200":

            sunrise=datetime.fromtimestamp(weather_data["sys"]["sunrise"]).strftime("%H:%M")
            sunset=datetime.fromtimestamp(weather_data["sys"]["sunset"]).strftime("%H:%M")

            weather={
                "city":city_name,
                "temp":round(weather_data["main"]["temp"]),
                "feels":round(weather_data["main"]["feels_like"]),
                "description":weather_data["weather"][0]["description"],
                "icon":weather_data["weather"][0]["icon"],
                "humidity":weather_data["main"]["humidity"],
                "pressure":weather_data["main"]["pressure"],
                "wind":weather_data["wind"]["speed"],
                "sunrise":sunrise,
                "sunset":sunset
            }

            for item in forecast_data["list"][:8]:

                today.append({
                    "time":item["dt_txt"][11:16],
                    "temp":round(item["main"]["temp"]),
                    "icon":item["weather"][0]["icon"]
                })

            days={}

            for item in forecast_data["list"]:

                date=item["dt_txt"].split(" ")[0]

                if date not in days:

                    days[date]={
                        "temp":round(item["main"]["temp"]),
                        "icon":item["weather"][0]["icon"]
                    }

            for d in list(days.keys())[:7]:

                week.append({
                    "date":datetime.strptime(d,"%Y-%m-%d").strftime("%m/%d"),
                    "temp":days[d]["temp"],
                    "icon":days[d]["icon"]
                })

    except Exception as e:
        print("Weather API error:",e)

    return render_template(
        "index.html",
        weather=weather,
        today=today,
        week=week,
        districts=districts
    )


if __name__=="__main__":

    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)