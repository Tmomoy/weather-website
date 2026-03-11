from flask import Flask, render_template, request
import requests
from taiwan_districts import districts, district_city_map

app = Flask(__name__)

API_KEY = "CWA-163D1E42-4393-42FE-8302-6E96BAB2974A"


@app.route("/")
def home():
    return render_template("index.html", districts=districts)


@app.route("/weather", methods=["POST"])
def weather():

    search = request.form.get("city", "").strip()

    # 區轉城市
    if search in district_city_map:
        city = district_city_map[search]
    else:
        city = search

    city = city.replace("台", "臺")

    if not city.endswith("市") and not city.endswith("縣"):
        if city in ["臺北", "新北", "桃園", "臺中", "臺南", "高雄", "基隆", "新竹", "嘉義"]:
            city += "市"
        else:
            city += "縣"

    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"

    params = {
        "Authorization": API_KEY,
        "locationName": city
    }

    forecast = []
    temps = []
    rains = []
    humidity = []
    times = []

    weather = None

    try:

        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        locations = data.get("records", {}).get("locations", [])

        if not locations:
            raise Exception("No weather data")

        location = locations[0]["location"][0]
        elements = location["weatherElement"]

        temp_data = elements[3]["time"]
        rain_data = elements[7]["time"]
        hum_data = elements[1]["time"]
        wx_data = elements[6]["time"]

        weather = {
            "city": search,
            "wx": wx_data[0]["elementValue"][0]["value"],
            "temp": temp_data[0]["elementValue"][0]["value"],
            "rain": rain_data[0]["elementValue"][0]["value"]
        }

        days = min(7, len(temp_data))

        for i in range(days):

            t = temp_data[i]["startTime"]

            temp = temp_data[i]["elementValue"][0]["value"]
            rain = rain_data[i]["elementValue"][0]["value"]
            hum = hum_data[i]["elementValue"][0]["value"]

            forecast.append({
                "time": t[5:10],
                "temp": temp,
                "rain": rain,
                "hum": hum
            })

            # 避免 "--" crash
            try:
                temps.append(int(temp))
            except:
                temps.append(0)

            try:
                rains.append(int(rain))
            except:
                rains.append(0)

            try:
                humidity.append(int(hum))
            except:
                humidity.append(0)

            times.append(t[5:10])

    except Exception as e:

        print("Weather API error:", e)

        weather = {
            "city": search,
            "wx": "查詢不到資料",
            "temp": "--",
            "rain": "--"
        }

    return render_template(
        "result.html",
        weather=weather,
        forecast=forecast,
        temps=temps,
        rains=rains,
        humidity=humidity,
        times=times,
        districts=districts
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)