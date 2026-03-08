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

        # 取得輸入城市
        city_input = request.form.get("city", "").strip()

        # 取得下拉選單城市
        city_select = request.form.get("city_select", "").strip()

        # 優先使用輸入
        city = city_input if city_input else city_select

        # 台灣城市對照
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

        # 中文轉英文
        city_en = city_map.get(city, city)

        if not city_en:
            city_en = "Taipei"

        weather_url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city_en}&appid={API_KEY}&units=metric&lang=zh_tw"
        )

        forecast_url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?q={city_en}&appid={API_KEY}&units=metric&lang=zh_tw"
        )

        try:

            weather_data = requests.get(weather_url, timeout=10).json()
            forecast_data = requests.get(forecast_url, timeout=10).json()

            if str(weather_data.get("cod")) == "200":

                weather = {
                    "city": city if city else "台北",
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