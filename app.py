from flask import Flask, render_template, request
import requests
from taiwan_districts import districts, district_city_map

app = Flask(__name__)

API_KEY="CWA-163D1E42-4393-42FE-8302-6E96BAB2974A"


@app.route("/")
def home():
    return render_template("index.html", districts=districts)


@app.route("/weather", methods=["POST"])
def weather():

    search=request.form.get("city","").strip()

    if search in district_city_map:
        city=district_city_map[search]
    else:
        city=search

    city=city.replace("台","臺")

    # 城市格式修正
    city_map={
    "臺北":"臺北市",
    "新北":"新北市",
    "桃園":"桃園市",
    "臺中":"臺中市",
    "臺南":"臺南市",
    "高雄":"高雄市",
    "基隆":"基隆市",
    "新竹":"新竹市",
    "嘉義":"嘉義市"
    }

    if city in city_map:
        city=city_map[city]

    elif not city.endswith("市") and not city.endswith("縣"):
        city+="市"

    url="https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

    params={
        "Authorization":API_KEY,
        "locationName":city
    }

    forecast=[]
    temps=[]
    rains=[]
    humidity=[]
    times=[]

    weather={
        "city":city,
        "wx":"查詢不到資料",
        "temp":"--",
        "rain":"--"
    }

    try:

        r=requests.get(url,params=params)
        data=r.json()

        locations=data.get("records",{}).get("location",[])

        if not locations:
            raise Exception("No weather data")

        location=locations[0]

        wx_data=location["weatherElement"][0]["time"]
        rain_data=location["weatherElement"][1]["time"]
        temp_data=location["weatherElement"][2]["time"]

        weather={
            "city":city,
            "wx":wx_data[0]["parameter"]["parameterName"],
            "temp":temp_data[0]["parameter"]["parameterName"],
            "rain":rain_data[0]["parameter"]["parameterName"]
        }

        for i in range(len(temp_data)):

            t=temp_data[i]["startTime"]

            temp=temp_data[i]["parameter"]["parameterName"]
            rain=rain_data[i]["parameter"]["parameterName"]
            wx=wx_data[i]["parameter"]["parameterName"]

            forecast.append({
                "time":t[5:16],
                "temp":temp,
                "rain":rain,
                "wx":wx
            })

            temps.append(int(temp))
            rains.append(int(rain))
            humidity.append(60)
            times.append(t[11:16])

    except Exception as e:
        print("Weather API error:",e)

    return render_template(
        "result.html",
        weather=weather,
        forecast=forecast,
        temps=temps,
        rains=rains,
        humidity=humidity,
        times=times
    )


if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)