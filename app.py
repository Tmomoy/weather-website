from flask import Flask, render_template, request
import requests
import os
from datetime import datetime
from taiwan_districts import districts, district_city_map

app = Flask(__name__)

API_KEY = os.environ.get("WEATHER_API_KEY")

city_map = {

"台北":"Taipei",
"臺北":"Taipei",

"新北":"New Taipei",

"桃園":"Taoyuan",

"台中":"Taichung",
"臺中":"Taichung",

"台南":"Tainan",
"臺南":"Tainan",

"高雄":"Kaohsiung",

"基隆":"Keelung",
"新竹":"Hsinchu",
"嘉義":"Chiayi",

"屏東":"Pingtung",
"宜蘭":"Yilan",
"花蓮":"Hualien",
"台東":"Taitung",

"南投":"Nantou",
"彰化":"Changhua",
"苗栗":"Miaoli",
"雲林":"Yunlin",

"澎湖":"Penghu",
"金門":"Kinmen",
"連江":"Lienchiang"
}

@app.route("/", methods=["GET","POST"])
def index():

    weather=None
    today=[]
    week=[]

    lat=request.args.get("lat")
    lon=request.args.get("lon")

    try:

        if lat and lon:

            weather_url=f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=zh_tw"
            forecast_url=f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=zh_tw"

            city_name="目前位置"

        else:

            if request.method=="POST":
                city=request.form.get("city","").strip()
            else:
                city="台北"

            if city in district_city_map:
                city = district_city_map[city]

            if city in city_map:
                city_query = city_map[city]
            else:
                city_query = city

            weather_url=f"https://api.openweathermap.org/data/2.5/weather?q={city_query},TW&appid={API_KEY}&units=metric&lang=zh_tw"
            forecast_url=f"https://api.openweathermap.org/data/2.5/forecast?q={city_query},TW&appid={API_KEY}&units=metric&lang=zh_tw"

            city_name=city

        weather_data=requests.get(weather_url).json()
        forecast_data=requests.get(forecast_url).json()

        if str(weather_data.get("cod"))=="200":

            weather={
                "city":city_name,
                "temp":round(weather_data["main"]["temp"]),
                "description":weather_data["weather"][0]["description"],
                "icon":weather_data["weather"][0]["icon"],
                "humidity":weather_data["main"]["humidity"]
            }

            # 今日24小時
            for item in forecast_data["list"][:8]:

                today.append({
                    "time":item["dt_txt"][11:16],
                    "temp":round(item["main"]["temp"]),
                    "icon":item["weather"][0]["icon"],
                    "rain":round(item.get("pop",0)*100)
                })

            # 未來7天
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
    app.run(debug=True)