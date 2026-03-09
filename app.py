from flask import Flask, render_template, request
import requests
from taiwan_districts import districts, district_city_map

app = Flask(__name__)

API_KEY = "CWA-163D1E42-4393-42FE-8302-6E96BAB2974A"


@app.route("/", methods=["GET", "POST"])
def index():

    weather = None
    forecast = []
    temps = []
    times = []

    search = "臺北市"

    if request.method == "POST":
        search = request.form.get("city", "").strip()

    if not search:
        search = "臺北市"

    # 行政區轉縣市
    if search in district_city_map:
        city = district_city_map[search]
    else:
        city = search

    # 自動修正縣市名稱
    city = city.replace("台", "臺")

    if not city.endswith("市") and not city.endswith("縣"):
        if city in ["臺北","新北","桃園","臺中","臺南","高雄","基隆","新竹","嘉義"]:
            city += "市"
        else:
            city += "縣"

    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

    params = {
        "Authorization": API_KEY,
        "locationName": city
    }

    try:

        r = requests.get(url, params=params, timeout=10)

        if r.status_code != 200:
            raise Exception("API request failed")

        data = r.json()

        locations = data.get("records", {}).get("location", [])

        if not locations:
            raise Exception("No location data")

        location = locations[0]

        weather = {
            "city": search,
            "wx": location["weatherElement"][0]["time"][0]["parameter"]["parameterName"],
            "temp": location["weatherElement"][2]["time"][0]["parameter"]["parameterName"],
            "rain": location["weatherElement"][1]["time"][0]["parameter"]["parameterName"]
        }

        for i, t in enumerate(location["weatherElement"][0]["time"]):

            temp = location["weatherElement"][2]["time"][i]["parameter"]["parameterName"]
            rain = location["weatherElement"][1]["time"][i]["parameter"]["parameterName"]

            forecast.append({
                "time": t["startTime"][5:16],
                "wx": t["parameter"]["parameterName"],
                "temp": temp,
                "rain": rain
            })

            temps.append(int(temp))
            times.append(t["startTime"][11:16])

    except Exception as e:

        print("Weather API error:", e)

        weather = {
            "city": search,
            "wx": "查詢不到資料",
            "temp": "--",
            "rain": "--"
        }

    return render_template(
        "index.html",
        weather=weather,
        forecast=forecast,
        temps=temps,
        times=times,
        districts=districts
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)