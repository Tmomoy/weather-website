from flask import Flask, render_template, request
import requests
import os
import urllib3
from datetime import datetime
from taiwan_districts import districts, district_city_map

urllib3.disable_warnings()

app = Flask(__name__)

CWA_KEY = "CWA-163D1E42-4393-42FE-8302-6E96BAB2974A"


@app.route("/")
def home():
    return render_template("index.html", districts=districts)


@app.route("/weather", methods=["POST"])
def weather():

    today = datetime.now().strftime("%Y-%m-%d")

    search = request.form.get("city", "").strip()

    # 行政區 → 縣市
    if search in district_city_map:
        city = district_city_map[search]
        district = search
    else:
        city = search
        district = None

    city = city.replace("台", "臺")

    if not city.endswith("市") and not city.endswith("縣"):

        if city in ["臺北", "新北", "桃園", "臺中", "臺南", "高雄", "基隆", "新竹", "嘉義"]:
            city += "市"
        else:
            city += "縣"

    # 如果只輸入縣市 → 找一個行政區
    if not district:
        for d, c in district_city_map.items():
            if c == city:
                district = d
                break

    weather = {"city": city, "wx": "--", "temp": "--", "rain": "--"}

    forecast = []
    forecast7 = []
    temps = []
    rains = []
    humidity = []
    times = []

    try:

        # ======================
        # 36小時預報
        # ======================

        url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

        params = {
            "Authorization": CWA_KEY,
            "locationName": city
        }

        r = requests.get(url, params=params, verify=False)
        data = r.json()

        location = data["records"]["location"][0]

        wx = location["weatherElement"][0]["time"]
        rain = location["weatherElement"][1]["time"]
        temp = location["weatherElement"][2]["time"]

        weather = {
            "city": city,
            "wx": wx[0]["parameter"]["parameterName"],
            "temp": temp[0]["parameter"]["parameterName"],
            "rain": rain[0]["parameter"]["parameterName"]
        }

        for i in range(len(temp)):

            start = temp[i]["startTime"]

            date = start[5:10]
            time = start[11:16]

            forecast.append({
                "date": date,
                "time": time,
                "temp": temp[i]["parameter"]["parameterName"],
                "rain": rain[i]["parameter"]["parameterName"]
            })

            temps.append(int(temp[i]["parameter"]["parameterName"]))
            rains.append(int(rain[i]["parameter"]["parameterName"]))
            humidity.append(60)
            times.append(time)

        # ======================
        # 未來7天預報
        # ======================

        url7 = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-091"

        params7 = {
            "Authorization": CWA_KEY,
            "locationName": district
        }

        r7 = requests.get(url7, params=params7, verify=False)
        data7 = r7.json()

        locations = data7.get("records", {}).get("locations", [])

        if locations:

            locs = locations[0].get("location", [])

            for loc in locs:

                if loc["locationName"] == district:

                    elements = loc["weatherElement"]

                    wx_times = []
                    temp_times = []

                    for e in elements:

                        if e["elementName"] == "Wx":
                            wx_times = e["time"]

                        if e["elementName"] == "T":
                            temp_times = e["time"]

                    seen = set()

                    for i in range(len(wx_times)):

                        day = wx_times[i]["startTime"][5:10]

                        if day not in seen:

                            forecast7.append({
                                "day": day,
                                "wx": wx_times[i]["elementValue"][0]["value"],
                                "temp": temp_times[i]["elementValue"][0]["value"]
                            })

                            seen.add(day)

                        if len(forecast7) == 7:
                            break

                    break

    except Exception as e:

        print("Weather API error:", e)

    return render_template(
        "result.html",
        weather=weather,
        forecast=forecast,
        forecast7=forecast7,
        temps=temps,
        rains=rains,
        humidity=humidity,
        times=times,
        today=today
    )


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)