from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

API_KEY = os.environ.get("WEATHER_API_KEY")

if not API_KEY:
    print("⚠️ WARNING: WEATHER_API_KEY not set")

# 英文轉中文城市
city_translate = {
    "Taipei": "台北",
    "New Taipei": "新北",
    "Taoyuan": "桃園",
    "Taichung": "台中",
    "Tainan": "台南",
    "Kaohsiung": "高雄",
    "Keelung": "基隆",
    "Hsinchu": "新竹",
    "Chiayi": "嘉義",
    "Pingtung": "屏東",
    "Yilan": "宜蘭",
    "Hualien": "花蓮",
    "Taitung": "台東",
    "Nantou": "南投",
    "Changhua": "彰化",
    "Miaoli": "苗栗",
    "Yunlin": "雲林",
    "Penghu": "澎湖",
    "Kinmen": "金門",
    "Lienchiang": "連江"
}

# 中文轉英文
city_map = {
    "台北": "Taipei",
    "臺北": "Taipei",
    "新北": "New Taipei",
    "桃園": "Taoyuan",
    "台中": "Taichung",
    "臺中": "Taichung",
    "台南": "Tainan",
    "高雄": "Kaohsiung",
    "基隆": "Keelung",
    "新竹": "Hsinchu",
    "嘉義": "Chiayi",
    "屏東": "Pingtung",
    "宜蘭": "Yilan",
    "花蓮": "Hualien",
    "台東": "Taitung",
    "南投": "Nantou",
    "彰化": "Changhua",
    "苗栗": "Miaoli",
    "雲林": "Yunlin",
    "澎湖": "Penghu",
    "金門": "Kinmen",
    "連江": "Lienchiang"
}


@app.route("/", methods=["GET", "POST"])
def index():

    weather = None
    forecast = None

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    try:

        # 📍 GPS定位
        if lat and lon:

            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=zh_tw"
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=zh_tw"

        else:

            if request.method == "POST":

                city_input = request.form.get("city", "").strip()
                city_select = request.form.get("city_select", "").strip()

                city = city_input if city_input else city_select

            else:
                city = "台北"

            city_en = city_map.get(city, city)

            weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={API_KEY}&units=metric&lang=zh_tw"
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_en}&appid={API_KEY}&units=metric&lang=zh_tw"

        weather_data = requests.get(weather_url, timeout=10).json()
        forecast_data = requests.get(forecast_url, timeout=10).json()

        if str(weather_data.get("cod")) == "200":

            city_en = weather_data["name"]
            city_zh = city_translate.get(city_en, city_en)

            weather = {
                "city": city_zh,
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